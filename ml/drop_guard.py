"""
Fraud Detection
=============
Two-part machine learning module for the Student Job & Internship Matching
System:

1. Disengagement risk classifier (supervised)
   - Algorithm: RandomForestClassifier (scikit-learn)
   - Predicts the probability that a student will disengage from the
     job-seeking process before securing an opportunity.

2. Suspicious listing detector (unsupervised anomaly detection)
   - Algorithm: IsolationForest (scikit-learn)
   - Flags company listings whose feature profile looks anomalous compared
     to the bulk of legitimate listings (e.g. implausible stipend, brand
     new unverified company, near-empty description, posting bursts).

Explainability: SHAP (TreeExplainer) is used to surface, per prediction,
which features pushed the score up (or down) — giving career-office staff
and administrators a transparent reason for every risk score / flag rather
than a black-box number.
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import RandomForestClassifier, IsolationForest

from ml.data_simulation import (
    simulate_student_engagement,
    simulate_listing_history,
    STUDENT_FEATURES,
    LISTING_FEATURES,
)

RISK_MODEL_FILE = "risk_classifier.joblib"
ANOMALY_MODEL_FILE = "anomaly_detector.joblib"


def _model_path(model_dir, filename):
    return os.path.join(model_dir, filename)


def train_and_save_models(model_dir):
    os.makedirs(model_dir, exist_ok=True)

    # --- 1. Disengagement risk classifier ---
    student_df = simulate_student_engagement()
    X = student_df[STUDENT_FEATURES]
    y = student_df["disengaged"]

    risk_clf = RandomForestClassifier(
        n_estimators=200, max_depth=6, random_state=42, class_weight="balanced"
    )
    risk_clf.fit(X, y)
    joblib.dump(risk_clf, _model_path(model_dir, RISK_MODEL_FILE))

    # --- 2. Suspicious listing anomaly detector ---
    listing_df = simulate_listing_history()
    Xl = listing_df[LISTING_FEATURES]

    anomaly_clf = IsolationForest(
        n_estimators=200, contamination=0.08, random_state=42
    )
    anomaly_clf.fit(Xl)
    joblib.dump(anomaly_clf, _model_path(model_dir, ANOMALY_MODEL_FILE))

    return risk_clf, anomaly_clf


def load_models(model_dir):
    risk_path = _model_path(model_dir, RISK_MODEL_FILE)
    anomaly_path = _model_path(model_dir, ANOMALY_MODEL_FILE)

    if not (os.path.exists(risk_path) and os.path.exists(anomaly_path)):
        return train_and_save_models(model_dir)

    risk_clf = joblib.load(risk_path)
    anomaly_clf = joblib.load(anomaly_path)
    return risk_clf, anomaly_clf


class DropGuardEngine:
    """Wraps both models plus SHAP explainers behind a simple API."""

    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.risk_clf, self.anomaly_clf = load_models(model_dir)

        # SHAP's exact API/output shape shifts across versions and model
        # types, so explainer construction is best-effort: if it fails for
        # any reason, _explain() below falls back to a simple, still
        # explainable "distance from typical value" heuristic rather than
        # breaking risk scoring / fraud screening.
        try:
            self._risk_explainer = shap.TreeExplainer(self.risk_clf)
        except Exception:
            self._risk_explainer = None
        try:
            self._anomaly_explainer = shap.TreeExplainer(self.anomaly_clf)
        except Exception:
            self._anomaly_explainer = None

        # Reference stats (from the training data distribution) used only by
        # the fallback explanation path.
        self._student_ref = simulate_student_engagement()[STUDENT_FEATURES]
        self._listing_ref = simulate_listing_history()[LISTING_FEATURES]

    # ---------------- Student disengagement risk ----------------
    def assess_student(self, student_profile):
        row = pd.DataFrame(
            [{f: getattr(student_profile, f) or 0 for f in STUDENT_FEATURES}]
        )
        proba = self.risk_clf.predict_proba(row)[0][1]  # P(disengaged)

        if proba >= 0.66:
            label = "high"
        elif proba >= 0.35:
            label = "medium"
        else:
            label = "low"

        top_factors = self._explain(
            self._risk_explainer, self.risk_clf, row, STUDENT_FEATURES,
            self._student_ref, mode="classifier",
        )
        return {
            "risk_label": label,
            "risk_probability": round(float(proba), 3),
            "top_factors": top_factors,
        }

    # ---------------- Listing anomaly / fraud screening ----------------
    def assess_listing(self, feature_dict):
        row = pd.DataFrame([{f: feature_dict.get(f, 0) for f in LISTING_FEATURES}])

        # decision_function: higher = more normal, lower/negative = more anomalous.
        raw_score = self.anomaly_clf.decision_function(row)[0]
        is_outlier = self.anomaly_clf.predict(row)[0] == -1

        # Convert to an intuitive 0-100 "suspicion score" (higher = riskier)
        suspicion_score = float(np.clip((0.5 - raw_score) * 100, 0, 100))

        top_factors = self._explain(
            self._anomaly_explainer, self.anomaly_clf, row, LISTING_FEATURES,
            self._listing_ref, mode="anomaly",
        )
        return {
            "is_flagged": bool(is_outlier),
            "anomaly_score": round(suspicion_score, 1),
            "top_factors": top_factors,
        }

    # ---------------- Explanation (SHAP, with a safe fallback) ----------------
    def _explain(self, explainer, model, row, feature_names, reference_df, mode, top_n=3):
        """Returns a JSON string of the top_n features driving this
        prediction, e.g. [{"feature": ..., "impact": ..., "direction": ...}].

        Tries SHAP's TreeExplainer first. SHAP's return shape differs across
        versions/model types (a list of per-class arrays, a 3D array, or a
        plain 2D array), so several shapes are handled. If SHAP is
        unavailable or its output can't be interpreted, falls back to a
        transparent heuristic: how many standard deviations each feature
        sits from the "typical" (mean) value seen during training, signed so
        that a positive value always means "pushes toward risk/suspicion".
        """
        if explainer is not None:
            try:
                values = self._shap_row_values(explainer, row, mode)
                if values is not None:
                    return self._top_factors_json(feature_names, values, top_n)
            except Exception:
                pass  # fall through to the heuristic below

        return self._fallback_explain(row, feature_names, reference_df, mode, top_n)

    @staticmethod
    def _shap_row_values(explainer, row, mode):
        raw = explainer.shap_values(row)

        if isinstance(raw, list):
            # Binary classifier: [shap_for_class_0, shap_for_class_1]
            arr = np.array(raw[-1])[0]
        else:
            arr = np.array(raw)
            if arr.ndim == 3:
                # (n_samples, n_features, n_classes) — take the positive class
                arr = arr[0, :, -1]
            elif arr.ndim == 2:
                arr = arr[0]
            else:
                arr = arr

        if mode == "anomaly":
            # IsolationForest: lower decision_function = more anomalous, so
            # flip sign such that positive SHAP always means "more suspicious".
            arr = -arr

        return arr

    @staticmethod
    def _top_factors_json(feature_names, values, top_n):
        pairs = list(zip(feature_names, values))
        pairs.sort(key=lambda p: abs(p[1]), reverse=True)
        top = pairs[:top_n]
        factors = [
            {
                "feature": _readable(name),
                "impact": round(float(val), 4),
                "direction": "increases" if val > 0 else "decreases",
            }
            for name, val in top
        ]
        return json.dumps(factors)

    @staticmethod
    def _fallback_explain(row, feature_names, reference_df, mode, top_n):
        """Signed z-score of each feature vs. the training distribution,
        oriented so that positive = pushes toward risk/suspicion. This is a
        simpler stand-in for SHAP but still gives an honest, per-feature
        reason rather than an opaque score."""
        means = reference_df.mean()
        stds = reference_df.std().replace(0, 1)

        # Features where a HIGHER raw value means LOWER risk/suspicion
        # (e.g. more logins is reassuring, not risky) get their z-score sign
        # flipped so "positive impact" consistently means "more risk".
        inverse_features = {
            "profile_completeness",
            "logins_last_30_days",
            "applications_last_30_days",
            "saved_searches",
            "profile_views_received",
            "company_age_years",
            "company_verified",
            "required_skills_count",
        }

        values = []
        for f in feature_names:
            raw_val = float(row.iloc[0][f])
            z = (raw_val - means[f]) / stds[f]
            if f in inverse_features:
                z = -z
            values.append(z)

        return DropGuardEngine._top_factors_json(feature_names, np.array(values), top_n)


_FEATURE_LABELS = {
    "profile_completeness": "Profile completeness",
    "logins_last_30_days": "Logins in last 30 days",
    "applications_last_30_days": "Applications in last 30 days",
    "days_since_last_login": "Days since last login",
    "days_since_last_application": "Days since last application",
    "saved_searches": "Saved searches",
    "profile_views_received": "Profile views received",
    "salary_stipend": "Stipend/salary offered",
    "duration_months": "Opportunity duration",
    "description_length": "Description length",
    "required_skills_count": "Number of required skills listed",
    "company_age_years": "Company age",
    "listings_posted_last_7_days": "Listings posted in last 7 days",
    "company_verified": "Company verification status",
}


def _readable(name):
    return _FEATURE_LABELS.get(name, name.replace("_", " ").capitalize())


_ENGINE_CACHE = {}


def get_engine(model_dir):
    """Returns a cached DropGuardEngine so models/explainers are built once
    per process rather than on every request."""
    if model_dir not in _ENGINE_CACHE:
        _ENGINE_CACHE[model_dir] = DropGuardEngine(model_dir)
    return _ENGINE_CACHE[model_dir]

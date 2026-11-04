"""
Generates simulated historical data used to TRAIN the fraud detection models.

In a production deployment these training sets would be built from real
historical platform logs (student engagement over time, and past
confirmed-fraudulent listings). For this academic prototype, representative
synthetic data is generated with clear, explainable relationships between
features and outcomes, so the trained models behave sensibly on the app's
live (also simulated) data.
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

STUDENT_FEATURES = [
    "profile_completeness",
    "logins_last_30_days",
    "applications_last_30_days",
    "days_since_last_login",
    "days_since_last_application",
    "saved_searches",
    "profile_views_received",
]

LISTING_FEATURES = [
    "salary_stipend",
    "duration_months",
    "description_length",
    "required_skills_count",
    "company_age_years",
    "listings_posted_last_7_days",
    "company_verified",
]


def simulate_student_engagement(n=1200):
    """Simulate student engagement history and a disengagement label.

    A student is labelled 'disengaged' (1) if they show the classic
    withdrawal pattern: low profile completeness, few logins, no recent
    applications and a long idle period.
    """
    profile_completeness = np.clip(RNG.normal(65, 22, n), 5, 100)
    logins_last_30_days = np.clip(RNG.poisson(6, n) - (100 - profile_completeness) / 25, 0, None)
    applications_last_30_days = np.clip(
        RNG.poisson(2, n) + (profile_completeness - 50) / 40, 0, None
    ).round()
    days_since_last_login = np.clip(RNG.exponential(8, n) + (100 - profile_completeness) / 6, 0, 90).round()
    days_since_last_application = np.clip(
        RNG.exponential(12, n) + (100 - profile_completeness) / 4, 0, 120
    ).round()
    saved_searches = RNG.poisson(1.5, n)
    profile_views_received = np.clip(RNG.poisson(3, n) + profile_completeness / 20, 0, None).round()

    df = pd.DataFrame(
        {
            "profile_completeness": profile_completeness,
            "logins_last_30_days": logins_last_30_days,
            "applications_last_30_days": applications_last_30_days,
            "days_since_last_login": days_since_last_login,
            "days_since_last_application": days_since_last_application,
            "saved_searches": saved_searches,
            "profile_views_received": profile_views_received,
        }
    )

    # Rule-based ground truth with noise, mirroring how disengagement is
    # actually recognised operationally (idle + inactive + thin profile).
    risk_score = (
        0.35 * (df["days_since_last_login"] / 90)
        + 0.30 * (df["days_since_last_application"] / 120)
        + 0.20 * (1 - df["profile_completeness"] / 100)
        + 0.10 * (1 / (1 + df["logins_last_30_days"]))
        + 0.05 * (1 / (1 + df["applications_last_30_days"]))
    )
    risk_score += RNG.normal(0, 0.05, n)
    label = (risk_score > np.quantile(risk_score, 0.7)).astype(int)

    df["disengaged"] = label
    return df


def simulate_listing_history(n=1000):
    """Simulate posted listings and a fraudulent/suspicious label.

    Suspicious listings tend to: offer implausibly high stipends, have very
    short/generic descriptions, list very broad or no real required skills,
    come from very new/unverified companies, or be posted in unusual bursts.
    """
    company_age_years = np.clip(RNG.exponential(3, n), 0.05, 25)
    company_verified = (RNG.random(n) < np.clip(company_age_years / 6, 0.05, 0.95)).astype(int)
    listings_posted_last_7_days = np.clip(RNG.poisson(1.2, n), 0, None)

    salary_stipend = np.clip(RNG.normal(6000, 2500, n), 0, None)
    duration_months = RNG.integers(1, 13, n)
    description_length = np.clip(RNG.normal(450, 200, n), 20, None).round()
    required_skills_count = RNG.integers(0, 8, n)

    df = pd.DataFrame(
        {
            "salary_stipend": salary_stipend,
            "duration_months": duration_months,
            "description_length": description_length,
            "required_skills_count": required_skills_count,
            "company_age_years": company_age_years,
            "listings_posted_last_7_days": listings_posted_last_7_days,
            "company_verified": company_verified,
        }
    )

    # Inject a fraud-like subpopulation
    n_fraud = int(n * 0.08)
    fraud_idx = RNG.choice(n, n_fraud, replace=False)
    df.loc[fraud_idx, "salary_stipend"] = RNG.uniform(25000, 60000, n_fraud)
    df.loc[fraud_idx, "description_length"] = RNG.uniform(20, 120, n_fraud)
    df.loc[fraud_idx, "required_skills_count"] = 0
    df.loc[fraud_idx, "company_age_years"] = RNG.uniform(0.01, 0.3, n_fraud)
    df.loc[fraud_idx, "company_verified"] = 0
    df.loc[fraud_idx, "listings_posted_last_7_days"] = RNG.integers(5, 15, n_fraud)

    label = np.zeros(n, dtype=int)
    label[fraud_idx] = 1
    df["fraudulent"] = label
    return df

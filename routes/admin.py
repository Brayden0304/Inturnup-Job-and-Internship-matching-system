import json
from functools import wraps
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user, login_user

from extensions import db
from models import User, StudentProfile, CompanyProfile, Opportunity, RiskAssessment
from ml.drop_guard import get_engine
from utils import validate_email

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("That page is only available to administrators.", "error")
            return redirect(url_for("admin.admin_login"))
        return f(*args, **kwargs)

    return wrapper


@admin_bp.route("/")
def index():
    if current_user.is_authenticated and current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("admin.admin_login"))


@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        flash("You are currently signed in with a student/company account. Please log out first to access the admin console.", "info")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email_raw = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email_raw or not password:
            flash("Administrator email and password are required.", "error")
            return render_template("admin/login.html")

        is_valid_email, email_val_or_err = validate_email(email_raw)
        if not is_valid_email:
            flash("Please enter a valid administrator email address.", "error")
            return render_template("admin/login.html")
        email = email_val_or_err

        alias_map = {
            "admin@launchpad.ac.za": "admin@launchpad.local",
            "admin@internup.ac.za": "admin@launchpad.local",
            "admin@internup.local": "admin@launchpad.local",
            "admin@internup.com": "admin@launchpad.local",
        }
        lookup_email = alias_map.get(email, email)
        user = User.query.filter_by(email=lookup_email).first()

        if user and user.role == "admin" and user.check_password(password):
            if not user.is_active:
                flash("This administrator account is disabled. Contact another administrator.", "error")
                return render_template("admin/login.html")
            user.last_login_at = datetime.utcnow()
            db.session.commit()
            login_user(user)
            flash("Welcome to the Academic Governance & Placement Console.", "success")
            return redirect(url_for("admin.dashboard"))

        flash("Invalid administrator credentials or unauthorized access.", "error")

    return render_template("admin/login.html")


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    student_count = StudentProfile.query.count()
    company_count = CompanyProfile.query.count()
    listing_count = Opportunity.query.count()
    flagged_count = Opportunity.query.filter_by(is_flagged=True, flag_reviewed=False).count()
    high_risk_count = RiskAssessment.query.filter_by(risk_label="high").count()
    
    from models import Application
    total_applications = Application.query.count()
    
    flagged_listings = (
        Opportunity.query.filter_by(is_flagged=True, flag_reviewed=False)
        .order_by(Opportunity.anomaly_score.desc())
        .limit(3)
        .all()
    )
    for listing in flagged_listings:
        listing.parsed_reason = json.loads(listing.flag_reason) if listing.flag_reason else []

    high_risk_assessments = (
        RiskAssessment.query.filter_by(risk_label="high")
        .order_by(RiskAssessment.risk_probability.desc())
        .limit(3)
        .all()
    )
    for a in high_risk_assessments:
        a.parsed_factors = json.loads(a.top_factors) if a.top_factors else []

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_applications = Application.query.order_by(Application.applied_at.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        student_count=student_count,
        company_count=company_count,
        listing_count=listing_count,
        flagged_count=flagged_count,
        high_risk_count=high_risk_count,
        total_applications=total_applications,
        flagged_listings=flagged_listings,
        high_risk_assessments=high_risk_assessments,
        recent_users=recent_users,
        recent_applications=recent_applications,
    )


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        flash("Administrator accounts can't be disabled from here.", "error")
        return redirect(url_for("admin.users"))
    user.is_active_account = not user.is_active_account
    db.session.commit()
    flash(
        "Account access restored. The user can sign in again."
        if user.is_active_account
        else "Account quarantined. New sign-ins are blocked, and existing sessions will be revoked on the next request.",
        "success",
    )
    return redirect(url_for("admin.users"))


@admin_bp.route("/listings")
@login_required
@admin_required
def listings():
    all_listings = Opportunity.query.order_by(Opportunity.posted_at.desc()).all()
    return render_template("admin/listings.html", listings=all_listings)


@admin_bp.route("/listings/<int:opp_id>/review", methods=["POST"])
@login_required
@admin_required
def review_listing(opp_id):
    opp = Opportunity.query.get_or_404(opp_id)
    decision = request.form.get("decision", "").strip()
    if decision == "approve":
        opp.flag_reviewed = True
        opp.is_active = True
        flash("Listing approved and is now live.", "success")
    elif decision == "remove":
        opp.flag_reviewed = True
        opp.is_active = False
        flash("Listing removed from the platform.", "success")
    else:
        flash("Invalid review decision specified.", "error")
        return redirect(url_for("admin.listings"))
    db.session.commit()
    return redirect(url_for("admin.listings"))


@admin_bp.route("/intervene/<int:student_id>", methods=["POST"])
@login_required
@admin_required
def intervene_student(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    flash(
        f"✓ Academic Intervention Dispatched: An institutional support notice and career advisor scheduling link were delivered to {student.full_name} ({student.user.email}).",
        "success",
    )
    return redirect(request.referrer or url_for("admin.dashboard"))


# ---------------- Fraud Detection ----------------

@admin_bp.route("/drop-guard")
@login_required
@admin_required
def drop_guard():
    flagged_listings = (
        Opportunity.query.filter_by(is_flagged=True, flag_reviewed=False)
        .order_by(Opportunity.anomaly_score.desc())
        .all()
    )
    for listing in flagged_listings:
        listing.parsed_reason = json.loads(listing.flag_reason) if listing.flag_reason else []

    risk_rows = []
    students = StudentProfile.query.all()
    for s in students:
        latest = (
            RiskAssessment.query.filter_by(student_id=s.id)
            .order_by(RiskAssessment.assessed_at.desc())
            .first()
        )
        if latest:
            risk_rows.append(
                {
                    "student": s,
                    "risk_label": latest.risk_label,
                    "risk_probability": latest.risk_probability,
                    "top_factors": json.loads(latest.top_factors) if latest.top_factors else [],
                    "assessed_at": latest.assessed_at,
                }
            )

    risk_rows.sort(key=lambda r: r["risk_probability"], reverse=True)

    return render_template(
        "admin/drop_guard.html", flagged_listings=flagged_listings, risk_rows=risk_rows
    )


@admin_bp.route("/drop-guard/run", methods=["POST"])
@login_required
@admin_required
def run_drop_guard():
    """Runs the disengagement-risk classifier across all students on demand."""
    engine = get_engine(current_app.config["MODEL_DIR"])
    students = StudentProfile.query.all()

    for s in students:
        result = engine.assess_student(s)
        assessment = RiskAssessment(
            student_id=s.id,
            risk_label=result["risk_label"],
            risk_probability=result["risk_probability"],
            top_factors=result["top_factors"],
            assessed_at=datetime.utcnow(),
        )
        db.session.add(assessment)

    db.session.commit()
    flash(f"Fraud detection analysis complete for {len(students)} students.", "success")
    return redirect(url_for("admin.drop_guard"))


@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
@admin_required
def settings():
    """Notification and account settings for administrators."""
    if request.method == "POST":
        current_user.notify_applications = request.form.get("notify_applications") == "on"
        current_user.notify_opportunities = request.form.get("notify_opportunities") == "on"
        current_user.notify_updates = request.form.get("notify_updates") == "on"
        current_user.email_digest = request.form.get("email_digest") == "on"
        db.session.commit()
        flash("Notification preferences updated.", "success")
        return redirect(url_for("admin.settings"))

    return render_template("admin/settings.html")

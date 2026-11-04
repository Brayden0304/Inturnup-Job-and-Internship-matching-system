from datetime import datetime, date
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from extensions import db
from models import Opportunity, Application, StudentProfile, Notification
from ml.drop_guard import get_engine
from utils import (
    format_title_case,
    validate_company_name,
    validate_url,
    validate_number,
    validate_closing_date,
    clean_comma_separated,
    sanitize_text,
)

company_bp = Blueprint("company", __name__, url_prefix="/company")


def company_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "company":
            flash("That page is only available to company accounts.", "error")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    return wrapper


@company_bp.route("/dashboard")
@login_required
@company_required
def dashboard():
    profile = current_user.company_profile
    listings = Opportunity.query.filter_by(company_id=profile.id).order_by(
        Opportunity.posted_at.desc()
    ).all()
    total_applications = sum(len(o.applications) for o in listings)
    flagged_count = sum(1 for o in listings if o.is_flagged)
    return render_template(
        "company/dashboard.html",
        profile=profile,
        listings=listings,
        total_applications=total_applications,
        flagged_count=flagged_count,
    )


@company_bp.route("/profile", methods=["GET", "POST"])
@login_required
@company_required
def profile():
    profile = current_user.company_profile
    if request.method == "POST":
        company_name_raw = request.form.get("company_name", profile.company_name)
        is_valid_name, name_val_or_err = validate_company_name(company_name_raw)
        if not is_valid_name:
            flash(name_val_or_err, "error")
            return redirect(url_for("company.profile"))
        profile.company_name = name_val_or_err

        # Website URL validation
        website_raw = request.form.get("website", "")
        is_valid_web, web_val_or_err = validate_url(website_raw, optional=True)
        if not is_valid_web:
            flash(web_val_or_err, "error")
            return redirect(url_for("company.profile"))
        profile.website = web_val_or_err

        # Company age validation
        age_raw = request.form.get("company_age_years")
        is_valid_age, age_num, age_err = validate_number(
            age_raw, field_name="Years in operation", min_val=0.0, max_val=200.0, default=1.0
        )
        if not is_valid_age:
            flash(age_err, "error")
            return redirect(url_for("company.profile"))
        profile.company_age_years = age_num

        profile.industry = format_title_case(sanitize_text(request.form.get("industry", ""), max_length=120))
        profile.location = format_title_case(sanitize_text(request.form.get("location", ""), max_length=120))
        profile.description = sanitize_text(request.form.get("description", ""), max_length=3000)

        db.session.commit()
        flash("Company profile updated.", "success")
        return redirect(url_for("company.profile"))
    return render_template("company/profile.html", profile=profile)


@company_bp.route("/settings", methods=["GET", "POST"])
@login_required
@company_required
def settings():
    """Notification and account settings for companies."""
    if request.method == "POST":
        current_user.notify_applications = request.form.get("notify_applications") == "on"
        current_user.notify_opportunities = request.form.get("notify_opportunities") == "on"
        current_user.notify_updates = request.form.get("notify_updates") == "on"
        current_user.email_digest = request.form.get("email_digest") == "on"
        db.session.commit()
        flash("Notification preferences updated.", "success")
        return redirect(url_for("company.settings"))

    return render_template("company/settings.html")


@company_bp.route("/post", methods=["GET", "POST"])
@login_required
@company_required
def post_opportunity():
    profile = current_user.company_profile

    if request.method == "POST":
        title_raw = sanitize_text(request.form.get("title", ""), max_length=150)
        title = format_title_case(title_raw)
        description = sanitize_text(request.form.get("description", ""), max_length=10000)
        opportunity_type = request.form.get("opportunity_type", "internship").strip().lower()
        field_of_study = format_title_case(sanitize_text(request.form.get("field_of_study", ""), max_length=150))
        location = format_title_case(sanitize_text(request.form.get("location", ""), max_length=120))
        required_skills = clean_comma_separated(request.form.get("required_skills", ""))

        if not title or len(title) < 3:
            flash("Opportunity title must be at least 3 characters long.", "error")
            return redirect(url_for("company.post_opportunity"))

        if opportunity_type not in ("internship", "learnership", "entry-level"):
            flash("Please choose a valid opportunity type (Internship, Learnership, or Entry-level).", "error")
            return redirect(url_for("company.post_opportunity"))

        if not description or len(description) < 15:
            flash("Opportunity description must be at least 15 characters long.", "error")
            return redirect(url_for("company.post_opportunity"))

        # Monthly stipend numeric validation
        sal_raw = request.form.get("salary_stipend")
        is_valid_sal, salary_stipend, sal_err = validate_number(
            sal_raw, field_name="Monthly stipend", min_val=0.0, max_val=500000.0, default=0.0
        )
        if not is_valid_sal:
            flash(sal_err, "error")
            return redirect(url_for("company.post_opportunity"))

        # Duration months validation
        dur_raw = request.form.get("duration_months")
        is_valid_dur, duration_months, dur_err = validate_number(
            dur_raw, field_name="Duration (months)", min_val=1, max_val=36, is_int=True, default=3
        )
        if not is_valid_dur:
            flash(dur_err, "error")
            return redirect(url_for("company.post_opportunity"))

        # Closing date validation
        closing_date_str = request.form.get("closing_date")
        is_valid_date, closing_date, date_err = validate_closing_date(closing_date_str)
        if not is_valid_date:
            flash(date_err, "error")
            return redirect(url_for("company.post_opportunity"))

        opp = Opportunity(
            company_id=profile.id,
            title=title,
            opportunity_type=opportunity_type,
            description=description,
            required_skills=required_skills,
            field_of_study=field_of_study,
            location=location,
            salary_stipend=salary_stipend,
            duration_months=duration_months,
            closing_date=closing_date,
        )
        db.session.add(opp)
        db.session.flush()

        # --- Fraud Detection: screen the new listing for fraud/anomaly signals ---
        listings_last_7_days = Opportunity.query.filter(
            Opportunity.company_id == profile.id
        ).count()

        features = {
            "salary_stipend": salary_stipend,
            "duration_months": duration_months,
            "description_length": len(description),
            "required_skills_count": len(
                [s for s in required_skills.split(",") if s.strip()]
            ),
            "company_age_years": profile.company_age_years or 0,
            "listings_posted_last_7_days": listings_last_7_days,
            "company_verified": int(bool(profile.verified)),
        }

        engine = get_engine(current_app.config["MODEL_DIR"])
        result = engine.assess_listing(features)

        opp.anomaly_score = result["anomaly_score"]
        opp.is_flagged = result["is_flagged"]
        if result["is_flagged"]:
            opp.flag_reason = result["top_factors"]

        db.session.commit()

        if result["is_flagged"]:
            flash(
                "Your listing was posted, but our fraud detection system flagged it for administrator "
                "review due to unusual characteristics. It will go live once reviewed.",
                "warning",
            )
        else:
            flash("Opportunity posted successfully.", "success")

        return redirect(url_for("company.dashboard"))

    today_str = date.today().strftime("%Y-%m-%d")
    return render_template("company/post_opportunity.html", today=today_str)


@company_bp.route("/listing/<int:opp_id>/applications")
@login_required
@company_required
def view_applications(opp_id):
    opp = Opportunity.query.get_or_404(opp_id)
    if opp.company_id != current_user.company_profile.id:
        flash("You don't have access to that listing.", "error")
        return redirect(url_for("company.dashboard"))

    apps = (
        Application.query.filter_by(opportunity_id=opp.id)
        .order_by(Application.match_score.desc())
        .all()
    )
    return render_template("company/applications.html", opp=opp, applications=apps)


@company_bp.route("/application/<int:app_id>/status", methods=["POST"])
@login_required
@company_required
def update_application_status(app_id):
    application = Application.query.get_or_404(app_id)
    if application.opportunity.company_id != current_user.company_profile.id:
        flash("You don't have access to that application.", "error")
        return redirect(url_for("company.dashboard"))

    new_status = request.form.get("status", "").strip()
    valid_statuses = ("submitted", "reviewed", "shortlisted", "rejected", "accepted")
    if new_status not in valid_statuses:
        flash("Invalid application status specified.", "error")
        return redirect(url_for("company.view_applications", opp_id=application.opportunity_id))

    # Add status change to history if status is different
    if application.status != new_status:
        application.add_status_change(new_status, f"Status updated by {current_user.company_profile.company_name}")

        # Create notification for the student
        student_user = application.student.user
        if student_user.notify_applications:
            notification = Notification(
                user_id=student_user.id,
                type="application_status",
                title=f"Application status updated to {new_status}",
                message=f"Your application for {application.opportunity.title} at {application.opportunity.company.company_name} has been updated to {new_status}.",
                link="/student/applications"
            )
            db.session.add(notification)
            student_user.unread_notifications = (student_user.unread_notifications or 0) + 1

    application.status = new_status
    db.session.commit()
    flash("Application status updated.", "success")

    return redirect(url_for("company.view_applications", opp_id=application.opportunity_id))

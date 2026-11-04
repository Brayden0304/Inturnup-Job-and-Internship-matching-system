from datetime import datetime, timedelta
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import User, StudentProfile, CompanyProfile
from utils import (
    validate_password,
    format_title_case,
    validate_email,
    validate_registration_email,
    APPROVED_REGISTRATION_EMAIL_DOMAINS,
    validate_student_name,
    validate_company_name,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(f"{current_user.role}.dashboard"))

    if request.method == "POST":
        role = request.form.get("role", "").strip()
        email_raw = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        name = request.form.get("name", "").strip()

        if role not in ("student", "company"):
            flash("Please choose a valid account type.", "error")
            return redirect(url_for("auth.register"))

        if not email_raw or not password or not name:
            flash("All fields are required.", "error")
            return redirect(url_for("auth.register"))

        # Email format & email name validation
        is_valid_email_res, email_val_or_err = validate_registration_email(email_raw)
        if not is_valid_email_res:
            flash(email_val_or_err, "error")
            return redirect(url_for("auth.register"))
        email = email_val_or_err

        # Password complexity validation (letters, numbers, special characters, min 6)
        is_valid_pass, pass_err = validate_password(password)
        if not is_valid_pass:
            flash(pass_err, "error")
            return redirect(url_for("auth.register"))

        # Role-specific name validation
        if role == "student":
            is_valid_name, name_val_or_err = validate_student_name(name)
            if not is_valid_name:
                flash(name_val_or_err, "error")
                return redirect(url_for("auth.register"))
            formatted_name = name_val_or_err
        else:
            is_valid_name, name_val_or_err = validate_company_name(name)
            if not is_valid_name:
                flash(name_val_or_err, "error")
                return redirect(url_for("auth.register"))
            formatted_name = name_val_or_err

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
            return redirect(url_for("auth.register"))

        user = User(email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # get user.id before commit

        if role == "student":
            profile = StudentProfile(
                user_id=user.id,
                full_name=formatted_name,
                profile_completeness=15.0,
            )
        else:
            profile = CompanyProfile(user_id=user.id, company_name=formatted_name)

        db.session.add(profile)
        db.session.commit()

        login_user(user)
        flash("Account created. Welcome!", "success")
        return redirect(url_for(f"{role}.dashboard"))

    return render_template("auth/register.html", approved_domains=sorted(APPROVED_REGISTRATION_EMAIL_DOMAINS))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(f"{current_user.role}.dashboard"))

    if request.method == "POST":
        email_raw = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email_raw or not password:
            flash("Please enter both email and password.", "error")
            return render_template("auth/login.html", approved_domains=sorted(APPROVED_REGISTRATION_EMAIL_DOMAINS))

        # Validate email structure
        is_valid_email_res, email_val_or_err = validate_email(email_raw)
        if not is_valid_email_res:
            flash("Please enter a valid email address.", "error")
            return render_template("auth/login.html", approved_domains=sorted(APPROVED_REGISTRATION_EMAIL_DOMAINS))
        email = email_val_or_err

        # Alias resolution: allows institutional and legacy emails to map cleanly
        alias_map = {
            "thabo.nkosi@students.wits.ac.za": "thabo@student.com",
            "ayanda.mthembu@students.uct.ac.za": "ayanda@student.com",
            "sipho.khumalo@students.up.ac.za": "sipho@student.com",
            "chloe.vdm@students.sun.ac.za": "chloe@student.com",
            "lerato.dlamini@students.ukzn.ac.za": "lerato@student.com",
            "graduates@standardbank.co.za": "standardbank@company.com",
            "talent@discovery.co.za": "discovery@company.com",
            "earlycareers@sasol.com": "sasol@company.com",
            "campusrecruitment@deloitte.co.za": "deloitte@company.com",
            "graduates@bowmanslaw.com": "bowmans@company.com",
            "admin@launchpad.ac.za": "admin@launchpad.local",
            "admin@internup.ac.za": "admin@launchpad.local",
            "admin@internup.local": "admin@launchpad.local",
            "admin@internup.com": "admin@launchpad.local",
            "acme@company.com": "standardbank@company.com",
            "recruitment@quickcash-loans.xyz": "quickcash@company.com",
        }
        lookup_email = alias_map.get(email, email)

        user = User.query.filter_by(email=lookup_email).first()
        # Existing accounts (including seeded demo/legacy domains) still work.
        # Unknown addresses with unapproved domains cannot pass sign-in.
        if user is None:
            allowed, _ = validate_registration_email(email)
            if not allowed:
                flash("Email domain is not approved. Use your registered email address.", "error")
                return render_template("auth/login.html", approved_domains=sorted(APPROVED_REGISTRATION_EMAIL_DOMAINS))
        if user and user.check_password(password):
            if not user.is_active:
                flash("This account has been quarantined by an administrator. Access is blocked until it is restored.", "error")
                return render_template("auth/login.html", approved_domains=sorted(APPROVED_REGISTRATION_EMAIL_DOMAINS))
            user.last_login_at = datetime.utcnow()
            if user.role == "student" and user.student_profile:
                user.student_profile.days_since_last_login = 0
                user.student_profile.logins_last_30_days = (
                    user.student_profile.logins_last_30_days or 0
                ) + 1
            db.session.commit()
            login_user(user)
            return redirect(url_for(f"{user.role}.dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("auth/login.html", approved_domains=sorted(APPROVED_REGISTRATION_EMAIL_DOMAINS))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email_raw = request.form.get("email", "").strip()
        is_valid_email_res, email_val_or_err = validate_email(email_raw)
        if not is_valid_email_res:
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("auth.forgot_password"))
        email = email_val_or_err

        user = User.query.filter_by(email=email).first()
        if user:
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            user.reset_token = reset_token
            user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()

            # In production, send email with reset link
            # For demo, show the link in flash message
            reset_link = url_for("auth.reset_password", token=reset_token, _external=True)
            flash(f"Password reset link (demo): {reset_link}", "info")
        else:
            flash("If an account exists with that email, a reset link has been sent.", "info")

        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()

    if not user or user.reset_token_expires < datetime.utcnow():
        flash("Invalid or expired reset link.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("auth.reset_password", token=token))

        user.set_password(password)
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()

        flash("Password has been reset. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token)

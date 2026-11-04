from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    """Base account shared by students, companies and administrators."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' | 'company' | 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active_account = db.Column(db.Boolean, default=True)

    # Password reset fields
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

    # Notification preferences
    notify_applications = db.Column(db.Boolean, default=True)
    notify_opportunities = db.Column(db.Boolean, default=True)
    notify_updates = db.Column(db.Boolean, default=True)
    email_digest = db.Column(db.Boolean, default=False)

    # Unread notification count
    unread_notifications = db.Column(db.Integer, default=0)

    student_profile = db.relationship(
        "StudentProfile", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    company_profile = db.relationship(
        "CompanyProfile", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    notifications = db.relationship(
        "Notification", backref="user", cascade="all, delete-orphan"
    )

    @property
    def is_active(self):
        """Flask-Login must reject accounts quarantined by an administrator."""
        return self.is_active_account is True

    @property
    def avatar_initials(self):
        """Initial of first and last name (Muhammad Aqeel Khan -> MK)."""
        if self.role == "admin":
            return "AD"
        if self.role == "student" and self.student_profile:
            display_name = self.student_profile.full_name or ""
        elif self.role == "company" and self.company_profile:
            display_name = self.company_profile.company_name or ""
        else:
            # Profiles can be incomplete during setup; avoid empty avatars.
            display_name = (self.email or "").split("@")[0]
            display_name = display_name.replace(".", " ").replace("_", " ").replace("-", " ")
        parts = display_name.split()
        if not parts:
            return "?"
        return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][0].upper()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not password or not self.password_hash:
            return False
        if check_password_hash(self.password_hash, password):
            return True
        # Allow case tolerance for convenience with mobile auto-capitalisation
        if check_password_hash(self.password_hash, password.lower()):
            return True
        if check_password_hash(self.password_hash, password.capitalize()):
            return True
        return False

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    full_name = db.Column(db.String(150), nullable=False)
    qualification = db.Column(db.String(150))
    field_of_study = db.Column(db.String(150))
    skills = db.Column(db.Text)  # comma separated
    interests = db.Column(db.Text)  # comma separated
    bio = db.Column(db.Text)
    location = db.Column(db.String(120))
    experience_years = db.Column(db.Float, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Engagement fields used as raw signal for fraud detection
    profile_completeness = db.Column(db.Float, default=0.0)  # 0-100
    logins_last_30_days = db.Column(db.Integer, default=0)
    applications_last_30_days = db.Column(db.Integer, default=0)
    days_since_last_login = db.Column(db.Integer, default=0)
    days_since_last_application = db.Column(db.Integer, default=0)
    saved_searches = db.Column(db.Integer, default=0)
    profile_views_received = db.Column(db.Integer, default=0)

    applications = db.relationship(
        "Application", backref="student", cascade="all, delete-orphan"
    )
    risk_assessments = db.relationship(
        "RiskAssessment", backref="student", cascade="all, delete-orphan"
    )
    bookmarked_opportunities = db.relationship(
        "Opportunity", secondary="bookmarks", backref="bookmarked_by"
    )

    def skills_list(self):
        return [s.strip() for s in (self.skills or "").split(",") if s.strip()]

    def interests_list(self):
        return [s.strip() for s in (self.interests or "").split(",") if s.strip()]


class CompanyProfile(db.Model):
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    company_name = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(120))
    website = db.Column(db.String(200))
    description = db.Column(db.Text)
    location = db.Column(db.String(120))
    company_age_years = db.Column(db.Float, default=1.0)
    verified = db.Column(db.Boolean, default=False)

    opportunities = db.relationship(
        "Opportunity", backref="company", cascade="all, delete-orphan"
    )


class Opportunity(db.Model):
    __tablename__ = "opportunities"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profiles.id"), nullable=False)

    title = db.Column(db.String(150), nullable=False)
    opportunity_type = db.Column(db.String(30))  # internship, learnership, entry-level
    description = db.Column(db.Text)
    required_skills = db.Column(db.Text)  # comma separated
    field_of_study = db.Column(db.String(150))
    location = db.Column(db.String(120))
    salary_stipend = db.Column(db.Float, default=0)
    duration_months = db.Column(db.Integer, default=3)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    closing_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)

    # Fraud detection fraud/anomaly fields
    anomaly_score = db.Column(db.Float, default=0.0)  # higher = more suspicious
    is_flagged = db.Column(db.Boolean, default=False)
    flag_reviewed = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.Text)

    applications = db.relationship(
        "Application", backref="opportunity", cascade="all, delete-orphan"
    )

    def required_skills_list(self):
        return [s.strip() for s in (self.required_skills or "").split(",") if s.strip()]


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunities.id"), nullable=False)

    status = db.Column(db.String(20), default="submitted")  # submitted, reviewed, shortlisted, rejected, accepted
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    match_score = db.Column(db.Float, default=0.0)  # skill-overlap match %
    status_history = db.Column(db.Text)  # JSON string tracking status changes with timestamps

    __table_args__ = (
        db.UniqueConstraint("student_id", "opportunity_id", name="uq_student_opportunity"),
    )

    def get_status_history(self):
        """Return status history as a list of dicts"""
        import json
        if not self.status_history:
            timestamp = self.applied_at.isoformat() if self.applied_at else datetime.utcnow().isoformat()
            return [{"status": "submitted", "timestamp": timestamp}]
        try:
            history = json.loads(self.status_history)
            # Ensure initial submission is included
            if not history or history[0].get("status") != "submitted":
                timestamp = self.applied_at.isoformat() if self.applied_at else datetime.utcnow().isoformat()
                history.insert(0, {"status": "submitted", "timestamp": timestamp})
            return history
        except:
            timestamp = self.applied_at.isoformat() if self.applied_at else datetime.utcnow().isoformat()
            return [{"status": "submitted", "timestamp": timestamp}]

    def add_status_change(self, new_status, note=""):
        """Add a status change to history"""
        import json
        history = self.get_status_history()
        history.append({
            "status": new_status,
            "timestamp": datetime.utcnow().isoformat(),
            "note": note
        })
        self.status_history = json.dumps(history)


class RiskAssessment(db.Model):
    """Stores the latest fraud detection disengagement-risk output per student."""

    __tablename__ = "risk_assessments"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), nullable=False)

    risk_label = db.Column(db.String(20))  # low, medium, high
    risk_probability = db.Column(db.Float)  # 0-1 probability of disengagement
    top_factors = db.Column(db.Text)  # JSON string of SHAP-based top contributing factors
    assessed_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    """User notifications for application status changes and platform updates."""

    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    type = db.Column(db.String(30))  # application_status, opportunity_update, system
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    link = db.Column(db.String(500))  # URL to relevant page
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Association table for bookmarked opportunities
bookmarks = db.Table(
    "bookmarks",
    db.Column("student_id", db.Integer, db.ForeignKey("student_profiles.id"), primary_key=True),
    db.Column("opportunity_id", db.Integer, db.ForeignKey("opportunities.id"), primary_key=True),
)

from flask import Flask, flash, redirect, request, session, url_for
from flask_login import logout_user
from config import get_config
from extensions import db, login_manager
from models import User


def create_app(config_name=None):
    app = Flask(__name__)
    config = get_config(config_name)
    app.config.from_object(config)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            user = db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None
        # Flask-Login normally restores signed-in users without checking
        # UserMixin.is_active. Never restore a quarantined user's session.
        return user if user is not None and user.is_active else None

    @app.before_request
    def revoke_quarantined_sessions():
        """Invalidate sessions already open when an admin quarantines an account."""
        signed_in_user_id = session.get("_user_id")
        if signed_in_user_id is None:
            return
        try:
            user = db.session.get(User, int(signed_in_user_id))
        except (TypeError, ValueError):
            user = None
        if user is None or not user.is_active:
            # Remove the signed-in identity, freshness token and remember cookie.
            # This also prevents a disabled session from coming back on restore.
            logout_user()
            if user is not None:
                flash("Your account is quarantined. Contact an administrator to restore access.", "error")
            if request.endpoint not in ("static", "main.index", "auth.login", "admin.admin_login"):
                return redirect(url_for("auth.login"))

    @app.after_request
    def protect_authenticated_page_cache(response):
        # Don't show an old private page when the user presses Back after logout
        # or after their account has been quarantined.
        if session.get("_user_id") and response.mimetype == "text/html":
            response.headers["Cache-Control"] = "private, no-store, max-age=0"
            response.headers["Pragma"] = "no-cache"
        return response

    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.company import company_bp
    from routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        # Generate PWA App Icons if missing
        import os
        if not os.path.exists("static/icon-192.png"):
            try:
                import make_icons
                make_icons.make_png(192, 192, (10, 11, 13), (197, 160, 89), "static/icon-192.png")
                make_icons.make_png(512, 512, (10, 11, 13), (197, 160, 89), "static/icon-512.png")
            except Exception:
                pass
        # Lazily initialise fraud detection models the first time they're needed
        # (see routes/admin.py -> get_drop_guard()) rather than at import time,
        # so a plain `flask run` stays fast to start.

    return app


app = create_app()

if __name__ == "__main__":
    import os
    env = os.environ.get("FLASK_ENV", "development")
    app = create_app(env)
    debug = env == "development"

    # Auto-start periodic background database backup service
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not debug:
        try:
            from periodic_backup import start_in_app_periodic_backup
            interval = int(os.environ.get("BACKUP_INTERVAL_MINUTES", "15"))
            start_in_app_periodic_backup(interval_minutes=interval, retention_count=20)
        except Exception as e:
            print(f"[!] Warning: Could not initialize periodic backup: {e}")

    app.run(debug=debug, port=5000, host="0.0.0.0")

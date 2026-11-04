# LaunchPad: Full-Stack Architecture & Implementation Manual
## A Complete Part-by-Part Engineering Breakdown for Pavan Saihan Singh

**Project Title:** LaunchPad — Student Job & Internship Matching System  
**Framework:** Python 3 / Flask (Application Factory & Blueprint Pattern)  
**ORM & Database:** SQLAlchemy / SQLite (MySQL-ready)  
**Machine Learning:** scikit-learn (RandomForest, IsolationForest) & SHAP (TreeExplainer)  
**Target Submission:** Richfield Faculty of Information Technology — Year 3 Capstone  

---

## Overview: How the Pieces Connect

LaunchPad is constructed using the **Model-View-Controller (MVC)** architectural pattern. The entire application is organized into logical, decoupled components so that backend business logic, database models, machine learning models, and frontend views can be maintained and tested independently.

```mermaid
flowchart TD
    subgraph View ["Presentation Tier (View)"]
        UI["Jinja2 HTML Templates\n(templates/)"]
        CSS_JS["CSS Stylesheets & Client JS\n(static/css, static/js)"]
    end

    subgraph Controller ["Application Tier (Controller & Logic)"]
        APP["Flask Application Factory\n(app.py)"]
        AUTH_R["Auth Blueprint\n(routes/auth.py)"]
        STUD_R["Student Blueprint\n(routes/student.py)"]
        COMP_R["Company Blueprint\n(routes/company.py)"]
        ADM_R["Admin Blueprint\n(routes/admin.py)"]
        UTILS["Matching Engine\n(utils.py)"]
        ML_ENG["Drop Guard AI Engine\n(ml/drop_guard.py)"]
    end

    subgraph Model ["Data Tier (Model & Persistence)"]
        ORM["SQLAlchemy ORM\n(models.py)"]
        DB[(SQLite Database\ninstance/app.db)]
        ML_FILES[("Saved ML Models (.joblib)\nml/saved_models/")]
    end

    UI <--> APP
    APP --> AUTH_R & STUD_R & COMP_R & ADM_R
    STUD_R --> UTILS
    COMP_R & ADM_R --> ML_ENG
    ML_ENG <--> ML_FILES
    AUTH_R & STUD_R & COMP_R & ADM_R <--> ORM
    ORM <--> DB
```

---

## Part 1: Application Factory, Configuration & Extensions

### 1.1 The Application Factory (`app.py`)
In standard beginner Flask apps, everything is often dumped in one global `app = Flask(__name__)`. LaunchPad uses the professional **Application Factory Pattern** (`create_app()`):

```python
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    # Register modular blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(company_bp, url_prefix='/company')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()

    return app
```

**Why this was built this way:**
- **URL Namespacing:** Notice the `url_prefix` parameters. Student routes live under `/student/...`, company routes under `/company/...`, and admin routes under `/admin/...`. This enforces clean routing and simplifies role checks.
- **Dynamic Database Creation:** The `db.create_all()` call inside `app.app_context()` ensures that whenever you start the application on a new computer, it automatically builds the SQLite database file (`instance/app.db`) if it doesn't already exist.

### 1.2 Configuration (`config.py`)
`config.py` centralizes all environment variables and paths:
- `SECRET_KEY`: Used to cryptographically sign session cookies so users cannot tamper with their logged-in user ID or role.
- `SQLALCHEMY_DATABASE_URI`: Defaults to `sqlite:///app.db`. However, notice that it checks `os.environ.get('DATABASE_URL')`. If you supply a MySQL URL (e.g. `mysql+pymysql://root:pass@localhost/launchpad`), Flask connects to MySQL with zero code modifications!
- `MODEL_DIR`: Points to the directory where trained machine learning models are saved (`ml/saved_models`).

### 1.3 Decoupled Extensions (`extensions.py`)
`extensions.py` instantiates `db = SQLAlchemy()` and `login_manager = LoginManager()`.  
**Why separate this?** To prevent **circular import errors**. If `models.py` imported `db` from `app.py`, while `app.py` imported models from `models.py`, Python would crash. Having a tiny `extensions.py` file breaks circular dependencies completely.

---

## Part 2: Database Schema & Relational Data Modeling (`models.py`)

LaunchPad's database structure uses six relational tables designed to satisfy 3rd Normal Form (3NF) and enforce data integrity.

### 2.1 The Six Tables and Their Responsibilities

1. **`users` Table:**
   - Central authentication record for every account.
   - Columns: `id`, `email` (unique, indexed), `password_hash` (stores 255-character salted PBKDF2 hash, never plain text), `role` (`'student'`, `'company'`, or `'admin'`), `is_active_account` (boolean flag to enable/disable accounts), `created_at`, `last_login_at`.
   - Relationships: One-to-one with `student_profiles` and `company_profiles`.

2. **`student_profiles` Table:**
   - Stores candidate attributes and engagement counters.
   - Core Profile: `full_name`, `qualification`, `field_of_study`, `skills` (comma-separated string), `interests`, `bio`, `location`, `experience_years`, `profile_completeness`.
   - Behavioral Tracking Columns: `logins_last_30_days`, `applications_last_30_days`, `days_since_last_login`, `days_since_last_application`, `saved_searches`, `profile_views_received`. These columns are continuously updated and feed directly into Drop Guard AI!

3. **`company_profiles` Table:**
   - Stores verified employer attributes.
   - Columns: `company_name`, `industry`, `website`, `description`, `location`, `company_age_years` (years in business), `verified` (boolean badge indicating institutional vetting).

4. **`opportunities` Table:**
   - Advertised positions posted by companies.
   - Columns: `company_id` (foreign key to `company_profiles.id`), `title`, `opportunity_type` (`internship`, `learnership`, `entry-level`), `description`, `required_skills`, `field_of_study`, `location`, `salary_stipend`, `duration_months`, `closing_date`, `is_active`.
   - Fraud Screening Columns: `anomaly_score` (0-100 float from Drop Guard), `is_flagged` (boolean), `flag_reviewed` (boolean), `flag_reason` (JSON string containing top SHAP factors).

5. **`applications` Table:**
   - Represents the many-to-many relationship linking students to opportunities.
   - Columns: `student_id` (FK), `opportunity_id` (FK), `status` (`'submitted'`, `'reviewed'`, `'shortlisted'`, `'rejected'`, `'accepted'`), `applied_at`, `match_score` (the calculated % match at time of application).
   - **Crucial Constraint:** `db.UniqueConstraint('student_id', 'opportunity_id', name='uq_student_opportunity')`. This database-level rule physically stops any student from submitting duplicate applications for the same job.

6. **`risk_assessments` Table:**
   - Audit trail generated by Drop Guard AI for institutional deans.
   - Columns: `student_id` (FK), `risk_label` (`'low'`, `'medium'`, `'high'`), `risk_probability` (0.0 to 1.0 float), `top_factors` (JSON string storing the top 3 SHAP feature explanations), `assessed_at`.

---

## Part 3: Authentication & Role-Based Access Control (`routes/auth.py`)

### 3.1 Password Security (PBKDF2 Salted Hashing)
Passwords are never stored in plain text. In `models.py`, `User.set_password(plain_password)` invokes:
```python
self.password_hash = generate_password_hash(plain_password)
```
Werkzeug uses the **PBKDF2-HMAC-SHA256** cryptographic algorithm with a random salt. Even if two users choose the identical password `password123`, their stored hashes are completely different, preventing rainbow table attacks.

### 3.2 Role-Based Access Control (RBAC) Decorators
How does LaunchPad ensure a student cannot view another company's applicant pool or access admin tools? Through a custom decorator defined in `routes/auth.py`:

```python
def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.role != required_role:
                flash(f"That page is only accessible to {required_role} accounts.", "error")
                return redirect(url_for('main.index'))
            return fn(*args, **kwargs)
        return decorated_view
    return decorator
```
Every route in `routes/student.py` is protected by `@role_required('student')`, `routes/company.py` by `@role_required('company')`, and `routes/admin.py` by `@role_required('admin')`.

---

## Part 4: The Deterministic Matching Engine (`utils.py`)

The matching algorithm is implemented in [`utils.py`](file:///C:/Users/pavan/Downloads/student-job-matching-20261027T105016Z-1-001%20(2)/student-job-matching-20261027T105016Z-1-001/student-job-matching/utils.py):

```python
def compute_match_score(student_skills, student_field, opportunity):
    required = set(s.lower() for s in opportunity.required_skills_list())
    student_set = set(s.lower() for s in student_skills)

    if required:
        overlap = len(required & student_set) / len(required)
    else:
        overlap = 0.5

    field_bonus = 0.0
    if student_field and opportunity.field_of_study:
        if student_field.strip().lower() == opportunity.field_of_study.strip().lower():
            field_bonus = 0.2

    score = min(1.0, overlap * 0.8 + field_bonus)
    return round(score * 100, 1)
```

### Mathematical Breakdown
1. **Case-Insensitive Set Intersection:** Both student skills and opportunity requirements are converted to lowercase sets. If an opportunity requires `{python, sql, flask}` and the student has `{python, java, sql, flask, git}`, the intersection `required & student_set` is `{python, sql, flask}` ($3 / 3 = 1.0$).
2. **Weighting:** Skill overlap provides up to 80% ($0.8$) of the total score.
3. **Academic Alignment Bonus:** If the student's degree field (e.g., "Information Technology") matches the opportunity's field, they receive a 20% ($0.2$) bonus.
4. **Bounding & Scaling:** The total is bounded by `min(1.0, ...)` and multiplied by 100, yielding an explainable score between 0% and 100%.

---

## Part 5: The Drop Guard™ Machine Learning Subsystem (`ml/`)

Drop Guard AI is composed of two scikit-learn models and an explainability engine.

### 5.1 Listing Fraud Detection: Isolation Forest (`ml/drop_guard.py`)
- **Type:** Unsupervised anomaly detection.
- **Why Unsupervised?** In real life, scammers constantly invent new tricks. Supervised models only detect past known frauds. An **Isolation Forest** isolates anomalies by randomly partitioning feature space. Outliers are isolated in very few splits.
- **Features Evaluated:**
  1. `salary_stipend` (unusually high entry-level pay)
  2. `duration_months` (abnormally short or long)
  3. `description_length` (spam listings typically have 1-2 generic sentences)
  4. `required_skills_count` (0 skills or absurdly high requirements)
  5. `company_age_years` (brand new 0-year entities)
  6. `listings_posted_last_7_days` (posting bursts / bot activity)
  7. `company_verified` (binary trust flag)
- **Scoring:** The raw decision function is converted into a normalized 0–100 suspicion score:
  $$\text{suspicion\_score} = \text{clamp}\Big((0.5 - \text{raw\_score}) \times 100, \, 0, \, 100\Big)$$
  If the listing is an outlier (`predict() == -1`), it is flagged, and students cannot see it until an admin inspects it.

### 5.2 Student Disengagement Risk: Random Forest Classifier
- **Type:** Supervised ensemble classifier.
- **Goal:** Predict the probability $P(\text{disengaged} = 1)$ that a student will drop out of the search pipeline.
- **Features Evaluated:** Profile completeness, 30-day logins, 30-day applications, days since last login, days since last application, saved searches, and profile views.
- **Thresholds:**
  - $\ge 66\%$ probability $\rightarrow$ **High Risk** (Red)
  - $35\%$ to $65\%$ probability $\rightarrow$ **Medium Risk** (Yellow)
  - $< 35\%$ probability $\rightarrow$ **Low Risk** (Green)

### 5.3 Explainable AI (XAI) via SHAP (SHapley Additive exPlanations)
Most AI projects fail in presentations because lecturers ask: *"Why did the AI give this score?"* and students have no answer.  
LaunchPad uses `shap.TreeExplainer(model)`. Based on cooperative game theory, SHAP calculates the exact marginal contribution of each feature to the model's output.  
- For QuickCash, SHAP outputs: `[{"feature": "salary_stipend", "impact": "+1.61"}, {"feature": "company_age_years", "impact": "+0.84"}]`.
- For Lerato Dlamini, SHAP outputs: `[{"feature": "profile_completeness", "direction": "increases risk"}, {"feature": "days_since_last_application", "direction": "increases risk"}]`.
- If SHAP is ever slow or unavailable, `drop_guard.py` includes a safe fallback that calculates standard deviations from the population mean, guaranteeing that the app never crashes!

---

## Part 6: Front-End UI, Jinja2 Templates & Styling

### 6.1 Template Inheritance
Instead of duplicating headers, navbars, and footers across 15 HTML files, LaunchPad uses Jinja2 template inheritance:
- **`templates/base.html`:** Contains the global HTML5 skeleton, meta tags, fonts, flash message display containers, responsive navigation bar, and footer.
- **Child templates (`{% extends "base.html" %}`):** Only define `{% block content %}` for their specific view (e.g., `templates/student/dashboard.html`, `templates/admin/drop_guard.html`).

### 6.2 Flash Notification System
Whenever an action occurs (e.g., saving a profile, applying for a job, updating an applicant status), the route calls `flash("Message", "category")`. `base.html` automatically renders these as clean green (success), red (error), or yellow (warning) alerts.

### 6.3 Responsive Styling (`static/css/style.css`)
The CSS uses modern CSS variables (`--primary`, `--bg`, `--card`, `--border`) with Flexbox and CSS Grid layout techniques, ensuring the dashboard looks sharp on standard 1080p projectors, desktop monitors, and laptops.

---

## Part 7: Database Seeding & Running Options

### 7.1 Seed Script (`seed.py`)
`seed.py` creates a realistic, rich demonstration dataset in under 2 seconds:
- 1 Administrator (`admin@launchpad.local`)
- 5 Diverse Students:
  - **Thabo Nkosi** (BSc CS, Wits, high engagement, ready for tech roles)
  - **Ayanda Mthembu** (BCom Accounting, CTA, finance roles)
  - **Sipho Khumalo** (BEng Mechanical, UP, engineering roles)
  - **Chloe van der Merwe** (BA Brand Strategy, marketing roles)
  - **Lerato Dlamini** (Clinical Nursing, disengagement demo)
- 6 Realistic Companies:
  - Verified blue-chips: Standard Bank, Discovery, Sasol, Deloitte, Bowmans.
  - Fraud demo: **QuickCash Global Capital** (unverified, high stipend scam listing).

### 7.2 Running Options
1. **Local Mode (Default for offline grading/lab computers):**
   ```bash
   python seed.py
   python app.py
   ```
   Open `http://127.0.0.1:5000` in Chrome/Edge.
2. **Cloudflare Tunnel Mode (`RUN_ONLINE_CLOUDFLARE.bat`):**
   If presenting remotely or allowing lecturers to test the app on their own phones or laptops, running this batch file uses `cloudflared.exe` to expose a secure public HTTPS URL (e.g. `https://launchpad-demo.trycloudflare.com`) without configuring router port-forwarding!

---

## Summary: Key Talking Points to Impress the Panel

1. **Software Engineering Rigor:** You followed the Agile model through all 4 phases with clear SRS documentation, DFDs, ERDs, and class diagrams.
2. **Architectural Separation:** Strict 3-tier MVC separation with Flask Blueprints and SQLAlchemy ORM.
3. **Data Integrity & Security:** Database-level uniqueness constraints, role-based route guards, and salted PBKDF2 hashing.
4. **Machine Learning Beyond Black Boxes:** Drop Guard AI combines unsupervised anomaly screening with supervised risk scoring, backed by SHAP explainability.
5. **Production Readiness:** Portable SQLite development with immediate MySQL scalability via environment variables.

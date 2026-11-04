# LaunchPad: Full-Stack Architecture, Codebase & Guideline Compliance Manual
## Complete Part-by-Part Engineering Guide & Implementation Defense

**Project Title:** LaunchPad — Student Job & Internship Matching System  
**Institution:** Faculty of Information Technology | Richfield Graduate Institute of Technology  
**Module:** IT Project — Year 3 (Cap-Stone Project)  
**Project Lead:** Pavan Saihan Singh (Student ID: 402307292)  
**Framework & Stack:** Python 3.10+ / Flask 3.0 / SQLAlchemy ORM / SQLite (MySQL-Ready) / scikit-learn & SHAP  

---

# SECTION 1: GUIDELINE COMPLIANCE & REQUIREMENTS TRACEABILITY MATRIX
## What the Guidelines Wanted vs. What We Built vs. In-Depth Code Explanation

The Richfield Year 3 IT Project Student Guide and Phases 1 through 4 establish rigorous academic and technical requirements. This section directly contrasts each guideline requirement against our implemented codebase, explaining the exact programming constructs, design choices, and file locations.

```
+--------------------------------------------------------------------------------------------------------------------+
| 1. MANDATORY SOFTWARE DEVELOPMENT (GUIDELINE SEC 1 & 2)                                                           |
+--------------------------------------------------------------------------------------------------------------------+
| GUIDELINE REQUIREMENT:                                                                                             |
| "The project work should compulsorily include software development. Physical installations, LAN/WAN configurations,|
| or theoretical projects/studies that do not involve software development are strictly not allowed."               |
+--------------------------------------------------------------------------------------------------------------------+
| WHAT WE BUILT:                                                                                                     |
| A production-grade, full-stack web application written in Python 3 and Flask 3.0, backed by a 3NF relational       |
| database via SQLAlchemy ORM, featuring an advanced machine learning subsystem (scikit-learn & SHAP), interactive   |
| responsive user interfaces, and automated disaster recovery services.                                             |
+--------------------------------------------------------------------------------------------------------------------+
| CODE EXPLANATION:                                                                                                  |
| - app.py implements the Application Factory pattern (`create_app()`).                                              |
| - models.py defines 6 fully mapped relational models inheriting from `db.Model`.                                   |
| - utils.py implements the deterministic skill-matching calculation.                                                |
| - ml/drop_guard.py and ml/data_simulation.py construct and persist dual scikit-learn models.                         |
| - routes/ package organizes routing into 5 decoupled Blueprints.                                                  |
+--------------------------------------------------------------------------------------------------------------------+
```

### Detailed Code Walkthrough: Application Factory (`app.py`)
In beginner tutorials, Flask applications are typically declared as a global object (`app = Flask(__name__)`). In professional software engineering, this causes cyclic dependencies and makes unit testing difficult. LaunchPad implements the **Application Factory Pattern**:

```python
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the application context
    db.init_app(app)
    login_manager.init_app(app)

    # Register decoupled modular Blueprints with URL prefixes
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(company_bp, url_prefix='/company')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Automatically create tables if SQLite file does not exist
    with app.app_context():
        db.create_all()

    return app
```
**How this code works:**
1. `app.config.from_object(config_class)` loads runtime variables from `config.py` (database connection strings, secret keys, model paths).
2. `db.init_app(app)` binds SQLAlchemy to this application instance without hardcoding database drivers.
3. `login_manager.init_app(app)` configures user session management and sets the default login view (`auth.login`).
4. `url_prefix` parameters enforce strict namespace separation: all student endpoints reside under `/student/*`, company endpoints under `/company/*`, and admin endpoints under `/admin/*`.
5. `with app.app_context(): db.create_all()` checks if `instance/app.db` exists. If not, it executes SQLite DDL statements to construct all tables, ensuring zero-configuration portability on any evaluation laptop.

---

```
+--------------------------------------------------------------------------------------------------------------------+
| 2. USER ROLES & ROLE-BASED ACCESS CONTROL (PHASE 2 & PHASE 3.6)                                                    |
+--------------------------------------------------------------------------------------------------------------------+
| GUIDELINE REQUIREMENT:                                                                                             |
| "The system will offer services to three types of users: students, companies and administrators... Protected       |
| functions and information should only be available after successful authentication and according to user role."   |
+--------------------------------------------------------------------------------------------------------------------+
| WHAT WE BUILT:                                                                                                     |
| Multi-tenant Role-Based Access Control (RBAC). A custom Python decorator `@role_required` wraps every endpoint,     |
| inspecting authenticated user tokens and intercepting unauthorized privilege escalations.                         |
+--------------------------------------------------------------------------------------------------------------------+
```

### Detailed Code Walkthrough: Security Decorator (`routes/auth.py`)
```python
def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            # Check 1: Is the user logged in?
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            
            # Check 2: Does the user role match the required role?
            if current_user.role != required_role:
                flash(f"That page is only accessible to {required_role} accounts.", "error")
                return redirect(url_for('main.index'))
            
            # Check 3: Is the account active?
            if not current_user.is_active_account:
                flash("Your account has been deactivated. Please contact support.", "error")
                logout_user()
                return redirect(url_for('auth.login'))

            return fn(*args, **kwargs)
        return decorated_view
    return decorator
```
**How this code works:**
- Python's `@wraps(fn)` preserves the original view function's metadata and docstrings.
- If an unauthenticated user accesses `/student/dashboard`, `login_manager.unauthorized()` flashes an error and redirects to `/login`.
- If an authenticated student attempts to view `/admin/users` or `/company/post`, the decorator intercepts the request, checks `current_user.role`, flashes an access violation alert, and redirects them to the landing page.
- Furthermore, if an administrator disabled that account (`is_active_account = False`), the decorator immediately terminates the session via `logout_user()` and redirects to login.

---

```
+--------------------------------------------------------------------------------------------------------------------+
| 3. PASSWORD ENCRYPTION & DATA SECURITY (PHASE 4.8.1 & GUIDELINE SEC 7)                                             |
+--------------------------------------------------------------------------------------------------------------------+
| GUIDELINE REQUIREMENT:                                                                                             |
| "Passwords must not be stored in readable plain text. Only a salted hash is saved and compared at login. The Flask |
| application uses a secret key to protect user sessions."                                                           |
+--------------------------------------------------------------------------------------------------------------------+
| WHAT WE BUILT:                                                                                                     |
| Industrial-grade cryptographic hashing using Werkzeug's PBKDF2-HMAC-SHA256 with 8-byte random salt generation.     |
+--------------------------------------------------------------------------------------------------------------------+
```

### Detailed Code Walkthrough: Cryptographic Hashing (`models.py`)
```python
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active_account = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```
**How this code works:**
- `generate_password_hash(password)` generates a string structured as: `pbkdf2:sha256:260000$salt$hash`.
- Even if two users choose the identical password `password123`, their generated hashes are mathematically unique because a distinct pseudorandom salt is combined with the input before 260,000 hashing rounds.
- When logging in, `check_password_hash()` hashes the entered plain text with the stored salt and compares the two digests in constant time, preventing timing attacks.

---

```
+--------------------------------------------------------------------------------------------------------------------+
| 4. DATABASE INTEGRITY & 3NF NORMALIZATION (PHASE 3.4 & PHASE 4.5)                                                  |
+--------------------------------------------------------------------------------------------------------------------+
| GUIDELINE REQUIREMENT:                                                                                             |
| "Enforce Entity integrity (primary keys), Referential integrity (foreign keys), Domain integrity, and Uniqueness   |
| constraints... Ensure one student should not submit the same application repeatedly for the same opportunity."     |
+--------------------------------------------------------------------------------------------------------------------+
| WHAT WE BUILT:                                                                                                     |
| A normalized 6-table relational architecture with cascading foreign keys, non-null field validations, and an      |
| explicit table-level composite UniqueConstraint on (student_id, opportunity_id).                                   |
+--------------------------------------------------------------------------------------------------------------------+
```

### Detailed Code Walkthrough: Anti-Duplicate Relational Constraint (`models.py`)
```python
class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'), nullable=False)
    status = db.Column(db.String(20), default='submitted')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    match_score = db.Column(db.Float, default=0.0)

    # Composite Unique Constraint enforcing Business Rule 3.4.5 & 3.4.7
    __table_args__ = (
        db.UniqueConstraint('student_id', 'opportunity_id', name='uq_student_opportunity'),
    )
```
**How this code works:**
- `db.ForeignKey('student_profiles.id')` and `db.ForeignKey('opportunities.id')` enforce referential integrity. An application cannot exist pointing to an invalid student or an deleted vacancy.
- `__table_args__ = (db.UniqueConstraint('student_id', 'opportunity_id', ...),)` instructs the underlying database engine to create a composite unique index. If any user, script, or concurrent network request attempts to insert a second record for the same student and job, the database engine aborts the transaction with an `IntegrityError`.

---

```
+--------------------------------------------------------------------------------------------------------------------+
| 5. DETERMINISTIC MATCHING ALGORITHM (PHASE 4.2.4 & PHASE 4.6.4)                                                    |
+--------------------------------------------------------------------------------------------------------------------+
| GUIDELINE REQUIREMENT:                                                                                             |
| "Skill overlap: student skills divided by required skills (default 0.5 if none provided). Field-of-study bonus: 0.2|
| added if student field matches. Score (%) = min(1, (Skill Overlap * 0.8) + Field Bonus) * 100."                    |
+--------------------------------------------------------------------------------------------------------------------+
| WHAT WE BUILT:                                                                                                     |
| A clean, explainable mathematical engine in utils.py implementing set theory intersection, case normalization,     |
| and bounded scaling.                                                                                               |
+--------------------------------------------------------------------------------------------------------------------+
```

### Detailed Code Walkthrough: The Matching Engine (`utils.py`)
```python
def compute_match_score(student_skills, student_field, opportunity):
    # Extract lowercased sets to guarantee case-insensitive comparison
    required = set(s.lower() for s in opportunity.required_skills_list())
    student_set = set(s.lower() for s in student_skills)

    # Calculate skill overlap ratio
    if required:
        overlap = len(required & student_set) / len(required)
    else:
        overlap = 0.5  # Specification fallback

    # Field-of-study alignment check
    field_bonus = 0.0
    if student_field and opportunity.field_of_study:
        if student_field.strip().lower() == opportunity.field_of_study.strip().lower():
            field_bonus = 0.2

    # Weighting: 80% skills, 20% academic discipline bonus, bounded to 1.0 (100%)
    score = min(1.0, (overlap * 0.8) + field_bonus)
    return round(score * 100, 1)
```
**How this code works:**
- `opportunity.required_skills_list()` splits comma-separated strings (e.g., `"Python, SQL, Flask"`) into Python lists.
- `required & student_set` computes set intersection. If an opportunity requires 4 skills and the student possesses 3, overlap is $3/4 = 0.75$.
- Multiplying by $0.8$ yields $0.60$ (60%). If the student also studied Computer Science, the $+0.20$ bonus triggers, producing $0.80$ (80%).
- `min(1.0, ...)` ensures that students with extra skills or bonuses cannot exceed 100%.

---

```
+--------------------------------------------------------------------------------------------------------------------+
| 6. DROP GUARD™ AI SUBSYSTEM & SHAP EXPLAINABILITY (PHASE 4.2.5 & 4.6.10)                                          |
+--------------------------------------------------------------------------------------------------------------------+
| GUIDELINE REQUIREMENT:                                                                                             |
| "Suspicious listing detection using Isolation Forest (0-100 score). Student disengagement risk assessment using    |
| Random Forest (Low <35%, Med 35-65%, High >=66%). Top 3 factors identified using SHAP."                            |
+--------------------------------------------------------------------------------------------------------------------+
| WHAT WE BUILT:                                                                                                     |
| A complete machine learning pipeline in ml/ combining unsupervised anomaly detection, supervised classification,  |
| and cooperative game theory feature attribution via SHAP TreeExplainer.                                           |
+--------------------------------------------------------------------------------------------------------------------+
```

### Detailed Code Walkthrough: Isolation Forest Listing Fraud Screening (`ml/drop_guard.py`)
```python
def assess_listing(self, features_dict):
    self._ensure_models_trained()
    X = pd.DataFrame([features_dict])[LISTING_FEATURE_NAMES]

    # Outlier prediction: -1 = anomaly, 1 = normal inlier
    is_anomaly = bool(self.anomaly_model.predict(X)[0] == -1)
    raw_score = float(self.anomaly_model.decision_function(X)[0])

    # Convert decision score to normalized 0-100 suspicion score
    suspicion_score = float(np.clip((0.5 - raw_score) * 100, 0.0, 100.0))

    # Explain prediction using SHAP TreeExplainer
    factors = self._explain_listing_shap(X)

    return {
        'flagged': is_anomaly,
        'suspicion_score': round(suspicion_score, 1),
        'factors': factors
    }
```
**How this code works:**
- `features_dict` extracts 7 numerical vacancy features: `salary_stipend`, `duration_months`, `description_length`, `required_skills_count`, `company_age_years`, `listings_posted_last_7_days`, and `company_verified`.
- `IsolationForest` isolates anomalies by constructing decision trees with random splits. Because abnormal values (e.g. stipend = R65,000 for a 1-month unverified job) sit far from the normal cluster, they require very few tree splits to isolate, resulting in high anomaly scores.
- `_explain_listing_shap(X)` passes the tree model and feature vector into `shap.TreeExplainer`, which computes Shapley values—measuring how much each feature shifted the prediction away from the baseline average.

---

# SECTION 2: SYSTEM ARCHITECTURE & CODEBASE REPOSITORY BREAKDOWN

LaunchPad is organized following separation of concerns across presentation, logic, and data storage.

```
student-job-matching/
├── app.py                          # Application factory entry point
├── config.py                       # Configuration classes & environment vars
├── extensions.py                   # Decoupled SQLAlchemy & LoginManager singletons
├── models.py                       # Relational schema (6 tables, foreign keys & methods)
├── utils.py                        # Deterministic matching calculation & string parsers
├── seed.py                         # Realistic demonstration data population script
├── db_sync_backup.py               # Automated database backup & restore utility
├── periodic_backup.py              # Background 15-minute scheduled snapshot service
├── requirements.txt                # Python package dependency specifications
├── instance/                       # SQLite database directory (app.db)
├── backups/                        # Timestamped database recovery archives
├── ml/                             # Machine learning engine
│   ├── drop_guard.py               # DropGuardEngine (IsolationForest, RandomForest, SHAP)
│   ├── data_simulation.py          # Synthetic training distribution generators
│   └── saved_models/               # Serialized .joblib model files
├── routes/                         # Flask Blueprints (Controllers)
│   ├── auth.py                     # Register, login, logout, password reset, @role_required
│   ├── student.py                  # Profile builder, vacancy search, application pipeline
│   ├── company.py                  # Recruiter profiles, posting vacancies, reviewing CVs
│   ├── admin.py                    # Platform analytics, listing review, Drop Guard UI
│   └── main.py                     # Unauthenticated home page and static marketing
├── templates/                      # Jinja2 Presentation Templates (Views)
│   ├── base.html                   # Master layout with responsive nav & flash alerts
│   ├── auth/                       # login.html, register.html
│   ├── student/                    # dashboard.html, profile.html, search.html, applications.html
│   ├── company/                    # dashboard.html, post.html, applicants.html
│   └── admin/                      # dashboard.html, users.html, drop_guard.html
└── static/                         # CSS styles, JavaScript logic, and assets
```

---

# SECTION 3: PART-BY-PART APP BUILD EXPLANATION

```
========================================================================================
PART 1: THE APPLICATION FACTORY & SYSTEM INITIALIZATION
========================================================================================
```
1. **Application Lifecycle:** When `python app.py` executes, Python calls `create_app()`.
2. **Configuration Binding:** `app.config.from_object(Config)` reads environment settings. The database URI defaults to `instance/app.db`.
3. **Extension Binding:** `db.init_app(app)` binds SQLAlchemy; `login_manager.init_app(app)` registers user session handlers.
4. **Blueprint Registration:** All routes are registered with their respective URL namespaces (`/student`, `/company`, `/admin`).
5. **Schema Provisioning:** `db.create_all()` verifies that the database file exists. If running on a new computer for the first time, all tables, indexes, and constraints are generated on the spot.

```
========================================================================================
PART 2: RELATIONAL DATABASE & 3NF DATA MODELING
========================================================================================
```
LaunchPad's database structure uses six relational tables designed to satisfy 3rd Normal Form (3NF) and enforce data integrity:
- **`users` Table:** Stores unique login credentials (`email`, `password_hash`, `role`).
- **`student_profiles` Table:** Stores student credentials (`full_name`, `qualification`, `skills`, `bio`) and 7 Drop Guard behavioral counters (`logins_last_30_days`, `applications_last_30_days`, `days_since_last_login`, etc.).
- **`company_profiles` Table:** Stores employer credentials (`company_name`, `industry`, `company_age_years`, `verified`).
- **`opportunities` Table:** Stores vacancy details (`title`, `required_skills`, `salary_stipend`, `duration_months`, `closing_date`, `anomaly_score`, `is_flagged`).
- **`applications` Table:** Many-to-many bridge table between Student and Opportunity. Enforces `UNIQUE(student_id, opportunity_id)`.
- **`risk_assessments` Table:** Audit history for Drop Guard disengagement predictions (`risk_label`, `risk_probability`, `top_factors`).

```
========================================================================================
PART 3: AUTHENTICATION, ROUTE PROTECTION & USER GOVERNANCE
========================================================================================
```
1. **Registration Workflow (`routes/auth.py: register()`):**
   - Validates that email is unique and non-empty.
   - Hashes password using Werkzeug's `generate_password_hash()`.
   - Creates a `User` record, and depending on the selected role, creates a blank `StudentProfile` (initial completeness 15%) or `CompanyProfile`.
2. **Login & Session Establishment (`routes/auth.py: login()`):**
   - Queries `User.query.filter_by(email=email).first()`.
   - Compares password using `user.check_password(password)`.
   - Updates `last_login_at` timestamp.
   - For students, resets `days_since_last_login = 0` and increments `logins_last_30_days += 1`.
   - Logs the user in via `flask_login.login_user(user)` and redirects them to their respective role dashboard.
3. **Role-Based Guards (`@role_required`):**
   - Intercepts requests to prevent unauthorized cross-role access (e.g. students trying to access recruiter applicant pools).

```
========================================================================================
PART 4: THE DETERMINISTIC MATCHING ENGINE
========================================================================================
```
1. **Parsing Skills Taxonomy:** Vacancy requirements (e.g., `"Python, SQL, Flask"`) and student skills (e.g., `"Python, Git, SQL, Docker"`) are parsed into normalized lowercase sets.
2. **Jaccard Intersection:** The intersection of both sets determines the skill overlap ratio:
   $$	ext{Skill Overlap} = rac{|	ext{Required Skills} \cap 	ext{Student Skills}|}{|	ext{Required Skills}|}$$
3. **Field Bonus:** If `student_profile.field_of_study == opportunity.field_of_study`, a $+0.2$ bonus is awarded.
4. **Final Computation:**
   $$	ext{Match Score (\%)} = \min\Big(1.0, \,(	ext{Skill Overlap} 	imes 0.8) + 	ext{Field Bonus}\Big) 	imes 100$$
5. **Real-Time Dynamic Sorting:** In `routes/company.py`, when a recruiter views applicants, SQLAlchemy queries all applications for that listing and sorts them by `Application.match_score.desc()`, presenting the top candidates first.

```
========================================================================================
PART 5: THE DROP GUARD™ AI SUBSYSTEM
========================================================================================
```
Drop Guard AI combines unsupervised anomaly detection, supervised risk classification, and explainable AI:
1. **Unsupervised Listing Fraud Detection (Isolation Forest):**
   - Whenever an employer submits a new listing in `routes/company.py: post_opportunity()`, the listing parameters are evaluated by `DropGuardEngine.assess_listing()`.
   - If `IsolationForest.predict(X) == -1`, the listing is flagged (`is_flagged = True`, `anomaly_score > 50`).
   - Flagged listings are quarantined from student searches until reviewed by an administrator.
2. **Supervised Disengagement Risk Assessment (Random Forest):**
   - When an administrator clicks "Run risk analysis now", `DropGuardEngine.assess_student()` evaluates all student profiles.
   - The Random Forest outputs a probability $P(	ext{disengaged})$.
   - Probability $\ge 66\%$ is labeled High Risk; $35	ext{--}65\%$ Medium Risk; $< 35\%$ Low Risk.
3. **Explainable AI via SHAP:**
   - SHAP TreeExplainer calculates the Shapley values for each feature.
   - The top 3 positive contributors are converted into plain English (e.g., *"Profile completeness increases risk"*, *"Stipend offered increases suspicion"*) and stored as JSON.

```
========================================================================================
PART 6: PRESENTATION TIER & JINJA2 TEMPLATES
========================================================================================
```
- **Modular Inheritance (`templates/base.html`):** Provides HTML5 boilerplate, navigation bars that dynamically render buttons depending on user role, and flash alert containers.
- **Form Feedback:** All POST forms validate input and flash color-coded feedback (green for success, red for validation errors).
- **Responsive Styling (`static/css/style.css`):** Built with CSS Grid, Flexbox, and CSS custom properties for sharp rendering across desktop browsers and mobile devices.

```
========================================================================================
PART 7: DISASTER RECOVERY & BACKUP AUTOMATION
========================================================================================
```
- **Automated Backup Batch Script (`backup_database.bat`):** Generates timestamped copies of `instance/app.db` in `backups/` (e.g. `internup_auto_20261102_204702.db`).
- **Sync & Restore Engine (`db_sync_backup.py`):** Enables one-click restoration of any backup file in the event of database corruption.
- **Public Tunneling (`RUN_ONLINE_CLOUDFLARE.bat`):** Launches `cloudflared.exe` to expose a secure public HTTPS URL for remote panel examination without port forwarding.

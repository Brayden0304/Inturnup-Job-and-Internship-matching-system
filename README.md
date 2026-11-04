# InternUp — Student Job & Internship Matching System

**Richfield Graduate Institute of Technology · IT Project**  
**Documentation updated: 4 November 2026**

InternUp is a Flask-based student employment and internship platform. It connects students with employers, supports profile and opportunity matching, and provides an administration interface with DropGuard™ fraud/risk tooling. The application can be used locally on a Windows PC or exposed temporarily to a phone or another device through a Cloudflare Quick Tunnel.

> **Scope of this update:** This README describes the current application and the interface/security fixes applied through the **“Sign In” heading update**. Updating this document does **not** modify application code, demo credentials, or database records.

---

## Features by role

### Students

- Create a student account and build an academic/career profile with qualification, field of study, skills, interests, location, experience, and bio.
- Import details by pasting their **own** CV/transcript text into the Quick Import section. Sample student presets have been removed from the visible profile form; new accounts should start without pre-filled demo profiles.
- Find opportunities, view match information, bookmark listings, and track applications.
- Explore career insights, skill information, and printable dossier features.

### Companies

- Register as a corporate partner using an email domain approved by the application.
- Maintain a company profile, publish opportunities, and review applications.
- Manage job requirements, stipends, and application status.

### Administrators

- Review users and postings and access DropGuard™ fraud/anomaly features.
- Quarantine and restore accounts. **Quarantined accounts cannot sign in**, and an already-signed-in user's access is revoked on their next server request. Restored users must sign in again.
- Review platform administration and audit/security information.

### Technology

| Area | Implementation |
| --- | --- |
| Backend | Python, Flask 3, Flask Blueprints |
| Frontend | HTML, CSS, JavaScript, Jinja2 templates |
| Accounts and sessions | Flask-Login, Werkzeug password hashing |
| Database | SQLite at `instance/app.db` (Flask-SQLAlchemy) |
| Machine learning | scikit-learn, SHAP, pre-trained models in `ml/saved_models/` |
| Remote testing | Cloudflare Quick Tunnel (`cloudflared`) |

Python **3.12** is recommended for the pinned package versions in `requirements.txt`.

---

## Windows installation — using `py`

**Run these commands in Command Prompt (CMD)** from the extracted project directory containing `app.py`, `requirements.txt` and `run_cloudflare.py`.

### First time on this computer

1. Extract the ZIP and open the folder `InternUp_Fixed`.
2. In File Explorer, click the address bar, type `cmd`, and press Enter.
3. Create and activate the virtual environment:

   ```cmd
   py -3.12 -m venv venv
   venv\Scripts\activate
   ```

4. Install the project dependencies:

   ```cmd
   py -m pip install -r requirements.txt
   ```

5. Start InternUp online, with a temporary Cloudflare URL:

   ```cmd
   py run_cloudflare.py
   ```

   The terminal prints a URL ending in `.trycloudflare.com`. Open it on a phone or laptop. **Leave CMD open while the site is in use.** The public link is temporary and can change when you restart the tunnel.

### Next time you want to start InternUp

Open CMD in the project directory and run:

```cmd
venv\Scripts\activate
py run_cloudflare.py
```

### Run locally, without Cloudflare

```cmd
venv\Scripts\activate
py app.py
```

Open **http://127.0.0.1:5000** on the same computer.

### Optional Windows launchers

- `SETUP_NEW_DEVICE.bat`: performs initial setup on a new PC; verify what it will do before running it, especially if you already have application data.
- `run_local.bat`: runs the local server.
- `RUN_ONLINE_CLOUDFLARE.bat`: launches the Cloudflare tunnel after `venv` exists.
- `backup_database.bat` and `manage_database.bat`: database backup/restore tools.

**Note about `py`:** This project uses the Windows Python launcher (`py`) in the commands above. After `venv\Scripts\activate`, an unqualified `py` should select that environment. If `py -3.12` is not found, check installed versions with `py --list` and install Python 3.12 rather than assuming `python` works in CMD.

**If you see `The system cannot find the path specified` after `venv\Scripts\activate`:** the `venv` folder has not been created in your current project directory. Run `py -3.12 -m venv venv` there first.

---

## Demo logins (original sample data)

These are demonstration accounts created by the project's `seed.py`, not credentials for a production deployment. All entries below were retained from the original project.

| Role | Name / organisation | Email | Password |
| --- | --- | --- | --- |
| Admin | Administrator | `admin@internup.ac.za` | `Admin@123` |
| Admin | Administrator | `admin@launchpad.local` | `Admin@123` |
| Student | Thabo Nkosi | `thabo@student.com` | `Student@123` |
| Student | Ayanda Mthembu | `ayanda@student.com` | `Student@123` |
| Student | Sipho Khumalo | `sipho@student.com` | `Student@123` |
| Student | Chloe van der Merwe | `chloe@student.com` | `Student@123` |
| Student | Lerato Dlamini | `lerato@student.com` | `Student@123` |
| Company | Standard Bank | `standardbank@company.com` | `Company@123` |
| Company | Discovery | `discovery@company.com` | `Company@123` |
| Company | Sasol | `sasol@company.com` | `Company@123` |
| Company | Deloitte | `deloitte@company.com` | `Company@123` |
| Company | Bowmans | `bowmans@company.com` | `Company@123` |
| Company | QuickCash (fraud/anomaly demonstration) | `quickcash@company.com` | `Company@123` |

> The ZIP includes `instance/app.db`. These seed credentials work if the corresponding records and passwords in the active database have not been changed or quarantined. **Do not run `seed.py` to fix a routine login problem:** reseeding can overwrite demonstration/application data, depending on how the script is implemented. Back up the database first.

---

## Registration rules and email validation

- Student and company registrations are separate, with role-specific labels and a responsive layout.
- The form and Flask backend check email syntax and use an **exact approved-domain list** for new registrations.
- Examples of approved email providers include `gmail.com` and `outlook.com`. Approved institutional and corporate domains are listed in `APPROVED_REGISTRATION_EMAIL_DOMAINS` in `utils.py`; this version includes **`wbho.co.za`**.
- Domains not on that list, including `5.com` and `lmao.cm`, are not approved for new registration. A company with another legitimate domain must have its exact domain reviewed and added to the list before it can self-register.
- Existing registered/demo users are retained; tightening new-registration rules does not automatically change their saved email addresses or passwords.
- **Important limitation:** an approved domain is **not** proof that the specific mailbox exists or is owned by the registrant. Email ownership verification would require a confirmation email or equivalent mechanism. This application does not claim to implement that confirmation process.

---

## Recent fixes — 4 November 2026

### Registration and profile

- Redesigned the mobile registration card to align with the home-page styling; the heading changes between **“Register As A Student”** and **“Register Your Company.”**
- Updated name, password and email validation messages; added backend validation in addition to browser checks.
- Removed built-in example profile preset buttons/content from the visible CV-import section, so a new student should not have another student's sample profile pre-filled. Existing students continue to see their own saved profile information.
- Made student-profile help text fit mobile screens and appear near the **ⓘ** icon when tapped—above the icon when space allows, with a nearby fallback position.

### Navigation and mobile display

- Simplified the sign-in page heading from **“Portal Sign In”** to **“Sign In.”**
- Removed the homepage **“Verified Competencies”** and **“Algorithmic Precision”** bullet points.
- Reordered the mobile footer to stack links vertically, including **Universities** under **Salaries & Stipends**, **Admin Portal** under **DropGuard™ Intelligence**, and **Help & Support** under **About InternUp**.
- Refined dashboard navigation: notification bell placement, avatar positioning, profile initials based on first and last name, and removal of the redundant displayed name / Install App header control.

### Security and appearance

- Updated account quarantine handling to block new sign-ins and invalidate sessions when an admin disables an account; a restored user must sign in again.
- Scoped dark-mode selection to the signed-in user in the current browser tab, with a light-mode reset on logout, rather than allowing a browser-wide theme preference to carry over to another account.
- Preserved the original demo seed data and database during the application-fix updates.

### Documentation update

- Brought this README up to date with the current feature behavior, demo accounts, approved-domain policy and Windows `py` startup procedure.
- **No application logic, assets, database records, or passwords were changed in the README-only update.**

---

## Database safety and backups

- The working database is **`instance/app.db`**; it contains existing users, applications and other records.
- The application includes backup utilities and periodic backup logic (`periodic_backup.py`, `db_sync_backup.py` and `backups/`).
- **Before replacing an existing project with a full ZIP, back up `instance/app.db`.** A full ZIP may include an older copy of the database and overwrite users registered after that ZIP was created.
- For code or documentation-only fixes, copy just the relevant files rather than replacing the whole application/database.
- Do not publish the demonstration credentials or expose the demo server as a permanent production site. A Cloudflare Quick Tunnel makes the running test site publicly reachable while it is active.

---

## Main project structure

```text
InternUp_Fixed/
├── app.py                         # Flask entry point
├── config.py                      # Application configuration
├── extensions.py                  # Shared Flask extensions
├── models.py                      # Database models and account status
├── routes/                        # main, auth, student, company and admin
├── templates/                     # Jinja2 pages and forms
├── static/                        # CSS, JavaScript, icons and PWA files
├── ml/                            # CV parser and fraud/risk models
├── instance/app.db                # Existing SQLite database
├── backups/                       # Stored database backup snapshots
├── seed.py                        # Demo database seed script
├── requirements.txt               # Python dependencies
├── run_cloudflare.py              # Cloudflare Quick Tunnel startup
├── RUN_ONLINE_CLOUDFLARE.bat      # Windows online launcher
├── run_local.bat                  # Windows local launcher
├── HOW_TO_RUN.md                  # Additional launch / backup guide
└── README.md                      # This document
```

For more background, see `HOW_TO_RUN.md`, `CLOUDFLARE_SETUP_GUIDE.md`, and the materials in `documentation/`. Some older supporting documents may use earlier UI wording; this README is the updated guide for the current ZIP.

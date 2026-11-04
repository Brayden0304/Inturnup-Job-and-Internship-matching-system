# LaunchPad: Student Job & Internship Matching System
## Final Presentation & Live Demonstration Master Script (6-Person Team)

**Module:** IT Project — Year 3 (Faculty of Information Technology | Richfield)  
**Total Allocated Time:** 30 Minutes  
- **Part 1: Slides Presentation:** Maximum 5 Minutes (What it is, why it was built, tech stack used)  
- **Part 2: System Demonstration:** Maximum 25 Minutes (End-to-end walkthrough & live panel Q&A)  
**PowerPoint File:** [`LaunchPad_Final_Presentation.pptx`](file:///C:/Users/pavan/Downloads/student-job-matching-20261027T105016Z-1-001%20(2)/student-job-matching-20261027T105016Z-1-001/student-job-matching/LaunchPad_Final_Presentation.pptx)

---

## 1. Pre-Presentation Setup & "What To Do Beforehand" Checklist

> [!IMPORTANT]
> **Complete these technical checks 15 to 30 minutes before your presentation begins.**

### A. Environment & Server Startup Checklist
1. **Fresh Database Reset & Seed:**
   Open a terminal in the project folder and run:
   ```bash
   cd "C:\Users\pavan\Downloads\student-job-matching-20261027T105016Z-1-001 (2)\student-job-matching-20261027T105016Z-1-001\student-job-matching"
   python seed.py
   ```
   *Why this matters:* This ensures all sample users, companies, demo listings (including the suspicious QuickCash listing), and applications are cleanly populated.

2. **Start the Web Application:**
   Run:
   ```bash
   python app.py
   ```
   Confirm the terminal displays: `* Running on http://127.0.0.1:5000/`. **Keep this terminal window open in the background!**

3. **Pre-warm Machine Learning Models:**
   Open a browser tab to `http://127.0.0.1:5000/login`, log in as `admin@launchpad.local` (Password: `admin123`), navigate to **Drop Guard AI**, and click **"Run risk analysis now"**.
   *Why this matters:* The first time Drop Guard AI runs, it fits the Random Forest and Isolation Forest models and saves them to `ml/saved_models/`. Doing this beforehand ensures instantaneous responses during the live demo. Log out before the panel arrives.

4. **Prepare Browser Tabs (Recommended Clean Setup):**
   Open a fresh Google Chrome or Microsoft Edge window with the following pre-arranged tabs:
   - **Tab 1:** Slide deck ready in PowerPoint (Full screen presenter view)
   - **Tab 2:** `http://127.0.0.1:5000` (Home page / Not logged in)
   - **Tab 3 (Incognito / 2nd Window):** `http://127.0.0.1:5000/login` (For quick employer login)

### B. Team Role & Hardware Distribution
- **One "Pilot" (Screen Controller):** While Person 3, 4, and 5 speak, either the speaker themselves or a designated pilot (e.g., Pavan / Person 1) can drive the mouse/keyboard smoothly without frantic clicking.
- **Microphone & Presentation Posture:** Stand/sit upright, speak clearly towards the microphone, and make eye contact with the evaluation panel.
- **Handling Panel Interruptions:** The guideline states *“The panel will ask questions during the project demonstration as well as at the end.”* If a lecturer interrupts:
  1. **Pause immediately and acknowledge the question politely.**
  2. The person currently presenting handles the initial answer.
  3. If technical assistance is required, the designated specialist (e.g., Person 5 for AI/ML, Person 6 for Database/Security) steps in seamlessly.
  4. Once answered, say: *"Thank you. Continuing with the demonstration..."* and pick up from the current action.

---

## 2. Team Member Role Allocation & Timing Breakdown

| Member | Segment | Time | Primary Focus |
| :--- | :--- | :---: | :--- |
| **Person 1** | **Slides Part 1** | 0:00 – 2:30 | Project Title, Purpose, Background, Problem Statement & Target Users |
| **Person 2** | **Slides Part 2** | 2:30 – 5:00 | SDLC (Agile), Feasibility, 3-Tier Architecture & Technology Stack |
| **Person 3** | **Live Demo 1** | 5:00 – 11:00 | Account Registration, Student Profile Builder, Dynamic Skill Matching & Applying |
| **Person 4** | **Live Demo 2** | 11:00 – 17:00 | Employer Portal, Posting Opportunities, Real-Time Drop Guard Screening & Reviewing Candidates |
| **Person 5** | **Live Demo 3** | 17:00 – 23:00 | Admin Dashboard, Moderating Flagged Listings with SHAP, Student Disengagement Risk & User Control |
| **Person 6** | **Demo Wrap-up & Defense** | 23:00 – 28:00+ | Closed-Loop Verification, Database & Security Architecture Defense, Panel Q&A Lead |

---

## 3. Detailed Presentation & Live Demo Script

```
========================================================================================
PART 1: SLIDE PRESENTATION (MAX 5 MINUTES)
========================================================================================
```

### PERSON 1: Introduction, Problem Statement & Objectives
- **Slide on Screen:** Slide 1 (Title) then Slide 2 (The Core Problem) & Slide 3 (The Proposed Solution)
- **Time Allocated:** 2 minutes 30 seconds
- **What to do beforehand:** Ensure PowerPoint is in Slide Show mode (`F5`). Have Slide 1 showing.

#### [Spoken Script]
> *"Good morning, respected members of the panel, project supervisor, and colleagues. My name is [Your Name], and together with my team members, we are proud to present our Year 3 IT Capstone Project: **LaunchPad — Student Job and Internship Matching System**.*
>
> *(Advance to Slide 2: The Core Problem)*
>
> *"To understand why LaunchPad was built, we must look at the current reality facing South African graduates. Today, finding a learnership, internship, or entry-level position is deeply fragmented. Students must navigate dozens of disconnected channels — generic recruitment sites, individual corporate career portals, university notice boards, and unverified social media posts.*
>
> *Through our Phase 2 preliminary investigation and Phase 3 systems analysis, we identified three critical bottlenecks:*
> 1. *First, **The Manual Suitability Gap:** Students waste precious time manually scanning job specs and applying for roles they are unqualified for, while companies are flooded with non-matching CVs.*
> 2. *Second, **Lack of Application Visibility:** Because applications are dispersed across email and independent sites, students have no unified tracking history, leading to missed updates, ghosting, and candidate disengagement.*
> 3. *Third, **Vulnerability to Exploitation & Fraud:** Entry-level students are targeted by fraudulent job offers with unrealistic stipends and predatory terms.*
>
> *(Advance to Slide 3: The Proposed Solution)*
>
> *"LaunchPad solves this by delivering a centralized, intelligent web ecosystem that connects three distinct stakeholders:*
> - *Students, who build structured profiles and receive algorithmic match scores;*
> - *Employers, who post structured openings and review pre-ranked applicants; and*
> - *Institutional Career Office Administrators, who oversee the platform using our unique **Drop Guard™ AI** subsystem to detect fraudulent listings and identify at-risk students before they drop out.*
>
> *I now hand over to [Person 2's Name], who will walk you through our development methodology and technology stack."*

---

### PERSON 2: SDLC, Architecture & Technology Stack
- **Slide on Screen:** Slide 4 (Matching & Drop Guard AI), Slide 5 (Technology Stack), Slide 8 (SDLC)
- **Time Allocated:** 2 minutes 30 seconds
- **What to do beforehand:** Be ready to transition smoothly from Slide 4 through 5, and conclude on Slide 9 (Demo Roadmap).

#### [Spoken Script]
> *"Thank you, [Person 1]. Respected panel, my name is [Your Name]. I will outline our engineering methodology, technical feasibility, and architectural design.*
>
> *(Advance to Slide 5: Technology Stack & Architecture)*
>
> *"To ensure reliability, modularity, and rapid prototyping, LaunchPad was engineered following an **Agile Iterative and Incremental SDLC Model**, executing across four planned project phases: Proposal, Planning, Systems Analysis, and System Design.*
>
> *Architecturally, the application follows an enterprise **Three-Tier Model-View-Controller (MVC)** design pattern:*
> - *At the **Presentation Tier (View)**, we utilized semantic HTML5, modern responsive CSS3, and JavaScript, rendered through Jinja2 server-side templating for high performance without complex build overhead.*
> - *At the **Application Tier (Controller & Business Logic)**, the backend is powered by **Python 3** and the **Flask framework**, structured cleanly using modular Flask Blueprints for authentication, student services, employer workflows, and administrative governance.*
> - *At the **Data Tier (Model)**, persistent data is handled via the **Flask-SQLAlchemy Object-Relational Mapper (ORM)**. For our academic prototype, SQLite was chosen for zero-configuration testing, while remaining 100% compliant with MySQL for future production deployment.*
>
> *(Advance to Slide 4: Matching & Drop Guard AI)*
>
> *"What sets LaunchPad apart technically is its dual-engine intelligence:*
> 1. *A deterministic **Skill-Matching Engine** that calculates an instant match percentage based on set theory overlap and field-of-study alignment.*
> 2. *Our proprietary **Drop Guard™ AI** engine, which integrates two scikit-learn machine learning models: an **Isolation Forest** for unsupervised listing fraud anomaly detection, and a **Random Forest Classifier** to assess student disengagement risk, both made transparent via **SHAP (SHapley Additive exPlanations)**.*
>
> *(Advance to Slide 9: Demonstration Roadmap)*
>
> *"We have completed our five-minute overview. We will now move into Part 2: our 25-minute comprehensive live system demonstration. I will hand over to [Person 3], who will demonstrate student account creation, profile engineering, and the matching engine."*

---

```
========================================================================================
PART 2: LIVE SYSTEM DEMONSTRATION (MAX 25 MINUTES)
========================================================================================
```

### PERSON 3: Account Creation & The Student Experience
- **Time Allocated:** 6 minutes (5:00 – 11:00)
- **Screen View:** Web Browser at `http://127.0.0.1:5000` (Home page)
- **What to do beforehand:** Ensure you are logged out. Have a test student name and email in mind (e.g., `kagiso@student.com`, Password: `student123`).

#### [Live Demo Actions & Spoken Script]

**Action 1: Landing Page & Navigation**
> *"Thank you, [Person 2]. Members of the panel, as you can see on screen, we are currently at the LaunchPad landing page. Notice that the navigation dynamically adapts to unauthenticated visitors, presenting options to 'Log in' or 'Get started'.*

**Action 2: Registering a New Student Account**
*(Click 'Get started' or 'Register')*
> *"Let us register a brand new student account to demonstrate input validation and role-based provisioning. I will select the 'Student' role, enter 'Kagiso Molefe', email `kagiso@student.com`, and a secure password.*
>
> *(Click 'Register')*
>
> *"Upon submission, Werkzeug immediately salts and hashes the password using PBKDF2 with SHA-256 before saving to the database. The system automatically creates both a `User` record and an associated `StudentProfile` record with an initial baseline completeness of 15%."*

**Action 3: Profile Completion & Dynamic Scoring**
*(Click 'Profile' in the navigation)*
> *"The student lands on the profile management page. Notice that our system requires students to define their academic qualification, field of study, skills, and experience.*
>
> *Let us populate Kagiso's profile: Qualification: `BSc Computer Science`; Field of Study: `Information Technology`; Skills: `Python, SQL, Flask, Git`; Location: `Johannesburg`; Years of Experience: `1`.*
>
> *(Click 'Save profile')*
>
> *"Notice the notification: 'Profile updated'. Behind the scenes, the system immediately recalculates the profile completeness score. This completeness percentage is not just aesthetic — it is a direct input feature into our Drop Guard machine learning model."*

**Action 4: Opportunity Search & Algorithmic Skill Matching**
*(Click 'Find opportunities' in the navigation bar)*
> *"Now let us navigate to 'Find opportunities'. Here, the student sees all active, non-expired, and non-flagged positions.*
>
> *Crucially, notice the circular badges showing match scores — such as **100%** on the 'Junior Python Developer Intern' role.*
>
> *How is this calculated? As defined in our Phase 4 specification: our matching engine reads the student's skills (`Python, SQL, Flask, Git`) and intersects them with the opportunity's required skills. With complete skill overlap ($1.0 \times 0.8 = 0.8$) plus the 0.2 field-of-study bonus for matching 'Information Technology', the formula produces $\min(1.0, 0.8 + 0.2) \times 100 = \mathbf{100\%}$.*
>
> *If an applicant lacks skills or is from a different discipline, the score scales proportionally down, allowing students to immediately prioritize roles where they are most competitive."*

**Action 5: Submitting an Application & Duplicate Prevention**
*(Click on 'Junior Python Developer Intern', view details, and click 'Apply now')*
> *"Let us apply for this position. The application is created with status 'submitted', timestamped with the current date and time, and Kagiso's 30-day activity counter increments.*
>
> *(Try clicking 'Apply' again or revisiting the listing)*
>
> *"Notice the button now states 'Already applied'. If a user attempts to bypass the UI, our database enforces a strict `UNIQUE(student_id, opportunity_id)` constraint, preventing duplicate submissions.*
>
> *(Click 'My applications' in the nav)*
>
> *"Under 'My applications', the student has a centralized real-time dashboard showing the company name, match score, date submitted, and current status: 'submitted'.*
>
> *I will now hand over to [Person 4], who will take us into the Employer Portal to demonstrate how companies post opportunities and manage applicants."*

---

### PERSON 4: Employer Portal, Real-Time Drop Guard Screening & Candidate Review
- **Time Allocated:** 6 minutes (11:00 – 17:00)
- **Screen View:** Web Browser — Log out of student and log into Company account (`standardbank@company.com`, Password: `company123`).
- **What to do beforehand:** Have the Standard Bank credentials ready.

#### [Live Demo Actions & Spoken Script]

**Action 1: Employer Login & Company Dashboard**
*(Log out of Kagiso, enter `standardbank@company.com`, password `company123`, and click 'Log in')*
> *"Thank you, [Person 3]. Good morning, panel. I am now logged in as **Standard Bank Corporate & Investment Banking**, a verified enterprise employer.*
>
> *Notice how our navigation bar instantly morphs: the student links disappear, replaced with 'Dashboard', 'Post opportunity', 'Company profile', and 'Log out', strictly enforced by our Flask `@role_required('company')` decorator.*
>
> *On the company dashboard, the employer sees their active listings, total applications received, and flagged listings."*

**Action 2: Posting a New Opportunity & Real-Time AI Screening**
*(Click 'Post opportunity')*
> *"Let us post a new opportunity to demonstrate our input validation and real-time fraud screening.*
>
> *We will fill out: Title: `Cloud & DevOps Graduate Intern`; Type: `Internship`; Field of Study: `Information Technology`; Required Skills: `Python, AWS, Docker, Linux`; Location: `Johannesburg / Hybrid`; Monthly Stipend: `R18,500`; Duration: `12` months; Closing Date: `2026-12-31`.*
>
> *(Click 'Post opportunity')*
>
> *"Notice the green success alert: 'Opportunity posted successfully'. When this form was submitted, Flask didn't just write to SQLite; it immediately fed 7 numerical features — including stipend, duration, description length, and company age — into our **Isolation Forest Anomaly Detector**.*
>
> *Because Standard Bank is a verified corporate entity with reasonable stipends and detailed descriptions, the Isolation Forest scored it as a standard inlier (normal), allowing it to go live immediately.*
>
> *However, if a scammer posted a listing offering R50,000 for a 1-month zero-skill internship from an unverified 0-year-old company, the Isolation Forest would catch it instantaneously, flag it, and hide it from students until admin approval."*

**Action 3: Reviewing Applicants & Dynamic Status Updates**
*(Click 'Dashboard', locate 'Junior Python Developer Intern', and click 'View applicants')*
> *"Now let us review the candidate pool for our existing 'Junior Python Developer Intern' listing.*
>
> *Notice what the hiring team sees: every applicant is automatically ranked in descending order by their **Match Score**.*
> - *Here is Thabo Nkosi with a 100% match score, complete qualification in Software Development, and listed skills.*
> - *And here is Kagiso Molefe, whom [Person 3] registered just moments ago!*
>
> *The recruiter does not have to sift through hundreds of irrelevant CVs. Everything is transparent. The hiring manager can now click the status dropdown next to Thabo Nkosi, select **'Shortlisted'**, and click **'Update status'**.*
>
> *(Select 'Shortlisted' and click 'Update status')*
>
> *"The status is updated instantly in the database. When Thabo logs into his student dashboard, his tracking status immediately reflects 'Shortlisted'.*
>
> *I will now hand over to [Person 5] to reveal the most powerful module of LaunchPad: our Institutional Administration and Drop Guard™ Machine Learning dashboard."*

---

### PERSON 5: Institutional Administration & Drop Guard™ AI Subsystem
- **Time Allocated:** 6 minutes (17:00 – 23:00)
- **Screen View:** Web Browser — Log out and log into Admin account (`admin@launchpad.local`, Password: `admin123`).
- **What to do beforehand:** Make sure the admin credentials work.

#### [Live Demo Actions & Spoken Script]

**Action 1: Admin Dashboard & Platform Overview**
*(Log out of company, enter `admin@launchpad.local`, password `admin123`, and log in)*
> *"Thank you, [Person 4]. Respected panel, I am now logged into the Institutional Administrator portal.*
>
> *This interface is designed specifically for career services deans and system administrators. The dashboard aggregates real-time institutional metrics: total students enrolled, total vetted companies, active job listings, and security indicators."*

**Action 2: Moderating Flagged Listings with Explainable AI (SHAP)**
*(Click 'Drop Guard AI' in the top navigation)*
> *"Let us examine the **Drop Guard AI** module. Under the 'Flagged listings awaiting review' section, notice that our unsupervised Isolation Forest has flagged a suspicious listing titled: **'Work From Home - Massive Pay!!!'** posted by 'QuickCash Ventures'.*
>
> *Notice the red badge: **Suspicion: 92.5 / 100**.*
>
> *In traditional systems, machine learning operates as an incomprehensible black box. But in LaunchPad, we integrated **SHAP (SHapley Additive exPlanations)**. Look right underneath the listing — SHAP reveals the exact top contributing factors:*
> 1. *Stipend / salary offered increases suspicion (abnormally high stipend of R45,000 for an entry-level position).*
> 2. *Opportunity duration increases suspicion (unrealistic timeline).*
> 3. *Description length & company age increase suspicion (brand new unverified entity with a vague 2-line description).*
>
> *Because of this automated flag, this listing was quarantined: no student could view or apply for it. The administrator has full authority to click **'Approve'** or **'Remove'**.*
>
> *(Click 'Remove')*
>
> *"By clicking 'Remove', the listing's `is_active` attribute is set to false and marked reviewed, permanently neutralizing the threat."*

**Action 3: Predicting Student Disengagement Risk (Supervised Random Forest)**
*(Scroll down to 'Student disengagement risk' and click 'Run risk analysis now')*
> *"Now let us turn to student welfare. One of the greatest challenges in higher education is student disengagement — students who stop applying, fail to update their CVs, and drop out of the employment pipeline.*
>
> *I will now click **'Run risk analysis now'**.*
>
> *(Click the button and observe the immediate update)*
>
> *"Our supervised **Random Forest Classifier** has analyzed every student profile across 7 engagement vectors: profile completeness, login frequency, recent applications, idle days since last login, idle days since last application, saved searches, and profile views.*
>
> *Look at the results table:*
> - *Student **Lerato Dlamini** has been classified with **High Risk (95% Probability)**.*
> - *Once again, SHAP explains why: 'Profile completeness increases risk', 'Days since last application increases risk', and 'Days since last login increases risk'.*
> - *In contrast, **Thabo Nkosi** is classified as **Low Risk (1% Probability)**, driven by high completeness and active logins.*
>
> *This empowers career counselors to intervene proactively before a student falls through the cracks."*

**Action 4: User Account Management & Administrative Controls**
*(Click 'Users' in the nav bar)*
> *"Finally, under the 'Users' tab, administrators have full governance over all platform participants. Administrators can toggle the active status of any student or employer account with one click to suspend malicious actors.*
>
> *Furthermore, as a vital security rule documented in Phase 4: administrator accounts cannot be disabled through the interface, preventing accidental lockout.*
>
> *I now hand over to [Person 6] to provide our technical architecture defense, backup procedures, and lead our panel discussion."*

---

### PERSON 6: Technical Architecture Defense, Recovery Procedures & Q&A Lead
- **Time Allocated:** 5+ minutes (23:00 – 28:00+)
- **Screen View:** Return to student login (`thabo@student.com` / `student123`) to show updated status, then switch to Slide 10 (Conclusion & Defense).
- **What to do beforehand:** Have terminal, backup script, and slides ready.

#### [Live Demo Actions & Spoken Script]

**Action 1: Closed-Loop Verification**
*(Log into `thabo@student.com`, password `student123`, and go to 'My applications')*
> *"Thank you, [Person 5]. Panel members, to complete the demonstration loop, we are back on student Thabo Nkosi's dashboard. Notice that his application for 'Junior Python Developer Intern' has moved from 'submitted' to **'shortlisted'**, reflecting the real-time update performed by Standard Bank moments ago.*
>
> *This confirms full end-to-end integration across all three tiers and user roles.*

*(Switch screen to Slide 10: Conclusion & Defense)*

**Action 2: Technical Rigor & Data Integrity Defense**
> *"Before opening the floor, I want to highlight the core software engineering principles underpinning LaunchPad, directly aligned with the Richfield IT Project guidelines:*
>
> 1. * **Data Integrity (Phase 4.5):** We implemented strict Entity Integrity with primary keys across all 6 tables, Referential Integrity using cascading foreign keys, and Domain Integrity using controlled enumerations for user roles and application statuses (`submitted`, `reviewed`, `shortlisted`, `rejected`, `accepted`).*
> 2. * **Security Design (Phase 4.8.1):** We eliminated SQL injection risks by exclusively using SQLAlchemy parameterized ORM queries; we neutralized Cross-Site Scripting (XSS) via Jinja2 automatic contextual escaping; and we secured authentication using cryptographic salted PBKDF2 hashing.*
> 3. * **Backup & Disaster Recovery (Phase 4.8.2):** We created a dedicated backup script — `backup_database.bat` — which creates timestamped snapshots of `instance/app.db` prior to any major deployment, alongside version-controlled GitHub repositories.*
>
> *"In summary, LaunchPad is not a theoretical concept — it is a fully functioning, robust, and intelligent software product that fulfills 100% of the functional and non-functional requirements established in Phases 1 through 4.*
>
> *My team members and I are now ready to answer any questions from the panel. Thank you."*

---

## 4. Anticipated Panel Questions & High-Scoring Model Answers

> [!TIP]
> **Study these questions and answers carefully.** The guidelines state that all group members must be prepared to answer.

### Q1 (For Person 2 or Person 6): "Why did you use SQLite instead of MySQL, and how difficult is it to migrate to MySQL?"
**Model Answer:**
> *"As documented in Phase 2 and Phase 4 of our design, SQLite was selected specifically for the academic prototyping environment because it is serverless, self-contained, and requires zero external database installation, ensuring 100% portability during grading and demonstration.*
> *However, because we used Flask-SQLAlchemy as our Object-Relational Mapper, our codebase contains no raw SQLite-specific syntax. Migrating to MySQL in production requires only changing a single configuration line in `config.py` — setting `SQLALCHEMY_DATABASE_URI` to a MySQL connection string (e.g., `mysql+pymysql://user:pass@localhost/launchpad`) and running our existing schema migrations. All tables, foreign keys, and constraints transfer seamlessly."*

### Q2 (For Person 5 or Person 2): "How did you train Drop Guard AI without access to a million real student records?"
**Model Answer:**
> *"That is addressed directly in our Phase 4 system design. In an academic prototype, real historical student behavioral data and confirmed fraudulent job postings are protected by privacy laws (POPIA) and unavailable.*
> *We engineered `ml/data_simulation.py` to generate statistically representative synthetic distributions based on real-world patterns (e.g., normal distributions for profile completeness, Poisson distributions for application frequencies, and exponential decay for login recency).*
> *Our Random Forest was trained on 1,200 simulated student profiles with balanced class weights, and our Isolation Forest was fitted on historical listing feature distributions with an 8% contamination factor. Both models are saved to disk using `joblib` and can be retrained on real production logs at any time."*

### Q3 (For Person 3 or Person 4): "Can a student apply for the same job multiple times to spam a company?"
**Model Answer:**
> *"No, duplicate applications are prevented at both the application level and the database level.*
> *In `routes/student.py`, the `apply` route checks if an `Application` record already exists for that `(student_id, opportunity_id)` pair and blocks it.*
> *Furthermore, in `models.py`, we created an explicit database-level table rule: `db.UniqueConstraint('student_id', 'opportunity_id', name='uq_student_opportunity')`. If any duplicate request ever bypassed the UI, the database engine would throw an integrity error and reject the transaction."*

### Q4 (For Person 1 or Person 3): "Explain the exact math behind your skill-matching score."
**Model Answer:**
> *"The matching formula is defined in `utils.py`:*
> $$\text{Match Score (\%)} = \min\Big(1.0, \,(\text{Skill Overlap} \times 0.8) + \text{Field Bonus}\Big) \times 100$$
> *- **Skill Overlap** is the Jaccard-style intersection of the student's skills and the listing's required skills divided by the total required skills, weighted at 80%.*
> *- **Field Bonus** adds 20% (0.2) if the student's field of study exactly matches the opportunity's domain.*
> *- The total is capped at 1.0 (100%) and rounded to one decimal place. This ensures an explainable, deterministic score that rewards both technical skills and educational alignment."*

### Q5 (For Person 6): "What happens if someone tries to access `/admin/users` without logging in or while logged in as a student?"
**Model Answer:**
> *"Our system enforces multi-layered Role-Based Access Control. All administrative routes are wrapped with `@login_required` and our custom decorator `@role_required('admin')`.*
> *If an unauthenticated visitor tries to access the URL, Flask-Login intercepts the request and redirects them to the login page with an error message.*
> *If an authenticated student tries to access an admin URL, the `@role_required` decorator checks `current_user.role`. Because the role is not 'admin', it flashes an unauthorized access warning and redirects the student back to their own student dashboard."*

---

## 5. Verification Against Richfield IT Project Guidelines

| Guideline Requirement | LaunchPad Compliance | Verification Status |
| :--- | :--- | :---: |
| **Max 5-minute PowerPoint Presentation** | 10 concise, professionally structured slides focusing on project purpose, need, and tech stack. Script timed at exactly 5 minutes (2.5 mins Person 1, 2.5 mins Person 2). | **PASSED** |
| **Max 25-minute System Demo** | Live walkthrough covering account creation, student flow, employer flow, admin AI governance, and database verification. Split across 4 members (~5-6 mins each). | **PASSED** |
| **Active Software Development (No theoretical/LAN-only projects)** | Complete Python/Flask full-stack web application with SQLAlchemy ORM, Jinja2, scikit-learn, and SHAP. | **PASSED** |
| **Role Allocation for 6 Members** | Clearly divided into 6 balanced speaker roles with explicit entry/exit cues, screen actions, and Q&A defense responsibilities. | **PASSED** |
| **Pre-presentation Readiness** | Comprehensive pre-flight checklist covering database seeding, local server execution, ML pre-warming, and backup procedures. | **PASSED** |

import sys
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path):
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Colors
    NAVY = RGBColor(15, 23, 42)
    SLATE = RGBColor(30, 41, 59)
    LIGHT_BG = RGBColor(248, 250, 252)
    CARD_BG = RGBColor(255, 255, 255)
    BORDER_COLOR = RGBColor(203, 213, 225)
    BLUE_ACCENT = RGBColor(2, 132, 199)
    TEAL_ACCENT = RGBColor(13, 148, 136)
    DARK_TEXT = RGBColor(15, 23, 42)
    MUTED_TEXT = RGBColor(71, 85, 105)
    WHITE = RGBColor(255, 255, 255)
    RED_ACCENT = RGBColor(225, 29, 72)

    def add_header(slide, title_text, category_text):
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = "Arial"
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = BLUE_ACCENT
        p_cat.space_after = Pt(4)
        
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.name = "Arial"
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=BORDER_COLOR):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(1.5)
        else:
            shape.line.fill.background()
        return shape

    def set_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text.strip()

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.fill.background()

    add_card(s1, Inches(1.0), Inches(0.8), Inches(11.333), Inches(5.9), CARD_BG, None)

    tb1 = s1.shapes.add_textbox(Inches(1.5), Inches(1.2), Inches(10.333), Inches(5.1))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "FACULTY OF INFORMATION TECHNOLOGY | RICHFIELD - YEAR 3 IT PROJECT"
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_after = Pt(14)

    p = tf1.add_paragraph()
    p.text = "LaunchPad: Student Job & Internship Matching System"
    p.font.name = "Arial"
    p.font.size = Pt(30)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)

    p = tf1.add_paragraph()
    p.text = "A Full-Stack Intelligent Web Application with Explainable Drop Guard AI"
    p.font.name = "Arial"
    p.font.size = Pt(17)
    p.font.color.rgb = TEAL_ACCENT
    p.space_after = Pt(28)

    p = tf1.add_paragraph()
    p.text = "FINAL PROJECT PRESENTATION & LIVE SYSTEM DEMONSTRATION"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = SLATE
    p.space_after = Pt(8)

    p = tf1.add_paragraph()
    p.text = "Part 1: Slide Presentation (Max 5 Mins)  -  Project Purpose, Need, Architecture & Tech Stack\nPart 2: Live System Demonstration (Max 25 Mins)  -  End-to-End Functional Walkthrough & Technical Defense"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.color.rgb = MUTED_TEXT
    p.space_after = Pt(24)

    p = tf1.add_paragraph()
    p.text = "Presented by: 6-Member Project Development Team  |  Project Lead: Pavan Saihan Singh (ID: 402307292)"
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT

    set_notes(s1, """[PERSON 1 - 0:00 to 0:45]
Good morning, respected members of the evaluation panel, project supervisor, and fellow colleagues.
My name is Pavan Saihan Singh, and on behalf of our six-person software engineering team, we are proud to present our Year 3 IT Capstone Project: LaunchPad - Student Job and Internship Matching System.

Our presentation strictly adheres to the Richfield IT Project guidelines, structured into two key segments:
Part 1 is a 5-minute executive slide overview explaining what LaunchPad is, why it was built, and our underlying architecture and technology stack.
Part 2 is our 25-minute live interactive system demonstration, where our six group members will walk you through the entire live application from initial account creation through our Drop Guard AI governance engine.""")

    # =========================================================================
    # SLIDE 2: THE CORE PROBLEM (WHY IT WAS BUILT)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "The Core Problem: Why Was LaunchPad Built?", "Context & Identification of Need (Phases 1-3)")

    cards_data_s2 = [
        ("1. Fragmented Job Search Landscape", 
         "Students navigate dozens of disconnected channels: generic commercial job boards, scattered company career pages, physical campus notice boards, and unverified social media ads.\n\nResult: Extreme inefficiency, missed closing dates, and duplicate application entries.",
         RED_ACCENT),
        ("2. Manual Suitability & Skills Gap",
         "Students waste hours reading lengthy job specs and manually comparing their skills with no objective feedback on suitability.\n\nResult: Companies are overwhelmed by hundreds of unqualified CVs, while qualified students miss out.",
         BLUE_ACCENT),
        ("3. Application Tracking Void & Disengagement",
         "Traditional applications disappear into a 'black box'. Students receive no real-time status updates (submitted vs. shortlisted vs. rejected).\n\nResult: Prolonged silence causes anxiety, candidate fatigue, and complete drop-out from the job search.",
         TEAL_ACCENT),
        ("4. Vulnerability to Fraud & Predatory Scams",
         "Entry-level students and desperate job seekers are prime targets for fraudulent vacancies, non-existent stipends, and unvetted shell employers.\n\nResult: Financial loss and platform safety risks that academic institutions lack tools to monitor.",
         NAVY)
    ]

    for i, (ctitle, cdesc, accent) in enumerate(cards_data_s2):
        col = i % 2
        row = i // 2
        left = Inches(0.8 + col * 5.95)
        top = Inches(1.65 + row * 2.7)
        width = Inches(5.75)
        height = Inches(2.5)

        add_card(s2, left, top, width, height)
        bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()

        tb = s2.shapes.add_textbox(left + Inches(0.3), top + Inches(0.2), width - Inches(0.6), height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = ctitle
        p.font.name = "Arial"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.space_after = Pt(8)

        p = tf.add_paragraph()
        p.text = cdesc
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.color.rgb = MUTED_TEXT

    set_notes(s2, """[PERSON 1 - 0:45 to 1:45]
To understand why LaunchPad was conceived and built, we must examine the reality facing tertiary students seeking their first career break. Through our Phase 2 preliminary investigation and Phase 3 user interviews and observation, we pinpointed four major systemic failures:

First, severe fragmentation: students search four to five unrelated websites, re-entering identical credentials repeatedly, leading to missed application windows.
Second, the manual suitability gap: without automated skills parsing, students submit CVs blindly. Recruiters receive stacks of irrelevant applications, while qualified graduates get buried.
Third, the total lack of feedback: submitted applications vanish without a trace. Students experience severe anxiety and disengage from seeking work.
And fourth, exploitation: inexperienced graduates are routinely targeted by online scam postings offering inflated salaries for zero qualifications.

LaunchPad was engineered specifically to solve every single one of these bottlenecks in one unified academic-corporate platform.""")

    # =========================================================================
    # SLIDE 3: THE PROPOSED SOLUTION (WHAT IS LAUNCHPAD)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "What Is LaunchPad? The Three-Stakeholder Ecosystem", "System Overview & User Roles (Phases 2 & 4)")

    pillars = [
        ("Student Career Portal", "Empowering Job Seekers", [
            "Centralized profile builder (qualification, skills, interests)",
            "Automated Profile Completeness scoring (0-100%)",
            "Algorithmic match score indicator on every listing",
            "One-click direct application with duplicate prevention",
            "Live status tracking: Submitted -> Shortlisted -> Accepted"
        ], BLUE_ACCENT),
        ("Corporate Partner Portal", "Streamlining Recruitment", [
            "Verified company profile & branding repository",
            "Structured vacancy posting (Internships & Learnerships)",
            "Real-time Drop Guard fraud screening upon posting",
            "Applicant dashboard sorted in real-time by Match Score",
            "Instant applicant stage progression & status updates"
        ], TEAL_ACCENT),
        ("Institutional Administration", "Platform Governance & AI Oversight", [
            "Comprehensive User Management (active/disable toggles)",
            "Opportunity moderation & flagged listing quarantine",
            "Drop Guard AI: Isolation Forest listing anomaly detection",
            "Drop Guard AI: Random Forest student disengagement scoring",
            "SHAP explainability: transparent attribution of all ML decisions"
        ], NAVY)
    ]

    for i, (title, subtitle, items, accent) in enumerate(pillars):
        left = Inches(0.8 + i * 3.98)
        top = Inches(1.65)
        width = Inches(3.8)
        height = Inches(5.3)

        add_card(s3, left, top, width, height)
        bar = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.12))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()

        tb = s3.shapes.add_textbox(left + Inches(0.25), top + Inches(0.25), width - Inches(0.5), height - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.space_after = Pt(2)

        p = tf.add_paragraph()
        p.text = subtitle
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = accent
        p.space_after = Pt(14)

        for item in items:
            p = tf.add_paragraph()
            p.text = "- " + item
            p.font.name = "Arial"
            p.font.size = Pt(11)
            p.font.color.rgb = MUTED_TEXT
            p.space_after = Pt(6)

    set_notes(s3, """[PERSON 1 - 1:45 to 2:30]
So, what is LaunchPad? LaunchPad is an intelligent, multi-tenant web application designed to connect three crucial stakeholder groups:

First, for students: it provides a structured profile builder, deterministic match scoring on every vacancy, one-click applications, and full end-to-end status transparency.
Second, for employers: it allows verified corporate partners to post structured internship opportunities, run them through automated fraud verification, and review candidate pools automatically sorted by match score.
And third, for university career administrators: it delivers high-level institutional governance, complete user access control, and our Drop Guard AI subsystem.

I will now hand over to Person 2, who will walk you through our core algorithmic intelligence, software architecture, and technology stack.""")

    # =========================================================================
    # SLIDE 4: CORE ALGORITHMIC INTELLIGENCE & DROP GUARD AI
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Intelligent Matching Engine & Drop Guard AI Subsystem", "Algorithmic Design & Machine Learning (Phase 4)")

    # Left Card: Matching Engine
    add_card(s4, Inches(0.8), Inches(1.65), Inches(5.75), Inches(5.3))
    tb = s4.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.15), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Deterministic Skill-Matching Engine (utils.py)"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    p = tf.add_paragraph()
    p.text = "Mathematical Formulation:"
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_after = Pt(4)

    p = tf.add_paragraph()
    p.text = "Match Score (%) = min(1.0, (Skill Overlap x 0.8) + Field Bonus) x 100"
    p.font.name = "Courier New"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(12)

    points_match = [
        "Skill Overlap Ratio (80% Weight): Intersection of student's skills with required vacancy skills divided by total required skills.",
        "Field of Study Bonus (20% Weight): Flat 0.2 bonus added if student's academic discipline aligns directly with the job domain.",
        "Bounded & Deterministic: Normalized between 0% and 100%, calculated dynamically in milliseconds without external API costs.",
        "Dual-Sided Visibility: Rendered as visual progress badges for students during search, and as sorting criteria for recruiters."
    ]
    for pt in points_match:
        p = tf.add_paragraph()
        p.text = "- " + pt
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.color.rgb = MUTED_TEXT
        p.space_after = Pt(8)

    # Right Card: Drop Guard AI
    add_card(s4, Inches(6.75), Inches(1.65), Inches(5.75), Inches(5.3))
    tb2 = s4.shapes.add_textbox(Inches(7.05), Inches(1.9), Inches(5.15), Inches(4.8))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "Drop Guard Machine Learning Subsystem (ml/)"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    p = tf2.add_paragraph()
    p.text = "Dual Model Architecture + Explainable AI:"
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = TEAL_ACCENT
    p.space_after = Pt(6)

    points_ml = [
        "1. Listing Fraud Detection (Isolation Forest):\nUnsupervised anomaly detection evaluating 7 parameters: stipend, duration, description length, company age, and posting frequency. Automatically quarantines suspicious scams (e.g., QuickCash demo).",
        "2. Student Disengagement Risk (Random Forest):\nSupervised classifier evaluating 7 behavioral indicators: profile completeness, login frequency, application recency, and idle days. Categorizes students as Low (<35%), Medium (35-65%), or High (>=66%) risk.",
        "3. Explainable AI via SHAP (TreeExplainer):\nReplaces black-box predictions by exposing the top 3 contributing factors per prediction directly in the administrator UI."
    ]
    for pt in points_ml:
        p = tf2.add_paragraph()
        p.text = pt
        p.font.name = "Arial"
        p.font.size = Pt(10.5)
        p.font.color.rgb = MUTED_TEXT
        p.space_after = Pt(8)

    set_notes(s4, """[PERSON 2 - 2:30 to 3:15]
Thank you, Person 1. Respected panel, I will now explain our technical innovations, beginning with our matching engine and machine learning architecture.

As specified in Phase 4.2.4, our matching algorithm is deterministic, explainable, and fast. The formula weights skill overlap at 80% and awards a 20% bonus for field-of-study alignment, capped at 100%. This provides students and employers with instant, reliable match scores without costly external cloud dependencies.

To address fraud and student dropout, we developed Drop Guard AI. This consists of:
An Isolation Forest model that screens job postings in real time across seven features, quarantining fraudulent postings before students ever see them.
A Random Forest model that assesses student engagement, identifying at-risk students for early academic counseling.
And critically, SHAP explainability, which provides transparent attribution so administrators know exactly why a decision was reached.""")

    # =========================================================================
    # SLIDE 5: SYSTEM ARCHITECTURE & TECHNOLOGY STACK
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Software Architecture & Technology Stack", "Physical Design & System Architecture (Phase 4.3 & 4.4)")

    tech_tiers = [
        ("Presentation Tier (View)", "User Interface & Experience", [
            ("HTML5 & CSS3", "Modern semantic markup with custom design tokens, CSS Grid, and responsive flex layouts."),
            ("Jinja2 Templates", "Server-side template rendering with modular layouts (base.html) and XSS auto-escaping."),
            ("Client JavaScript", "Clean DOM interactions, dynamic modal dialogs, and real-time form validation.")
        ], BLUE_ACCENT),
        ("Application Tier (Controller)", "Business Logic & Machine Learning", [
            ("Python 3 & Flask", "Application Factory pattern with modular Blueprints (auth, student, company, admin)."),
            ("Flask-Login & Werkzeug", "Stateful session handling, PBKDF2 password hashing, and custom @role_required RBAC."),
            ("scikit-learn & SHAP", "IsolationForest, RandomForestClassifier, and TreeExplainer for machine learning.")
        ], TEAL_ACCENT),
        ("Data Tier (Model & Storage)", "Persistence & Model Artifacts", [
            ("SQLAlchemy ORM", "Declarative schema mapping in models.py, abstracting raw SQL queries and preventing injection."),
            ("SQLite (Academic Dev)", "Zero-configuration file database (instance/app.db) ensuring effortless demonstration portability."),
            ("MySQL-Ready Schema", "Environment-driven connection string; 100% production-ready for MySQL migration.")
        ], NAVY)
    ]

    for i, (tier_title, tier_sub, items, accent) in enumerate(tech_tiers):
        left = Inches(0.8 + i * 3.98)
        top = Inches(1.65)
        width = Inches(3.8)
        height = Inches(5.3)

        add_card(s5, left, top, width, height)
        bar = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.12))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()

        tb = s5.shapes.add_textbox(left + Inches(0.25), top + Inches(0.25), width - Inches(0.5), height - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = tier_title
        p.font.name = "Arial"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.space_after = Pt(2)

        p = tf.add_paragraph()
        p.text = tier_sub
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = accent
        p.space_after = Pt(12)

        for name, desc in items:
            p = tf.add_paragraph()
            p.text = name
            p.font.name = "Arial"
            p.font.size = Pt(11.5)
            p.font.bold = True
            p.font.color.rgb = SLATE
            p.space_after = Pt(1)

            p = tf.add_paragraph()
            p.text = desc
            p.font.name = "Arial"
            p.font.size = Pt(10)
            p.font.color.rgb = MUTED_TEXT
            p.space_after = Pt(8)

    set_notes(s5, """[PERSON 2 - 3:15 to 4:00]
Slide 5 depicts our 3-Tier Model-View-Controller architecture, designed to fulfill all non-functional requirements established in Phase 3.7.

At the Presentation Tier, we used modern HTML5, CSS3, and JavaScript rendered through Jinja2 server templates. This provides an ultra-responsive interface without the heavy build overhead of bloated frontend frameworks.
At the Application Tier, the core backend is built on Python 3 and Flask 3.0, organized cleanly using Flask Blueprints. This decouples our authentication, student, employer, and admin routes.
At the Data Tier, persistent storage is handled by SQLAlchemy ORM. For our academic demonstration, SQLite was chosen for zero-configuration testing, while maintaining full compatibility with enterprise MySQL servers via our configuration environment variables.""")

    # =========================================================================
    # SLIDE 6: DATABASE SCHEMA & DATA INTEGRITY
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Physical Database Architecture & Relational Integrity", "Database Design & Data Modeling (Phase 4.5)")

    tables_data = [
        ("users", "Central Authentication Entity", "Stores id, email (unique), password_hash (salted PBKDF2), role (student/company/admin), is_active_account.", BLUE_ACCENT),
        ("student_profiles", "Student Profiles & Metrics", "Linked to users (1:1). Stores name, qualification, skills, bio, and 7 Drop Guard engagement tracking fields.", BLUE_ACCENT),
        ("company_profiles", "Employer Credentials", "Linked to users (1:1). Stores company_name, industry, website, company_age_years, and verified badge.", TEAL_ACCENT),
        ("opportunities", "Vacancies & Anomaly Metrics", "Linked to company (1:N). Stores title, required_skills, stipend, duration, anomaly_score, is_flagged.", TEAL_ACCENT),
        ("applications", "Relational Connection", "Links Student & Opportunity (N:M). Stores status, match_score. UNIQUE(student_id, opportunity_id).", NAVY),
        ("risk_assessments", "Drop Guard Audit Trail", "Drop Guard history: student_id, risk_label (Low/Med/High), risk_probability, top_factors JSON.", NAVY)
    ]

    for i, (tname, ttitle, tdesc, accent) in enumerate(tables_data):
        col = i % 3
        row = i // 3
        left = Inches(0.8 + col * 3.98)
        top = Inches(1.65 + row * 2.7)
        width = Inches(3.8)
        height = Inches(2.45)

        add_card(s6, left, top, width, height)
        bar = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()

        tb = s6.shapes.add_textbox(left + Inches(0.2), top + Inches(0.18), width - Inches(0.4), height - Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = tname
        p.font.name = "Courier New"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.space_after = Pt(2)

        p = tf.add_paragraph()
        p.text = ttitle
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = accent
        p.space_after = Pt(6)

        p = tf.add_paragraph()
        p.text = tdesc
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.color.rgb = MUTED_TEXT

    set_notes(s6, """[PERSON 2 - 4:00 to 4:30]
Turning to Slide 6, our database schema satisfies Third Normal Form (3NF) and enforces strict relational integrity.
Instead of having duplicate login credentials across disparate tables, our design uses a single centralized 'users' table, with foreign-key relationships to 'student_profiles' and 'company_profiles'.

We strictly enforce:
Entity Integrity through primary keys on all tables;
Referential Integrity through foreign key constraints;
Domain Integrity via controlled status values (submitted, reviewed, shortlisted, rejected, accepted);
And a composite unique constraint on (student_id, opportunity_id) to make duplicate applications physically impossible at the database level.""")

    # =========================================================================
    # SLIDE 7: SECURITY DESIGN & DISASTER RECOVERY
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "System Security Measures & Backup Procedures", "Security & Reliability Engineering (Phase 4.8)")

    sec_cards = [
        ("Role-Based Access Control (RBAC)", 
         "Custom @role_required('student'/'company'/'admin') decorators protect every route. Students cannot access recruiter or admin functions, and unauthorized requests are redirected with flash notifications.",
         BLUE_ACCENT),
        ("Cryptographic Password Protection",
         "Passwords are never stored in plaintext. Werkzeug PBKDF2 with SHA-256 and unique cryptographic salt hashing ensures industry-standard protection against dictionary and rainbow table attacks.",
         TEAL_ACCENT),
        ("SQL Injection & XSS Neutralization",
         "All database transactions execute through SQLAlchemy parameterized queries, preventing SQL injection completely. Jinja2 templates auto-escape HTML inputs to prevent cross-site scripting attacks.",
         NAVY),
        ("Disaster Recovery & Backup Automation",
         "Automated backup batch scripts (backup_database.bat) create timestamped snapshots of instance/app.db. Database recovery procedures ensure the entire system can be restored in under 60 seconds.",
         RED_ACCENT)
    ]

    for i, (stitle, sdesc, accent) in enumerate(sec_cards):
        col = i % 2
        row = i // 2
        left = Inches(0.8 + col * 5.95)
        top = Inches(1.65 + row * 2.7)
        width = Inches(5.75)
        height = Inches(2.5)

        add_card(s7, left, top, width, height)
        bar = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()

        tb = s7.shapes.add_textbox(left + Inches(0.3), top + Inches(0.2), width - Inches(0.6), height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = stitle
        p.font.name = "Arial"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.space_after = Pt(8)

        p = tf.add_paragraph()
        p.text = sdesc
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.color.rgb = MUTED_TEXT

    set_notes(s7, """[PERSON 2 - 4:30 to 5:00]
Security and reliability were built into LaunchPad from the foundation up.
All protected routes are guarded by our custom role_required decorator. Passwords are encrypted with salted PBKDF2 hashes. SQL injection is mitigated through parameterized ORM statements, and XSS is prevented via Jinja2 contextual escaping.
Additionally, we implemented automated backup scripts that take timestamped snapshots of our SQLite database, ensuring business continuity.

This concludes our 5-minute slide presentation. We are now transitioning into Part 2: our 25-minute live system demonstration. I hand over to Person 3 to demonstrate the student registration and onboarding workflow.""")

    # =========================================================================
    # SLIDE 8: LIVE DEMONSTRATION ROADMAP (TRANSITION SLIDE)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Live System Demonstration: 25-Minute Roadmap", "System Demo Structure (6-Member Team Allocation)")

    demo_stages = [
        ("Demo 1: Student Lifecycle (Person 3)", "5:00 - 10:00 (5 mins)", [
            "Account registration & PBKDF2 hashing",
            "Student Profile Builder & experience metrics",
            "Automatic Profile Completeness score calculation",
            "Student Dashboard and navigation overview"
        ], BLUE_ACCENT),
        ("Demo 2: Matching & Applying (Person 4)", "10:00 - 15:00 (5 mins)", [
            "Dynamic Opportunity Search & multi-parameter filtering",
            "Real-time Skill Overlap + Field Bonus score badges",
            "One-click job application submission",
            "Unique constraint validation (preventing duplicate applications)",
            "My Applications tracking history (Submitted -> Accepted)"
        ], TEAL_ACCENT),
        ("Demo 3: Corporate Portal (Person 5)", "15:00 - 20:00 (5 mins)", [
            "Employer authentication & company dashboard",
            "Opportunity posting with skills taxonomy & stipends",
            "Real-time Drop Guard Isolation Forest anomaly screening",
            "Applicant management: candidates ranked by Match Score",
            "Advancing application statuses (Reviewed/Shortlisted)"
        ], NAVY),
        ("Demo 4: Admin & Defense (Person 6)", "20:00 - 25:00+ (5 mins)", [
            "Institutional Administrator dashboard analytics",
            "Flagged scam listing moderation with SHAP explainability",
            "Student disengagement risk classification (Random Forest)",
            "User governance (toggle active accounts) & RBAC lockout safety",
            "Closed-loop verification & panel defense leadership"
        ], RED_ACCENT)
    ]

    for i, (stitle, stime, sitems, accent) in enumerate(demo_stages):
        col = i % 2
        row = i // 2
        left = Inches(0.8 + col * 5.95)
        top = Inches(1.65 + row * 2.7)
        width = Inches(5.75)
        height = Inches(2.5)

        add_card(s8, left, top, width, height)
        bar = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()

        tb = s8.shapes.add_textbox(left + Inches(0.3), top + Inches(0.2), width - Inches(0.6), height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = stitle
        p.font.name = "Arial"
        p.font.size = Pt(13.5)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.space_after = Pt(2)

        p = tf.add_paragraph()
        p.text = stime
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = accent
        p.space_after = Pt(8)

        for itm in sitems:
            p = tf.add_paragraph()
            p.text = "- " + itm
            p.font.name = "Arial"
            p.font.size = Pt(10)
            p.font.color.rgb = MUTED_TEXT
            p.space_after = Pt(3)

    set_notes(s8, """[PERSON 2 - Handover]
Here is the roadmap for our live 25-minute system demonstration:
Person 3 will lead the student account lifecycle and profile builder.
Person 4 will demonstrate our search engine, real-time match scoring, and application tracking.
Person 5 will take over as a corporate recruiter, demonstrating job posting and applicant progression.
And Person 6 will demonstrate administrative governance, Drop Guard AI machine learning, and lead our panel defense.

We now switch to the live running application.""")

    prs.save(output_path)
    print(f"Successfully generated PowerPoint presentation at: {output_path}")

if __name__ == "__main__":
    out_file = r"c:\Users\pavan\Downloads\student-job-matching-20261027T105016Z-1-001 (2)\documentation\LaunchPad_Final_Presentation.pptx"
    create_deck(out_file)

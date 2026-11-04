from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from extensions import db
from models import Opportunity, Application, CompanyProfile, User
from utils import (
    compute_match_score,
    format_title_case,
    validate_student_name,
    validate_number,
    clean_comma_separated,
    sanitize_text,
)
from ml.cv_parser import parse_cv_text

student_bp = Blueprint("student", __name__, url_prefix="/student")


def student_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "student":
            flash("That page is only available to student accounts.", "error")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    return wrapper


def _score_and_sort(opportunities, profile):
    scored = []
    for opp in opportunities:
        score = compute_match_score(profile.skills_list(), profile.field_of_study, opp)
        scored.append((opp, score))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored


@student_bp.route("/dashboard")
@login_required
@student_required
def dashboard():
    profile = current_user.student_profile
    all_opps = Opportunity.query.filter_by(is_active=True).all()
    # Rank all live opportunities and display top matches on dashboard
    ranked = _score_and_sort(all_opps, profile)
    recommended = ranked[:8]
    recent_applications = (
        Application.query.filter_by(student_id=profile.id)
        .order_by(Application.applied_at.desc())
        .limit(5)
        .all()
    )

    # Calculate application status counts for chart
    application_status_data = {
        'submitted': sum(1 for app in profile.applications if app.status == 'submitted'),
        'reviewed': sum(1 for app in profile.applications if app.status == 'reviewed'),
        'shortlisted': sum(1 for app in profile.applications if app.status == 'shortlisted'),
        'accepted': sum(1 for app in profile.applications if app.status == 'accepted'),
        'rejected': sum(1 for app in profile.applications if app.status == 'rejected')
    }

    # Build activity timeline
    activities = []
    for app in recent_applications:
        activities.append({
            'type': 'application',
            'title': f'Applied to {app.opportunity.title}',
            'company': app.opportunity.company.company_name,
            'time': app.applied_at,
            'icon': 'application'
        })

    # Add profile update activity
    if profile.updated_at:
        activities.append({
            'type': 'profile',
            'title': 'Profile updated',
            'company': 'Your credentials',
            'time': profile.updated_at,
            'icon': 'profile'
        })

    # Sort by time
    activities.sort(key=lambda x: x['time'], reverse=True)
    activities = activities[:5]

    return render_template(
        "student/dashboard.html",
        profile=profile,
        recommended=recommended,
        total_opportunities=len(all_opps),
        recent_applications=recent_applications,
        application_status_data=application_status_data,
        activities=activities,
    )


@student_bp.route("/profile", methods=["GET", "POST"])
@login_required
@student_required
def profile():
    profile = current_user.student_profile

    if request.method == "POST":
        full_name_raw = request.form.get("full_name", profile.full_name)
        is_valid_name, name_val_or_err = validate_student_name(full_name_raw)
        if not is_valid_name:
            flash(name_val_or_err, "error")
            return redirect(url_for("student.profile"))
        profile.full_name = name_val_or_err

        # Experience years validation (0 to 50 years)
        exp_raw = request.form.get("experience_years")
        is_valid_exp, exp_num, exp_err = validate_number(
            exp_raw, field_name="Years of experience", min_val=0.0, max_val=50.0, default=0.0
        )
        if not is_valid_exp:
            flash(exp_err, "error")
            return redirect(url_for("student.profile"))
        profile.experience_years = exp_num

        profile.qualification = format_title_case(sanitize_text(request.form.get("qualification", ""), max_length=150))
        field_of_study = request.form.get("field_of_study", "").strip()
        profile.field_of_study = format_title_case(sanitize_text(field_of_study, max_length=150))
        profile.skills = clean_comma_separated(request.form.get("skills", ""))
        profile.interests = clean_comma_separated(request.form.get("interests", ""))
        profile.bio = sanitize_text(request.form.get("bio", ""), max_length=3000)
        profile.location = format_title_case(sanitize_text(request.form.get("location", ""), max_length=120))

        # Recompute a simple profile-completeness score used by fraud detection
        fields = [
            profile.full_name,
            profile.qualification,
            profile.field_of_study,
            profile.skills,
            profile.interests,
            profile.bio,
            profile.location,
        ]
        filled = sum(1 for f in fields if f and str(f).strip())
        profile.profile_completeness = round((filled / len(fields)) * 100, 1)

        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("student.profile"))

    return render_template("student/profile.html", profile=profile)


@student_bp.route("/settings", methods=["GET", "POST"])
@login_required
@student_required
def settings():
    """Notification and account settings."""
    if request.method == "POST":
        current_user.notify_applications = request.form.get("notify_applications") == "on"
        current_user.notify_opportunities = request.form.get("notify_opportunities") == "on"
        current_user.notify_updates = request.form.get("notify_updates") == "on"
        current_user.email_digest = request.form.get("email_digest") == "on"
        db.session.commit()
        flash("Notification preferences updated.", "success")
        return redirect(url_for("student.settings"))

    return render_template("student/settings.html")


@student_bp.route("/parse-cv", methods=["POST"])
@login_required
@student_required
def parse_cv():
    """Extracts structured candidate data from pasted CV text or uploaded text file."""
    text = ""
    if request.is_json:
        data = request.get_json() or {}
        text = data.get("cv_text", "")
    elif "cv_file" in request.files:
        f = request.files["cv_file"]
        if f:
            try:
                text = f.read().decode("utf-8", errors="ignore")
            except Exception:
                text = ""
    else:
        text = request.form.get("cv_text", "")

    if not text.strip() or len(text.strip()) < 15:
        return jsonify({"success": False, "error": "Please provide substantive resume or transcript text (at least 15 characters)."}), 400

    extracted = parse_cv_text(text)
    return jsonify({"success": True, "data": extracted})


@student_bp.route("/dossier")
@login_required
@student_required
def dossier():
    """Renders the executive, printable Dean's Certified Talent Dossier."""
    profile = current_user.student_profile
    apps = Application.query.filter_by(student_id=profile.id).all()
    return render_template("student/dossier.html", profile=profile, applications=apps)


@student_bp.route("/bookmark/<int:opp_id>", methods=["POST"])
@login_required
@student_required
def toggle_bookmark(opp_id):
    """Toggle bookmark status for an opportunity."""
    profile = current_user.student_profile
    opp = Opportunity.query.get_or_404(opp_id)

    if opp in profile.bookmarked_opportunities:
        profile.bookmarked_opportunities.remove(opp)
        db.session.commit()
        return jsonify({"bookmarked": False})
    else:
        profile.bookmarked_opportunities.append(opp)
        db.session.commit()
        return jsonify({"bookmarked": True})


@student_bp.route("/bookmarks")
@login_required
@student_required
def bookmarks():
    """Show bookmarked opportunities."""
    profile = current_user.student_profile
    bookmarked = profile.bookmarked_opportunities
    scored = _score_and_sort(bookmarked, profile)
    return render_template("student/bookmarks.html", results=scored)


@student_bp.route("/search")
@login_required
@student_required
def search():
    profile = current_user.student_profile
    query = request.args.get("q", "").strip()
    field = request.args.get("field", "").strip()
    location = request.args.get("location", "").strip()
    opp_type = request.args.get("type", "").strip()
    min_stipend_str = request.args.get("min_stipend", "").strip()
    work_type = request.args.get("work_type", "").strip()

    q = Opportunity.query.filter_by(is_active=True)
    if query:
        like = f"%{query}%"
        q = q.filter(
            db.or_(Opportunity.title.ilike(like), Opportunity.description.ilike(like))
        )
    if field and field != "All":
        q = q.filter(Opportunity.field_of_study.ilike(f"%{field}%"))
    if location and location != "All":
        q = q.filter(Opportunity.location.ilike(f"%{location}%"))
    if opp_type and opp_type != "All":
        q = q.filter(Opportunity.opportunity_type == opp_type)
    if min_stipend_str:
        try:
            min_stipend = float(min_stipend_str)
            q = q.filter(Opportunity.salary_stipend >= min_stipend)
        except ValueError:
            pass
    if work_type and work_type != "All":
        if work_type == "remote":
            q = q.filter(Opportunity.location.ilike("%remote%"))
        elif work_type == "on-site":
            q = q.filter(~Opportunity.location.ilike("%remote%"))
        # hybrid: allow both remote and on-site

    results = _score_and_sort(q.all(), profile)
    applied_ids = {
        a.opportunity_id for a in Application.query.filter_by(student_id=profile.id).all()
    }

    return render_template(
        "student/search.html",
        results=results,
        applied_ids=applied_ids,
        query=query,
        field=field,
        location=location,
        opp_type=opp_type,
        min_stipend=min_stipend_str,
        work_type=work_type,
    )


@student_bp.route("/opportunity/<int:opp_id>")
@login_required
@student_required
def view_opportunity(opp_id):
    opp = Opportunity.query.get_or_404(opp_id)
    profile = current_user.student_profile
    score = compute_match_score(profile.skills_list(), profile.field_of_study, opp)
    already_applied = Application.query.filter_by(
        student_id=profile.id, opportunity_id=opp.id
    ).first() is not None

    # Interactive Skill-Gap Analysis
    user_skills_lower = {s.strip().lower() for s in profile.skills_list() if s.strip()}
    req_skills = [s.strip() for s in opp.required_skills_list() if s.strip()]
    
    matched_skills = [s for s in req_skills if s.lower() in user_skills_lower]
    missing_skills = [s for s in req_skills if s.lower() not in user_skills_lower]
    potential_score = min(100.0, score + (len(missing_skills) * 14.0))

    # Curated recommendations based on faculty & missing skills
    recommended_electives = []
    if missing_skills:
        for ms in missing_skills[:3]:
            recommended_electives.append({
                "skill": ms,
                "course": f"Applied {ms} Intensive (Faculty Credential)",
                "provider": "University Institutional Micro-Credential",
                "impact": f"+{int(14.0)}% match boost",
            })

    return render_template(
        "student/opportunity_detail.html",
        opp=opp,
        score=score,
        already_applied=already_applied,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        potential_score=potential_score,
        recommended_electives=recommended_electives,
    )


@student_bp.route("/apply/<int:opp_id>", methods=["POST"])
@login_required
@student_required
def apply(opp_id):
    profile = current_user.student_profile
    opp = Opportunity.query.get_or_404(opp_id)

    existing = Application.query.filter_by(student_id=profile.id, opportunity_id=opp.id).first()
    if existing:
        flash("You've already applied to this opportunity.", "info")
        return redirect(url_for("student.view_opportunity", opp_id=opp.id))

    score = compute_match_score(profile.skills_list(), profile.field_of_study, opp)
    application = Application(student_id=profile.id, opportunity_id=opp.id, match_score=score)
    db.session.add(application)

    profile.applications_last_30_days = (profile.applications_last_30_days or 0) + 1
    profile.days_since_last_application = 0
    db.session.commit()

    flash("Application submitted!", "success")
    return redirect(url_for("student.applications"))


@student_bp.route("/applications")
@login_required
@student_required
def applications():
    profile = current_user.student_profile
    apps = (
        Application.query.filter_by(student_id=profile.id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    return render_template("student/applications.html", applications=apps)


@student_bp.route("/skill-dna")
@login_required
@student_required
def skill_dna():
    profile = current_user.student_profile
    skills_list = profile.skills_list()

    # Define multi-disciplinary skill categories across all career fields
    skill_categories = {
        'Technical & Analytics': ['Python', 'Java', 'SQL', 'Excel', 'Financial Modeling', 'CAD', 'MATLAB', 'Data Analysis', 'Auditing', 'Clinical Skills'],
        'Communication & Media': ['Public Speaking', 'Writing', 'Presentation', 'Negotiation', 'Copywriting', 'Brand Strategy', 'Client Relations', 'Drafting'],
        'Leadership & Operations': ['Team Management', 'Project Management', 'Mentoring', 'Decision Making', 'Operations', 'Budgeting', 'Compliance'],
        'Problem Solving & Research': ['Critical Thinking', 'Analytical', 'Research', 'Diagnostic Skills', 'Financial Analysis', 'Risk Management'],
        'Design & Innovation': ['Design', 'UI/UX', 'Innovation', 'Brainstorming', 'Creative Strategy', 'Prototyping', 'Content Creation'],
        'Collaboration & Ethics': ['Teamwork', 'Conflict Resolution', 'Networking', 'Partnership', 'Ethics', 'Stakeholder Management']
    }

    # Calculate scores for each category
    category_scores = {}
    for category, category_skills in skill_categories.items():
        matching_skills = [s for s in skills_list if any(cs.lower() in s.lower() for cs in category_skills)]
        if matching_skills:
            category_scores[category] = min(100, len(matching_skills) * 25 + 20)
        else:
            category_scores[category] = 25  # Base score

    # Prepare data for the chart
    skill_labels = list(category_scores.keys())
    skill_scores = [category_scores[cat] for cat in skill_labels]

    # Prepare detailed skill breakdown
    skills_data = []
    for skill in skills_list:
        score = min(100, len(skill.split()) * 15 + 60)
        skills_data.append({'name': skill, 'score': score})

    # Generate multi-disciplinary recommendations based on student's field
    field_lower = (profile.field_of_study or "").lower()
    if any(k in field_lower for k in ['finance', 'accounting', 'economics']):
        recommendations = [
            {'title': 'Master Advanced Financial Modeling', 'description': 'Excel modeling, DCF valuation, and IFRS standards will position you for investment and corporate finance mandates.', 'category': 'Technical & Analytics'},
            {'title': 'Chartered Accountancy (SAICA) Track', 'description': 'Begin preparatory coursework for initial assessments of competence to accelerate post-graduate training.', 'category': 'Leadership & Operations'},
            {'title': 'Corporate Pitching & Valuation Defense', 'description': 'Refine presentation techniques for board-level financial reports and advisory pitches.', 'category': 'Communication & Media'}
        ]
    elif any(k in field_lower for k in ['engineering', 'civil', 'mechanical', 'electrical']):
        recommendations = [
            {'title': 'AutoCAD & 3D Parametric Modeling', 'description': 'Proficiency in industry-standard CAD, Revit, or SolidWorks is essential for project engineering placements.', 'category': 'Technical & Analytics'},
            {'title': 'Project Engineering & Cost Estimation', 'description': 'Develop expertise in structural bill of quantities (BOQ) and site safety governance.', 'category': 'Leadership & Operations'},
            {'title': 'ECSA Candidate Registration Prep', 'description': 'Document experiential hours for registration as Candidate Engineer with ECSA.', 'category': 'Collaboration & Ethics'}
        ]
    elif any(k in field_lower for k in ['health', 'nursing', 'pharmacy', 'medicine']):
        recommendations = [
            {'title': 'Clinical Pharmacotherapy Protocols', 'description': 'Deepen mastery of hospital dispensary protocols and clinical audit management.', 'category': 'Technical & Analytics'},
            {'title': 'Patient Consultation & Ethics', 'description': 'Hone empathetic clinical communication and compliance with healthcare regulatory boards.', 'category': 'Communication & Media'},
            {'title': 'Clinical Research Methodology', 'description': 'Contribute to published medical research or randomized clinical trials to enhance residency prospects.', 'category': 'Problem Solving & Research'}
        ]
    elif any(k in field_lower for k in ['marketing', 'media', 'communication', 'pr']):
        recommendations = [
            {'title': 'Omnichannel Performance Marketing', 'description': 'Gain certification in Google Analytics 4, Meta Ads Manager, and growth telemetry.', 'category': 'Technical & Analytics'},
            {'title': 'Brand Architecture & Storytelling', 'description': 'Build a public portfolio showcasing brand repositioning campaigns and PR releases.', 'category': 'Design & Innovation'},
            {'title': 'Crisis Communication & Media Relations', 'description': 'Master press conference coordination and strategic stakeholder engagement.', 'category': 'Communication & Media'}
        ]
    else:
        recommendations = [
            {'title': 'Data-Driven Decision Making', 'description': 'Python, SQL, and PowerBI skills substantially boost starting placement offers across all industries.', 'category': 'Technical & Analytics'},
            {'title': 'Executive Communication & Presentation', 'description': 'Sharpen persuasive writing and cross-functional leadership techniques.', 'category': 'Communication & Media'},
            {'title': 'Professional Portfolio Architecture', 'description': 'Showcase capstone projects and verified case studies directly to hiring decision-makers.', 'category': 'Design & Innovation'}
        ]

    return render_template(
        "student/skill_dna.html",
        skill_labels=skill_labels,
        skill_scores=skill_scores,
        skills=skills_data,
        recommendations=recommendations
    )


@student_bp.route("/career-path")
@login_required
@student_required
def career_path():
    profile = current_user.student_profile
    field = profile.field_of_study or "General"

    # Multi-disciplinary career progression paths across all faculties
    career_paths = {
        'Information Technology': [
            {'title': 'Junior Software Developer', 'timeline': '0-2 years', 'skills': ['Python / Java', 'Version Control', 'Unit Testing'], 'salary': 'R20,000 - R32,000 / mo', 'description': 'Entry-level engineering role contributing to production features, testing, and system architecture.'},
            {'title': 'Software Engineer', 'timeline': '2-4 years', 'skills': ['System Design', 'Cloud APIs', 'Microservices'], 'salary': 'R35,000 - R55,000 / mo', 'description': 'Mid-level engineer owning core service modules and cross-functional integration.'},
            {'title': 'Senior Systems Architect', 'timeline': '4-7 years', 'skills': ['Enterprise Architecture', 'High Availability', 'Mentorship'], 'salary': 'R60,000 - R90,000 / mo', 'description': 'Technical authority driving distributed infrastructure, security posture, and code standards.'},
            {'title': 'Chief Technology Officer / Principal', 'timeline': '7+ years', 'skills': ['Executive Leadership', 'Technology Strategy', 'Venture Scaling'], 'salary': 'R95,000 - R150,000+ / mo', 'description': 'Strategic leadership heading enterprise engineering organisations and technology roadmaps.'}
        ],
        'Finance & Accounting': [
            {'title': 'Graduate Analyst / Audit Trainee', 'timeline': '0-2 years', 'skills': ['Financial Modeling', 'IFRS Standards', 'Audit Procedures'], 'salary': 'R22,000 - R35,000 / mo', 'description': 'Conducting balance sheet audits, statutory reconciliations, and financial due diligence.'},
            {'title': 'Senior Financial Analyst / CA(SA)', 'timeline': '2-5 years', 'skills': ['Valuation Modeling', 'Tax Strategy', 'Variance Analysis'], 'salary': 'R40,000 - R65,000 / mo', 'description': 'Advising executive leadership on capital allocation, budget forecasting, and corporate risk.'},
            {'title': 'Finance Manager / VP Advisory', 'timeline': '5-8 years', 'skills': ['M&A Execution', 'Capital Markets', 'Treasury'], 'salary': 'R70,000 - R110,000 / mo', 'description': 'Leading corporate finance divisions, debt restructuring, and investment portfolio governance.'},
            {'title': 'Chief Financial Officer (CFO)', 'timeline': '8+ years', 'skills': ['Capital Strategy', 'Investor Relations', 'Corporate Governance'], 'salary': 'R120,000 - R200,000+ / mo', 'description': 'Senior executive heading institutional balance sheets, shareholder returns, and fiscal policy.'}
        ],
        'Engineering': [
            {'title': 'Candidate / Junior Engineer', 'timeline': '0-2 years', 'skills': ['CAD & FEA', 'Site Inspection', 'Quality Assurance'], 'salary': 'R22,000 - R34,000 / mo', 'description': 'Field and design office execution, preparing technical specifications and project schematics.'},
            {'title': 'Project Engineer (Pr.Eng)', 'timeline': '2-5 years', 'skills': ['Project Management', 'Structural Design', 'ECSA Compliance'], 'salary': 'R38,000 - R60,000 / mo', 'description': 'Managing multi-disciplinary engineering projects, budget execution, and site safety standards.'},
            {'title': 'Lead Engineering Consultant', 'timeline': '5-8 years', 'skills': ['Infrastructure Planning', 'Contract Law (FIDIC)', 'Risk Analysis'], 'salary': 'R65,000 - R95,000 / mo', 'description': 'Directing major public and private infrastructure tenders, capital assets, and sustainability plans.'},
            {'title': 'Engineering Director / Partner', 'timeline': '8+ years', 'skills': ['Executive Engineering', 'Asset Strategy', 'Firm Governance'], 'salary': 'R105,000 - R180,000+ / mo', 'description': 'Executive leadership of national consultancies, energy conglomerates, or construction firms.'}
        ],
        'Marketing & Communications': [
            {'title': 'Marketing Coordinator / PR Associate', 'timeline': '0-2 years', 'skills': ['Content Strategy', 'Campaign Analytics', 'Media Relations'], 'salary': 'R18,000 - R28,000 / mo', 'description': 'Executing promotional campaigns, press releases, social growth metrics, and market research.'},
            {'title': 'Brand & Growth Manager', 'timeline': '2-5 years', 'skills': ['Omnichannel Strategy', 'Budget Optimisation', 'Customer Acquisition'], 'salary': 'R32,000 - R52,000 / mo', 'description': 'Leading product launches, brand positioning, multi-million rand advertising allocations, and PR.'},
            {'title': 'Head of Marketing & Communications', 'timeline': '5-8 years', 'skills': ['Brand Governance', 'Crisis Management', 'Executive Media'], 'salary': 'R55,000 - R85,000 / mo', 'description': 'Overseeing enterprise communication, corporate identity, public affairs, and market share.'},
            {'title': 'Chief Marketing Officer (CMO)', 'timeline': '8+ years', 'skills': ['Global Brand Vision', 'Revenue Leadership', 'Consumer Psychology'], 'salary': 'R90,000 - R160,000+ / mo', 'description': 'Executive board officer steering market reputation, global brand valuation, and revenue growth.'}
        ],
        'Healthcare & Nursing': [
            {'title': 'Clinical Research Associate / Intern', 'timeline': '0-2 years', 'skills': ['Patient Protocols', 'Clinical Auditing', 'Pharmacovigilance'], 'salary': 'R20,000 - R32,000 / mo', 'description': 'Administering clinical evaluations, laboratory verification, and compliance with healthcare councils.'},
            {'title': 'Senior Medical Specialist / Clinical Lead', 'timeline': '2-5 years', 'skills': ['Diagnostic Precision', 'Protocol Design', 'Team Leadership'], 'salary': 'R38,000 - R62,000 / mo', 'description': 'Managing clinical wards, healthcare operations, and patient safety governance.'},
            {'title': 'Healthcare Services Director', 'timeline': '5-8 years', 'skills': ['Hospital Administration', 'Regulatory Policy', 'Quality Governance'], 'salary': 'R65,000 - R100,000 / mo', 'description': 'Directing hospital systems, clinical trials programs, and regional health center strategy.'},
            {'title': 'Chief Medical Officer / Health Executive', 'timeline': '8+ years', 'skills': ['Healthcare Strategy', 'Epidemiology Policy', 'Executive Care'], 'salary': 'R110,000 - R190,000+ / mo', 'description': 'Directing pharmaceutical research, hospital conglomerates, and national healthcare systems.'}
        ],
        'General': [
            {'title': 'Associate Trainee', 'timeline': '0-2 years', 'skills': ['Analytical Thinking', 'Business Communication', 'Operational Agility'], 'salary': 'R18,000 - R26,000 / mo', 'description': 'Foundation rotation developing high-level organisational execution and stakeholder relations.'},
            {'title': 'Operations Specialist', 'timeline': '2-4 years', 'skills': ['Project Execution', 'Process Engineering', 'Client Advisory'], 'salary': 'R30,000 - R48,000 / mo', 'description': 'Managing core operational divisions, partner relations, and business intelligence reporting.'},
            {'title': 'Senior Business Manager', 'timeline': '4-7 years', 'skills': ['Departmental Strategy', 'Budget Authority', 'Team Development'], 'salary': 'R52,000 - R80,000 / mo', 'description': 'Heading division performance, strategic client contracts, and talent development.'},
            {'title': 'Managing Director / Executive', 'timeline': '7+ years', 'skills': ['Corporate Leadership', 'Strategic Expansion', 'Board Governance'], 'salary': 'R85,000 - R150,000+ / mo', 'description': 'Executive stewardship of enterprise growth, shareholder value, and organisational culture.'}
        ]
    }

    # Match student's field of study against career paths
    matched_path = None
    field_lower = field.lower()
    for key in career_paths:
        if any(w in field_lower for w in key.lower().split('&')) or key.lower() in field_lower:
            matched_path = career_paths[key]
            field = key
            break

    paths = matched_path or career_paths['General']

    return render_template("student/career_path.html", paths=paths, field=field)


@student_bp.route("/predictions")
@login_required
@student_required
def predictions():
    profile = current_user.student_profile
    all_opps = Opportunity.query.filter_by(is_active=True).all()

    # Calculate prediction scores for each opportunity
    predictions = []
    for opp in all_opps:
        score = compute_match_score(profile.skills_list(), profile.field_of_study, opp)

        # Calculate confidence based on various factors
        confidence = min(95, score + (profile.profile_completeness or 0) * 0.3)

        # Determine prediction label
        if confidence >= 80:
            prediction = 'High Match'
            color = 'success'
        elif confidence >= 60:
            prediction = 'Good Match'
            color = 'medium'
        elif confidence >= 40:
            prediction = 'Moderate Match'
            color = 'neutral'
        else:
            prediction = 'Low Match'
            color = 'high'

        predictions.append({
            'opportunity': opp,
            'score': score,
            'confidence': round(confidence, 1),
            'prediction': prediction,
            'color': color
        })

    # Sort by confidence
    predictions.sort(key=lambda x: x['confidence'], reverse=True)

    return render_template("student/predictions.html", predictions=predictions[:20])


@student_bp.route("/insights")
@login_required
@student_required
def insights():
    profile = current_user.student_profile
    applications = Application.query.filter_by(student_id=profile.id).all()

    # Calculate analytics
    total_applications = len(applications)
    avg_match_score = sum(app.match_score for app in applications) / total_applications if total_applications > 0 else 0

    # Get application status breakdown
    status_counts = {'pending': 0, 'viewed': 0, 'interview': 0, 'offer': 0, 'rejected': 0}
    for app in applications:
        if hasattr(app, 'status'):
            status = app.status.lower()
            if status in status_counts:
                status_counts[status] += 1
        else:
            status_counts['pending'] += 1

    # Calculate response rate (simulated)
    response_rate = min(100, total_applications * 15) if total_applications > 0 else 0

    # Calculate success rate
    success_rate = (status_counts['offer'] / total_applications * 100) if total_applications > 0 else 0

    # Get recent activity
    recent_apps = sorted(applications, key=lambda x: x.applied_at, reverse=True)[:5]

    # Skill match trend (simulated data)
    skill_trend = {
        'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        'data': [65, 72, 78, 82]
    }

    insights_data = {
        'total_applications': total_applications,
        'avg_match_score': round(avg_match_score, 1),
        'response_rate': response_rate,
        'success_rate': round(success_rate, 1),
        'status_counts': status_counts,
        'recent_apps': recent_apps,
        'skill_trend': skill_trend
    }

    return render_template("student/insights.html", insights=insights_data)

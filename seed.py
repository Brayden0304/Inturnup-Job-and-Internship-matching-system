"""
InternUp - Student Job & Internship Matching Demonstration Seed Data
==============================================================
Populates the database with:
- Authentic University Student Profiles (Wits, UCT, Tuks, Maties, UKZN)
- Tier-One Corporate Employer Accounts (Standard Bank, Discovery, Sasol, Deloitte, Bowmans)
- 24 Detailed Career Postings across all fields (Finance, Engineering, IT, Healthcare, Marketing, Law)
- DropGuard™ ML Anomaly Screening Demonstration

Run in your terminal:
    python seed.py
"""
from datetime import date, timedelta
from app import create_app
from extensions import db
from models import User, StudentProfile, CompanyProfile, Opportunity, Application, RiskAssessment
from utils import compute_match_score
from ml.drop_guard import get_engine

app = create_app()

with app.app_context():
    print("Resetting database schema...")
    db.drop_all()
    db.create_all()

    print("Seeding authentic institutional & corporate accounts...")

    # =========================================================================
    # 1. INSTITUTIONAL ADMINISTRATOR
    # =========================================================================
    # Primary Institutional Admin Account
    admin_internup = User(email="admin@internup.ac.za", role="admin")
    admin_internup.set_password("Admin@123")
    db.session.add(admin_internup)

    admin_primary = User(email="admin@launchpad.local", role="admin")
    admin_primary.set_password("Admin@123")
    db.session.add(admin_primary)

    # =========================================================================
    # 2. REALISTIC STUDENT ACCOUNTS (Primary Demo Logins)
    # =========================================================================

    # --- Student 1: Thabo Nkosi (Computer Science & Cloud - Wits University) ---
    u_thabo = User(email="thabo@student.com", role="student")
    u_thabo.set_password("Student@123")
    db.session.add(u_thabo)
    db.session.flush()
    s_thabo = StudentProfile(
        user_id=u_thabo.id,
        full_name="Thabo Nkosi",
        qualification="BSc (Hons) Computer Science & Applied Mathematics",
        field_of_study="Information Technology",
        skills="Python, Golang, SQL, Docker, AWS, Kubernetes, Distributed Systems, Git, Linux, CI/CD",
        interests="Cloud Infrastructure, Distributed Systems, High-Performance Computing",
        bio="Final-year Honours candidate at Wits University. Dean's Merit List (2024, 2025). Contributor to open-source telemetry tools. Seeking graduate software engineering or cloud infrastructure rotation.",
        location="Braamfontein, Johannesburg",
        experience_years=1.5,
        profile_completeness=96.0,
        logins_last_30_days=22,
        applications_last_30_days=5,
        days_since_last_login=1,
        days_since_last_application=2,
        saved_searches=6,
        profile_views_received=38,
    )
    db.session.add(s_thabo)

    # --- Student 2: Ayanda Mthembu (Finance & Accounting - UCT) ---
    u_ayanda = User(email="ayanda@student.com", role="student")
    u_ayanda.set_password("Student@123")
    db.session.add(u_ayanda)
    db.session.flush()
    s_ayanda = StudentProfile(
        user_id=u_ayanda.id,
        full_name="Ayanda Mthembu",
        qualification="BCom (Hons) in Accounting Sciences (CTA / SAICA Stream)",
        field_of_study="Finance & Accounting",
        skills="Financial Modeling, IFRS, Auditing, GAAP, Valuation, Advanced Excel, Tax Strategy, Risk Analysis",
        interests="Investment Banking, Corporate Valuation, M&A Advisory, Private Equity",
        bio="UCT Commerce Dean's List fellow. Former Treasurer of UCT Investment Society. Completed winter advisory vacation work at PwC. Pursuing SAICA articles and corporate finance placements.",
        location="Rondebosch, Cape Town",
        experience_years=1.0,
        profile_completeness=92.0,
        logins_last_30_days=19,
        applications_last_30_days=4,
        days_since_last_login=1,
        days_since_last_application=3,
        saved_searches=5,
        profile_views_received=29,
    )
    db.session.add(s_ayanda)

    # --- Student 3: Sipho Khumalo (Mechanical & Mechatronics - University of Pretoria) ---
    u_sipho = User(email="sipho@student.com", role="student")
    u_sipho.set_password("Student@123")
    db.session.add(u_sipho)
    db.session.flush()
    s_sipho = StudentProfile(
        user_id=u_sipho.id,
        full_name="Sipho Khumalo",
        qualification="BEng (Hons) in Mechanical & Mechatronics Engineering",
        field_of_study="Engineering",
        skills="SolidWorks, AutoCAD, MATLAB, FEA Simulation, Thermodynamics, PLC Automation, Project Management, ECSA Guidelines",
        interests="Industrial Automation, Clean Energy Powertrains, Fluid Dynamics",
        bio="Engineering graduate candidate registered with ECSA as Candidate Engineer. Capstone thesis: Solar thermal energy storage optimisation. Experienced in CAD modeling and stress analysis.",
        location="Hatfield, Pretoria",
        experience_years=1.0,
        profile_completeness=88.0,
        logins_last_30_days=14,
        applications_last_30_days=3,
        days_since_last_login=2,
        days_since_last_application=4,
        saved_searches=4,
        profile_views_received=22,
    )
    db.session.add(s_sipho)

    # --- Student 4: Chloe van der Merwe (Brand Strategy - Stellenbosch) ---
    u_chloe = User(email="chloe@student.com", role="student")
    u_chloe.set_password("Student@123")
    db.session.add(u_chloe)
    db.session.flush()
    s_chloe = StudentProfile(
        user_id=u_chloe.id,
        full_name="Chloe van der Merwe",
        qualification="BA (Hons) in Strategic Brand Communication & Media",
        field_of_study="Marketing & Communications",
        skills="Brand Strategy, Omnichannel Marketing, Copywriting, Public Relations, Google Analytics 4, SEO, Crisis Communications",
        interests="Luxury Brand Architecture, Digital Storytelling, Consumer Neuroscience",
        bio="Stellenbosch brand communication graduate with agency internship experience. Managed cross-channel university campaigns with over 250k impressions. Certified in GA4 and Meta Blueprint.",
        location="Stellenbosch, Western Cape",
        experience_years=1.2,
        profile_completeness=90.0,
        logins_last_30_days=16,
        applications_last_30_days=3,
        days_since_last_login=1,
        days_since_last_application=3,
        saved_searches=4,
        profile_views_received=27,
    )
    db.session.add(s_chloe)

    # --- Student 5: Lerato Dlamini (Healthcare - UKZN - Disengagement Demo Profile) ---
    u_lerato = User(email="lerato@student.com", role="student")
    u_lerato.set_password("Student@123")
    db.session.add(u_lerato)
    db.session.flush()
    s_lerato = StudentProfile(
        user_id=u_lerato.id,
        full_name="Lerato Dlamini",
        qualification="BCur in Professional Nursing & Clinical Sciences",
        field_of_study="Healthcare & Nursing",
        skills="Patient Care, Clinical Protocols, Triage, Pharmacology Basics",
        interests="Hospital Nursing, Intensive Care, Pediatric Healthcare",
        bio="Candidate seeking regional hospital nursing residency and clinical care opportunities.",
        location="Berea, Durban",
        experience_years=0.5,
        profile_completeness=28.0,
        logins_last_30_days=1,
        applications_last_30_days=1,
        days_since_last_login=48,
        days_since_last_application=95,
        saved_searches=0,
        profile_views_received=2,
    )
    db.session.add(s_lerato)

    # =========================================================================
    # 3. REALISTIC TIER-ONE CORPORATE EMPLOYERS (Primary Demo Logins)
    # =========================================================================

    # Company 1: Standard Bank Group (CIB)
    cu1 = User(email="standardbank@company.com", role="company")
    cu1.set_password("Company@123")
    db.session.add(cu1)
    db.session.flush()
    c_sbg = CompanyProfile(
        user_id=cu1.id,
        company_name="Standard Bank Corporate & Investment Banking",
        industry="Financial Services & Merchant Banking",
        website="https://www.standardbank.co.za/cib",
        description="Africa's largest bank by assets. Our Corporate and Investment Banking division advises governments, multinationals, and institutional investors across capital markets and infrastructure.",
        location="Sandton Central, Johannesburg",
        company_age_years=162.0,
        verified=True,
    )
    db.session.add(c_sbg)

    # Company 2: Discovery Limited
    cu2 = User(email="discovery@company.com", role="company")
    cu2.set_password("Company@123")
    db.session.add(cu2)
    db.session.flush()
    c_disc = CompanyProfile(
        user_id=cu2.id,
        company_name="Discovery Limited (Health & Vitality)",
        industry="Healthcare, Insurance & FinTech",
        website="https://www.discovery.co.za",
        description="Global financial services organisation pioneering shared-value health insurance, clinical informatics, digital banking, and predictive behavioural data science.",
        location="1 Discovery Place, Sandton",
        company_age_years=32.0,
        verified=True,
    )
    db.session.add(c_disc)

    # Company 3: Sasol Energy & Chemical Engineering
    cu3 = User(email="sasol@company.com", role="company")
    cu3.set_password("Company@123")
    db.session.add(cu3)
    db.session.flush()
    c_sasol = CompanyProfile(
        user_id=cu3.id,
        company_name="Sasol Global Energy & Engineering",
        industry="Energy, Chemical & Infrastructure",
        website="https://www.sasol.com",
        description="Integrated chemicals and energy company operating world-scale synthetic fuel plants, renewable hydrogen infrastructure, and advanced process engineering facilities.",
        location="Sasol Place, Rosebank, Johannesburg",
        company_age_years=74.0,
        verified=True,
    )
    db.session.add(c_sasol)

    # Company 4: Deloitte Africa
    cu4 = User(email="deloitte@company.com", role="company")
    cu4.set_password("Company@123")
    db.session.add(cu4)
    db.session.flush()
    c_deloitte = CompanyProfile(
        user_id=cu4.id,
        company_name="Deloitte & Touche South Africa",
        industry="Audit, Advisory & Tax Consulting",
        website="https://www2.deloitte.com/za",
        description="Global leader in professional services, statutory audit, corporate finance restructuring, and cyber risk advisory across the African continent.",
        location="Waterfall City, Midrand, Gauteng",
        company_age_years=179.0,
        verified=True,
    )
    db.session.add(c_deloitte)

    # Company 5: Bowmans Law
    cu5 = User(email="bowmans@company.com", role="company")
    cu5.set_password("Company@123")
    db.session.add(cu5)
    db.session.flush()
    c_bowmans = CompanyProfile(
        user_id=cu5.id,
        company_name="Bowmans (Bowman Gilfillan)",
        industry="Corporate Commercial Law Practice",
        website="https://bowmanslaw.com",
        description="Premier Pan-African law firm advising multinational corporations, sovereign entities, and financial institutions on banking, mergers & acquisitions, and regulatory compliance.",
        location="11 Alice Lane, Sandton",
        company_age_years=120.0,
        verified=True,
    )
    db.session.add(c_bowmans)

    # Company 6: Shady / Fraud Demo Entity
    cu_shady = User(email="quickcash@company.com", role="company")
    cu_shady.set_password("Company@123")
    db.session.add(cu_shady)
    db.session.flush()
    c_shady = CompanyProfile(
        user_id=cu_shady.id,
        company_name="QuickCash Global Capital",
        industry="Direct Online Lending",
        website="",
        description="Instant money guaranteed! Zero CV or experience required, earn massive daily deposits immediately.",
        location="Offshore / Unregistered",
        company_age_years=0.06,
        verified=False,
    )
    db.session.add(c_shady)

    db.session.flush()

    # =========================================================================
    # 4. 24 AUTHENTIC OPPORTUNITIES ACROSS ALL FIELDS
    # =========================================================================
    print("Seeding 24 authentic opportunities across all faculties...")

    opportunities = [
        # --- 1. Finance & Investment Banking (Standard Bank) ---
        Opportunity(
            company_id=c_sbg.id,
            title="Junior Investment Banking Analyst (Mergers & Acquisitions)",
            opportunity_type="entry-level",
            description="Rotate through our Sandton Investment Banking Division. Conduct complex DCF valuation modeling, prepare confidential information memoranda (CIM), analyse cross-border transaction comparables, and assist executive directors on corporate debt restructuring.",
            required_skills="Financial Modeling, Valuation, Excel, Risk Analysis, IFRS, Communication",
            field_of_study="Finance & Accounting",
            location="Sandton Central, Johannesburg",
            salary_stipend=32000,
            duration_months=12,
            closing_date=date.today() + timedelta(days=45),
            is_active=True,
        ),
        # --- 2. Accounting & SAICA Articles (Deloitte) ---
        Opportunity(
            company_id=c_deloitte.id,
            title="SAICA Trainee Chartered Accountant (Audit 2026 Cohort)",
            opportunity_type="entry-level",
            description="Join Deloitte's prestigious 3-year accredited SAICA training contract. Lead statutory field audits, evaluate client internal controls under ISA standards, verify revenue recognition under IFRS 15, and prepare for ITC/APC board examinations.",
            required_skills="IFRS, Auditing, GAAP, Financial Modeling, Advanced Excel, Communication",
            field_of_study="Finance & Accounting",
            location="Waterfall City, Midrand",
            salary_stipend=26500,
            duration_months=36,
            closing_date=date.today() + timedelta(days=60),
            is_active=True,
        ),
        # --- 3. Technology & Cloud Architecture (Standard Bank CIB) ---
        Opportunity(
            company_id=c_sbg.id,
            title="Associate Cloud Platform Engineer (AWS & Distributed Systems)",
            opportunity_type="internship",
            description="Engineer mission-critical financial cloud microservices within our Core Banking Modernization initiative. Automate infrastructure with Terraform and Kubernetes, monitor real-time telemetry, and write robust APIs in Python and Go.",
            required_skills="Python, Cloud Computing, AWS, Docker, Kubernetes, Git, SQL",
            field_of_study="Information Technology",
            location="Sandton, Johannesburg",
            salary_stipend=24000,
            duration_months=12,
            closing_date=date.today() + timedelta(days=35),
            is_active=True,
        ),
        # --- 4. Health Data Science & Machine Learning (Discovery) ---
        Opportunity(
            company_id=c_disc.id,
            title="Junior Machine Learning & Actuarial Data Fellow",
            opportunity_type="internship",
            description="Work with Discovery's Vitality behavioural research lab. Develop predictive machine learning models in Python (scikit-learn, XGBoost) to forecast clinical wellness outcomes and optimise personalised member risk scores.",
            required_skills="Python, SQL, Data Analysis, Analytical, Machine Learning, Git",
            field_of_study="Information Technology",
            location="1 Discovery Place, Sandton",
            salary_stipend=25000,
            duration_months=12,
            closing_date=date.today() + timedelta(days=40),
            is_active=True,
        ),
        # --- 5. Mechanical Engineering (Sasol) ---
        Opportunity(
            company_id=c_sasol.id,
            title="Graduate Mechanical Plant & Reliability Engineer",
            opportunity_type="entry-level",
            description="Join Sasol's synthetic fuels and green hydrogen engineering rotational program. Perform finite element analysis (FEA), evaluate pressure vessel integrity, optimise steam turbine thermal efficiency, and prepare maintenance blueprints.",
            required_skills="SolidWorks, CAD, Thermodynamics, FEA Simulation, Quality Assurance, ECSA Guidelines",
            field_of_study="Engineering",
            location="Secunda & Rosebank",
            salary_stipend=28000,
            duration_months=24,
            closing_date=date.today() + timedelta(days=50),
            is_active=True,
        ),
        # --- 6. Civil & Structural Engineering (Sasol Infrastructure) ---
        Opportunity(
            company_id=c_sasol.id,
            title="Civil & Structural Infrastructure Engineering Fellow",
            opportunity_type="internship",
            description="Participate in large-scale renewable energy infrastructure projects. Calculate reinforced concrete foundation loads, model stormwater drainage basins in AutoCAD Civil 3D, and inspect structural steel construction sites.",
            required_skills="AutoCAD, CAD, Project Management, Quality Assurance, Structural Design",
            field_of_study="Engineering",
            location="Secunda / Pretoria",
            salary_stipend=22000,
            duration_months=12,
            closing_date=date.today() + timedelta(days=45),
            is_active=True,
        ),
        # --- 7. Electrical Power Systems (Sasol Energy) ---
        Opportunity(
            company_id=c_sasol.id,
            title="Junior Electrical Power Systems & Substation Trainee",
            opportunity_type="internship",
            description="Analyse high-voltage electrical distribution networks, calibrate numerical protection relays, develop PLC automation routines, and conduct arc flash hazard calculations in MATLAB/Simulink.",
            required_skills="MATLAB, CAD, Electrical Systems, Quality Assurance, Analytical",
            field_of_study="Engineering",
            location="Sasolburg / Rosebank",
            salary_stipend=23500,
            duration_months=12,
            closing_date=date.today() + timedelta(days=30),
            is_active=True,
        ),
        # --- 8. Brand Marketing & Omnichannel PR (Discovery) ---
        Opportunity(
            company_id=c_disc.id,
            title="Brand Strategy & Omnichannel Campaign Associate",
            opportunity_type="entry-level",
            description="Drive national marketing and brand loyalty initiatives for Discovery Bank and Vitality. Manage digital media performance, analyse customer engagement metrics in Google Analytics 4, and draft high-impact copy for public releases.",
            required_skills="Brand Strategy, Omnichannel Marketing, Copywriting, Google Analytics 4, SEO, Public Relations",
            field_of_study="Marketing & Communications",
            location="1 Discovery Place, Sandton",
            salary_stipend=21000,
            duration_months=12,
            closing_date=date.today() + timedelta(days=38),
            is_active=True,
        ),
        # --- 9. Public Relations & Corporate Affairs (Deloitte) ---
        Opportunity(
            company_id=c_deloitte.id,
            title="Corporate Communications & Executive PR Coordinator",
            opportunity_type="internship",
            description="Draft executive briefings, press releases, and leadership speeches for Deloitte Africa partners. Coordinate media interviews with leading business publications (Business Day, Financial Mail) and assist with crisis communication management.",
            required_skills="Public Relations, Copywriting, Communication, Crisis Communications, Media Relations",
            field_of_study="Marketing & Communications",
            location="Waterfall City, Midrand",
            salary_stipend=19000,
            duration_months=6,
            closing_date=date.today() + timedelta(days=28),
            is_active=True,
        ),
        # --- 10. Healthcare & Clinical Research (Discovery Health) ---
        Opportunity(
            company_id=c_disc.id,
            title="Clinical Research Associate & Health Protocols Analyst",
            opportunity_type="internship",
            description="Coordinate medical audit reviews for Discovery Health medical schemes. Analyse clinical pathway compliance, evaluate pharmaceutical therapeutic outcomes, and collaborate with medical specialists on hospital quality benchmarks.",
            required_skills="Clinical Protocols, Patient Care, Healthcare Regulations, Medical Research, Quality Assurance",
            field_of_study="Healthcare & Nursing",
            location="Sandton Central, Johannesburg",
            salary_stipend=22500,
            duration_months=12,
            closing_date=date.today() + timedelta(days=42),
            is_active=True,
        ),
        # --- 11. Hospital Clinical Informatics & Pharmacy (Discovery Health) ---
        Opportunity(
            company_id=c_disc.id,
            title="Hospital Clinical Informatics & Dispensing Fellow",
            opportunity_type="learnership",
            description="Collaborate with hospital clinical networks to monitor electronic patient dispensary records, audit antimicrobial stewardship protocols, and reduce clinical medication errors across regional hospital wards.",
            required_skills="Clinical Protocols, Patient Care, Pharmacovigilance, Data Analysis, Communication",
            field_of_study="Healthcare & Nursing",
            location="Cape Town & Durban",
            salary_stipend=18500,
            duration_months=12,
            closing_date=date.today() + timedelta(days=25),
            is_active=True,
        ),
        # --- 12. Corporate Commercial Law (Bowmans) ---
        Opportunity(
            company_id=c_bowmans.id,
            title="Candidate Attorney (2026 Articles of Clerkship)",
            opportunity_type="entry-level",
            description="Two-year candidate attorney rotation at Bowmans. Rotate through Corporate M&A, Banking & Finance, and Competition Law. Draft cross-border sale of shares agreements, conduct regulatory due diligence, and attend High Court litigation proceedings.",
            required_skills="Legal Research, Legal Drafting, Communication, Analytical, Contract Law",
            field_of_study="Law & Legal Studies",
            location="11 Alice Lane, Sandton",
            salary_stipend=28000,
            duration_months=24,
            closing_date=date.today() + timedelta(days=60),
            is_active=True,
        ),
        # --- 13. Financial Risk & Compliance (Standard Bank CIB) ---
        Opportunity(
            company_id=c_sbg.id,
            title="Quantitative Market Risk & Basel III Analyst",
            opportunity_type="entry-level",
            description="Formulate mathematical Value-at-Risk (VaR) algorithms, conduct liquidity stress tests across derivative trading books, and formulate compliance disclosures for the South African Reserve Bank (SARB) and international regulators.",
            required_skills="Risk Analysis, Financial Modeling, SQL, Python, IFRS, Analytical",
            field_of_study="Finance & Accounting",
            location="Sandton, Johannesburg",
            salary_stipend=30000,
            duration_months=12,
            closing_date=date.today() + timedelta(days=36),
            is_active=True,
        ),
        # --- 14. Human Resources & People Operations (Discovery) ---
        Opportunity(
            company_id=c_disc.id,
            title="Graduate People & Culture Business Partner",
            opportunity_type="internship",
            description="Participate in university recruitment roadshows, manage performance appraisal analytics for tech teams, administer leadership talent pipelines, and design progressive employee wellness initiatives.",
            required_skills="Communication, Team Management, Project Management, Conflict Resolution, Empathy",
            field_of_study="Human Resources & Business",
            location="Sandton, Johannesburg",
            salary_stipend=18000,
            duration_months=12,
            closing_date=date.today() + timedelta(days=32),
            is_active=True,
        ),
        # --- 15. UI/UX Product Design (Discovery Digital) ---
        Opportunity(
            company_id=c_disc.id,
            title="Junior Digital Product Designer (UI/UX & Mobile App)",
            opportunity_type="internship",
            description="Design next-generation interfaces for the Discovery Banking & Vitality mobile applications in Figma. Conduct qualitative user research, formulate interactive micro-prototypes, and collaborate with iOS/Android engineers.",
            required_skills="Figma, UI/UX Design, Prototyping, Brand Strategy, User Research, Design Systems",
            field_of_study="Design & Creative Arts",
            location="Sandton / Remote",
            salary_stipend=20500,
            duration_months=12,
            closing_date=date.today() + timedelta(days=40),
            is_active=True,
        ),
        # --- 16. Sustainability & ESG Engineering (Sasol) ---
        Opportunity(
            company_id=c_sasol.id,
            title="ESG Sustainability & Decarbonization Fellow",
            opportunity_type="internship",
            description="Assess greenhouse gas emissions across chemical manufacturing complexes, measure industrial wastewater treatment metrics, and formulate sustainability reports adhering to the Taskforce on Climate-Related Financial Disclosures (TCFD).",
            required_skills="Research, Environmental Science, Quality Assurance, Analytical, Technical Writing",
            field_of_study="Environmental Science & Engineering",
            location="Rosebank, Johannesburg",
            salary_stipend=23000,
            duration_months=12,
            closing_date=date.today() + timedelta(days=48),
            is_active=True,
        ),
        # --- 17. Supply Chain & Logistics (Sasol Chemical) ---
        Opportunity(
            company_id=c_sasol.id,
            title="Global Supply Chain Logistics & Telematics Trainee",
            opportunity_type="learnership",
            description="Optimise international freight shipping schedules from Durban harbor, manage bulk chemical rail dispatch with Transnet, and audit warehouse safety procedures under ISO 9001.",
            required_skills="Supply Chain, Project Management, Data Analysis, Quality Assurance, Communication",
            field_of_study="Supply Chain & Operations",
            location="Durban & Johannesburg",
            salary_stipend=17500,
            duration_months=12,
            closing_date=date.today() + timedelta(days=26),
            is_active=True,
        ),
        # --- 18. Strategy & Management Consulting (Deloitte) ---
        Opportunity(
            company_id=c_deloitte.id,
            title="Junior Strategy & Business Operations Consultant",
            opportunity_type="entry-level",
            description="Formulate strategic operating models for telecommunications and banking clients. Structure revenue turnaround plans, build competitive market entry models, and present synthesis decks to C-suite executives.",
            required_skills="Analytical, Financial Modeling, Presentation, Strategic Planning, Communication",
            field_of_study="Business & Management",
            location="Waterfall City, Midrand",
            salary_stipend=31000,
            duration_months=12,
            closing_date=date.today() + timedelta(days=50),
            is_active=True,
        ),
        # --- 19. Cyber Security & Forensics (Deloitte Cyber) ---
        Opportunity(
            company_id=c_deloitte.id,
            title="Associate Cyber Threat Intelligence & Forensics Analyst",
            opportunity_type="internship",
            description="Monitor security operations center (SOC) event telemetry, execute vulnerability assessments across enterprise cloud networks, and support digital forensics investigations during incident response mandates.",
            required_skills="Python, Linux, Network Security, SQL, Critical Thinking, Ethical Hacking",
            field_of_study="Information Technology",
            location="Midrand & Cape Town",
            salary_stipend=25500,
            duration_months=12,
            closing_date=date.today() + timedelta(days=35),
            is_active=True,
        ),
        # --- 20. Legal Compliance & AML (Standard Bank CIB) ---
        Opportunity(
            company_id=c_sbg.id,
            title="Junior Financial Crime Compliance & Anti-Money Laundering Analyst",
            opportunity_type="entry-level",
            description="Investigate suspicious corporate transactional activities under the Financial Intelligence Centre Act (FICA), verify sanctions list compliance, and submit statutory regulatory disclosures.",
            required_skills="Legal Research, Analytical, Compliance, Financial Regulations, Communication",
            field_of_study="Law & Legal Studies",
            location="Sandton Central, Johannesburg",
            salary_stipend=27000,
            duration_months=12,
            closing_date=date.today() + timedelta(days=40),
            is_active=True,
        ),
        # --- 21. Frontend Software Engineering (Discovery) ---
        Opportunity(
            company_id=c_disc.id,
            title="Associate Web Application Developer (React & TypeScript)",
            opportunity_type="entry-level",
            description="Build customer onboarding interfaces for Discovery Bank. Implement state management with Redux, build reusable UI component libraries, and optimise client-side bundle load speeds.",
            required_skills="JavaScript, TypeScript, React, HTML/CSS, Git, REST APIs",
            field_of_study="Information Technology",
            location="1 Discovery Place, Sandton",
            salary_stipend=24500,
            duration_months=12,
            closing_date=date.today() + timedelta(days=30),
            is_active=True,
        ),
        # --- 22. Chemical Process Engineering (Sasol) ---
        Opportunity(
            company_id=c_sasol.id,
            title="Graduate Chemical Process Optimisation Engineer",
            opportunity_type="entry-level",
            description="Simulate continuous distillation columns and reactor thermodynamics in Aspen Plus. Troubleshoot catalyst deactivation parameters and implement energy efficiency pinch technology on chemical synthesis loops.",
            required_skills="Chemical Engineering, Aspen Plus, Thermodynamics, Process Safety, Analytical",
            field_of_study="Engineering",
            location="Sasolburg, Free State",
            salary_stipend=29000,
            duration_months=24,
            closing_date=date.today() + timedelta(days=45),
            is_active=True,
        ),
        # --- 23. Tax & Transfer Pricing (Bowmans / Deloitte) ---
        Opportunity(
            company_id=c_bowmans.id,
            title="International Tax & Cross-Border Advisory Trainee",
            opportunity_type="internship",
            description="Conduct transfer pricing economic analyses, calculate withholding tax liabilities across Sub-Saharan African jurisdictions, and draft legal opinion memoranda under double taxation agreements.",
            required_skills="Tax Strategy, Legal Research, Financial Analysis, Writing, Analytical",
            field_of_study="Finance & Accounting",
            location="Sandton, Johannesburg",
            salary_stipend=25000,
            duration_months=12,
            closing_date=date.today() + timedelta(days=55),
            is_active=True,
        ),
        # --- 24. Anomalous / Flagged Listing (QuickCash Loans) ---
        Opportunity(
            company_id=c_shady.id,
            title="EASY ONLINE DATA TYPIST - R65,000 GUARANTEED DAILY PAYOUTS!!!",
            opportunity_type="entry-level",
            description="Earn huge cash from your smartphone! No qualification, CV, or interviews needed. Just deposit registration verification fee and receive immediate payouts today!",
            required_skills="",
            field_of_study="",
            location="Anywhere / Unknown",
            salary_stipend=65000,
            duration_months=1,
            closing_date=date.today() + timedelta(days=10),
            is_active=True,
        ),
    ]

    for opp in opportunities:
        db.session.add(opp)

    db.session.flush()

    # =========================================================================
    # 5. DROPGUARD™ FRAUD DETECTION SCREENING (Screen listing #24 & Students)
    # =========================================================================
    print("Running DropGuard™ automated fraud detection model...")
    try:
        from datetime import datetime
        engine = get_engine(app.config["MODEL_DIR"])
        shady_opp = opportunities[-1]
        result = engine.assess_listing({
            "salary_stipend": shady_opp.salary_stipend,
            "duration_months": shady_opp.duration_months,
            "description_length": len(shady_opp.description),
            "required_skills_count": 0,
            "company_age_years": c_shady.company_age_years,
            "listings_posted_last_7_days": 1,
            "company_verified": int(bool(c_shady.verified)),
        })
        shady_opp.anomaly_score = result["anomaly_score"]
        shady_opp.is_flagged = result["is_flagged"]
        if result["is_flagged"]:
            shady_opp.flag_reason = result["top_factors"]

        # Also pre-compute student disengagement risk assessments
        all_students = [s_thabo, s_ayanda, s_sipho, s_chloe, s_lerato]
        for s in all_students:
            s_res = engine.assess_student(s)
            assessment = RiskAssessment(
                student_id=s.id,
                risk_label=s_res["risk_label"],
                risk_probability=s_res["risk_probability"],
                top_factors=s_res["top_factors"],
                assessed_at=datetime.utcnow(),
            )
            db.session.add(assessment)
    except Exception as e:
        print(f"DropGuard notice: {e}")

    # =========================================================================
    # 6. SEED PRE-EXISTING CANDIDATE APPLICATIONS ACROSS FACULTIES
    # =========================================================================
    print("Creating candidate applications and historical reviews...")

    # Thabo (IT) applied to Cloud Platform Engineer & ML Fellow
    app1 = Application(
        student_id=s_thabo.id, opportunity_id=opportunities[2].id, status="shortlisted",
        match_score=compute_match_score(s_thabo.skills_list(), s_thabo.field_of_study, opportunities[2])
    )
    app1.add_status_change("reviewed", "Application reviewed by hiring team")
    app1.add_status_change("shortlisted", "Candidate shortlisted for interview")
    db.session.add(app1)

    app2 = Application(
        student_id=s_thabo.id, opportunity_id=opportunities[3].id, status="reviewed",
        match_score=compute_match_score(s_thabo.skills_list(), s_thabo.field_of_study, opportunities[3])
    )
    app2.add_status_change("reviewed", "Application under review")
    db.session.add(app2)

    app3 = Application(
        student_id=s_thabo.id, opportunity_id=opportunities[18].id, status="accepted",
        match_score=compute_match_score(s_thabo.skills_list(), s_thabo.field_of_study, opportunities[18])
    )
    app3.add_status_change("reviewed", "Initial review completed")
    app3.add_status_change("shortlisted", "Advanced to interview stage")
    app3.add_status_change("accepted", "Offer accepted - congratulations!")
    db.session.add(app3)

    # Ayanda (Finance) applied to Investment Banking & SAICA Trainee
    app4 = Application(
        student_id=s_ayanda.id, opportunity_id=opportunities[0].id, status="shortlisted",
        match_score=compute_match_score(s_ayanda.skills_list(), s_ayanda.field_of_study, opportunities[0])
    )
    app4.add_status_change("reviewed", "Credentials verified")
    app4.add_status_change("shortlisted", "Shortlisted for final interview")
    db.session.add(app4)

    app5 = Application(
        student_id=s_ayanda.id, opportunity_id=opportunities[1].id, status="accepted",
        match_score=compute_match_score(s_ayanda.skills_list(), s_ayanda.field_of_study, opportunities[1])
    )
    app5.add_status_change("reviewed", "SAICA qualification confirmed")
    app5.add_status_change("shortlisted", "Interview completed successfully")
    app5.add_status_change("accepted", "SAICA articles position secured")
    db.session.add(app5)

    app6 = Application(
        student_id=s_ayanda.id, opportunity_id=opportunities[12].id, status="reviewed",
        match_score=compute_match_score(s_ayanda.skills_list(), s_ayanda.field_of_study, opportunities[12])
    )
    app6.add_status_change("reviewed", "Application under assessment")
    db.session.add(app6)

    # Sipho (Engineering) applied to Plant Reliability & Civil Infrastructure
    app7 = Application(
        student_id=s_sipho.id, opportunity_id=opportunities[4].id, status="shortlisted",
        match_score=compute_match_score(s_sipho.skills_list(), s_sipho.field_of_study, opportunities[4])
    )
    app7.add_status_change("reviewed", "Engineering credentials reviewed")
    app7.add_status_change("shortlisted", "Shortlisted for technical assessment")
    db.session.add(app7)

    app8 = Application(
        student_id=s_sipho.id, opportunity_id=opportunities[5].id, status="submitted",
        match_score=compute_match_score(s_sipho.skills_list(), s_sipho.field_of_study, opportunities[5])
    )
    db.session.add(app8)

    app9 = Application(
        student_id=s_sipho.id, opportunity_id=opportunities[6].id, status="reviewed",
        match_score=compute_match_score(s_sipho.skills_list(), s_sipho.field_of_study, opportunities[6])
    )
    app9.add_status_change("reviewed", "Application under review")
    db.session.add(app9)

    # Chloe (Marketing) applied to Brand Strategy & Executive PR
    app10 = Application(
        student_id=s_chloe.id, opportunity_id=opportunities[7].id, status="shortlisted",
        match_score=compute_match_score(s_chloe.skills_list(), s_chloe.field_of_study, opportunities[7])
    )
    app10.add_status_change("reviewed", "Portfolio reviewed")
    app10.add_status_change("shortlisted", "Shortlisted for creative presentation")
    db.session.add(app10)

    app11 = Application(
        student_id=s_chloe.id, opportunity_id=opportunities[8].id, status="reviewed",
        match_score=compute_match_score(s_chloe.skills_list(), s_chloe.field_of_study, opportunities[8])
    )
    app11.add_status_change("reviewed", "Application under review")
    db.session.add(app11)

    # Lerato (Healthcare) has 1 older application
    app12 = Application(
        student_id=s_lerato.id, opportunity_id=opportunities[9].id, status="submitted",
        match_score=compute_match_score(s_lerato.skills_list(), s_lerato.field_of_study, opportunities[9])
    )
    db.session.add(app12)

    db.session.commit()
    print("Database successfully seeded with 24 multi-disciplinary career listings and authentic demo accounts!")

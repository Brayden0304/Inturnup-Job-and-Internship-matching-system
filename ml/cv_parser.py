"""
LaunchPad - Resume & CV Profile Extraction Engine
=================================================
Heuristic NLP & Taxonomy-driven parser that extracts structured student profile data:
- Full Name
- Qualification / Degree
- Field of Study
- Multi-Disciplinary Skills
- Location & Contact Region
- Years of Experience / Graduation Cohort
- Executive Bio / Summary
- Interests & Career Aspirations
"""
import re

# Comprehensive taxonomy of skills across all modern faculties
SKILL_TAXONOMY = {
    # Information Technology & Data
    "Python": ["python", "python3", "py"],
    "Java": ["java", "jvm", "spring"],
    "Golang": ["golang", "go programming", "go lang"],
    "C++": ["c++", "cpp"],
    "SQL": ["sql", "postgresql", "postgres", "mysql", "sqlite", "relational database"],
    "Docker": ["docker", "containerization", "containers"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "Azure": ["azure", "microsoft azure"],
    "Git": ["git", "github", "gitlab", "version control"],
    "Linux": ["linux", "bash", "unix", "shell scripting"],
    "CI/CD": ["ci/cd", "ci cd", "continuous integration", "github actions"],
    "Machine Learning": ["machine learning", "ml", "scikit-learn", "deep learning", "tensorflow", "pytorch"],
    "Data Science": ["data science", "pandas", "numpy", "jupyter"],
    "Distributed Systems": ["distributed systems", "microservices", "message queues", "grpc"],
    "JavaScript": ["javascript", "js", "typescript", "react", "node", "nodejs"],
    "Cybersecurity": ["cybersecurity", "soc", "siem", "penetration testing", "network security"],
    
    # Finance & Accounting
    "Financial Modeling": ["financial modeling", "financial modelling", "dcf", "valuation modeling"],
    "IFRS": ["ifrs", "ifrs standards", "ifrs 9", "ifrs 15", "ifrs 16"],
    "Auditing": ["auditing", "statutory audit", "internal audit", "isa standards"],
    "GAAP": ["gaap", "generally accepted accounting"],
    "Valuation": ["valuation", "company valuation", "dcf valuation", "lbo"],
    "Advanced Excel": ["advanced excel", "excel modeling", "vlookup", "xlookup", "pivot tables"],
    "Tax Strategy": ["tax", "taxation", "corporate tax", "vat", "sars"],
    "Risk Analysis": ["risk analysis", "risk management", "credit risk", "market risk"],
    "Corporate Finance": ["corporate finance", "capital markets", "m&a", "mergers and acquisitions"],
    "SAICA": ["saica", "saica trainee", "cta", "itc", "apc"],
    
    # Engineering
    "SolidWorks": ["solidworks", "solid works"],
    "AutoCAD": ["autocad", "cad modeling", "drafting"],
    "MATLAB": ["matlab", "simulink"],
    "FEA Simulation": ["fea", "finite element", "simulation", "ansys"],
    "Thermodynamics": ["thermodynamics", "thermal dynamics", "heat transfer"],
    "PLC Automation": ["plc", "programmable logic", "scada", "automation"],
    "Project Management": ["project management", "agile", "scrum", "prince2"],
    "ECSA Guidelines": ["ecsa", "candidate engineer", "engineering council"],
    "Renewable Energy": ["renewable energy", "solar", "photovoltaic", "clean energy"],
    "Process Engineering": ["process engineering", "chemical engineering", "plant design"],
    
    # Marketing & Communications
    "Brand Strategy": ["brand strategy", "branding", "brand architecture"],
    "Omnichannel Marketing": ["omnichannel", "digital marketing", "multi-channel"],
    "Copywriting": ["copywriting", "content strategy", "editorial writing"],
    "Public Relations": ["public relations", "pr", "media relations", "press release"],
    "Google Analytics 4": ["google analytics", "ga4", "analytics"],
    "SEO": ["seo", "search engine optimization", "sem"],
    "Crisis Communications": ["crisis communications", "reputation management"],
    "Social Media Strategy": ["social media", "meta blueprint", "community management"],
    
    # Healthcare & Clinical Sciences
    "Patient Care": ["patient care", "nursing care", "bedside care"],
    "Clinical Protocols": ["clinical protocols", "clinical procedures", "infection control"],
    "Triage": ["triage", "emergency triage", "acute care"],
    "Pharmacology Basics": ["pharmacology", "pharmacotherapy", "drug administration"],
    "Healthcare Informatics": ["health informatics", "clinical records", "emr", "ehr"],
    "SANC Registration": ["sanc", "nursing council", "registered nurse"],
    
    # Law & Governance
    "Contract Law": ["contract law", "contract drafting", "commercial agreements"],
    "Commercial Litigation": ["litigation", "commercial litigation", "dispute resolution"],
    "M&A Due Diligence": ["due diligence", "regulatory compliance", "mergers"],
    "Corporate Governance": ["corporate governance", "king iv", "compliance"],
}

LOCATION_KEYWORDS = [
    "Johannesburg", "Sandton", "Braamfontein", "Rosebank", "Pretoria", "Hatfield",
    "Cape Town", "Rondebosch", "Stellenbosch", "Durban", "Berea", "Midrand",
    "Centurion", "Gauteng", "Western Cape", "KwaZulu-Natal", "Remote"
]

FACULTY_MAP = [
    ("Information Technology", [
        "computer science", "software", "information technology", "informatics",
        "data science", "cyber security", "ai", "cloud", "bsc it", "systems"
    ]),
    ("Finance & Accounting", [
        "accounting", "finance", "bcom", "cta", "saica", "ca(sa)", "chartered accountant",
        "taxation", "auditing", "investment", "banking", "economics", "actuarial"
    ]),
    ("Engineering", [
        "engineering", "mechanical", "electrical", "civil", "chemical", "mechatronics",
        "industrial", "beng", "bsc eng", "solidworks", "ecsa"
    ]),
    ("Marketing & Communications", [
        "marketing", "brand", "communications", "media", "public relations",
        "advertising", "journalism", "digital strategy"
    ]),
    ("Healthcare & Nursing", [
        "nursing", "medicine", "clinical", "healthcare", "bcur", "mbchb", "pharmacy",
        "medical", "patient care", "hospital"
    ]),
    ("Law & Governance", [
        "law", "llb", "legal", "advocate", "attorney", "litigation", "jurisprudence"
    ]),
]


def parse_cv_text(text: str) -> dict:
    """Extracts structured fields from raw CV/Resume text."""
    if not text or not text.strip():
        return {}

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned_lower = text.lower()

    # 1. Candidate Full Name
    # Strategy: Scan top lines for common name patterns or "Name:" labels
    name = ""
    for line in lines[:8]:
        name_match = re.search(r"(?:name|candidate|applicant)\s*[:\-]?\s*([A-Za-z\s'\-]+)", line, re.I)
        if name_match:
            name = name_match.group(1).strip()
            break
        # First short line that looks like a clean capitalized 2-4 word name
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
            if not any(k in line.lower() for k in ["curriculum", "resume", "cv", "page", "email", "phone", "university"]):
                name = line.strip()
                break

    if not name and lines:
        first_line = lines[0]
        if len(first_line.split()) <= 4 and not any(k in first_line.lower() for k in ["cv", "resume", "curriculum"]):
            name = first_line

    # 2. Degree / Qualification
    qualification = ""
    deg_patterns = [
        r"(BSc\s*(?:\(Hons\))?[^,\n\r]+)",
        r"(BCom\s*(?:\(Hons\))?[^,\n\r]+)",
        r"(BEng\s*(?:\(Hons\))?[^,\n\r]+)",
        r"(BCur\s*(?:\(Hons\))?[^,\n\r]+)",
        r"(BA\s*(?:\(Hons\))?[^,\n\r]+)",
        r"(LLB[^,\n\r]+)",
        r"(Bachelor\s+of\s+[^,\n\r]+)",
        r"(Master\s+of\s+[^,\n\r]+)",
        r"(Diploma\s+in\s+[^,\n\r]+)",
        r"(Honours\s+in\s+[^,\n\r]+)",
    ]
    for pattern in deg_patterns:
        match = re.search(pattern, text, re.I)
        if match:
            qualification = match.group(1).strip()
            # Clean trailing punctuation
            qualification = re.sub(r"[\.\;]+$", "", qualification)
            break

    # 3. Field of Study / Faculty
    field_of_study = "Information Technology"
    for faculty, keywords in FACULTY_MAP:
        if any(kw in cleaned_lower for kw in keywords):
            field_of_study = faculty
            break

    # 4. Multi-Disciplinary Skills
    detected_skills = []
    for skill_name, aliases in SKILL_TAXONOMY.items():
        for alias in aliases:
            # Word boundary matching
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, cleaned_lower):
                detected_skills.append(skill_name)
                break

    # 5. Location
    location = "Johannesburg"
    for loc in LOCATION_KEYWORDS:
        if re.search(r"\b" + re.escape(loc) + r"\b", text, re.I):
            location = loc
            break

    # 6. Experience Years
    experience_years = 1.0
    exp_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)(?:\s+of)?\s*(?:experience|work)", cleaned_lower)
    if exp_match:
        try:
            experience_years = float(exp_match.group(1))
        except ValueError:
            experience_years = 1.0
    elif any(k in cleaned_lower for k in ["final-year", "final year", "honours", "graduate"]):
        experience_years = 1.0
    elif any(k in cleaned_lower for k in ["internship", "vacation work", "assistant"]):
        experience_years = 0.5

    # 7. Interests
    interests = []
    if "machine learning" in cleaned_lower or "cloud" in cleaned_lower:
        interests.append("Cloud Architecture & Distributed Systems")
    if "investment" in cleaned_lower or "valuation" in cleaned_lower or "m&a" in cleaned_lower:
        interests.append("Corporate Finance & Investment Advisory")
    if "energy" in cleaned_lower or "automation" in cleaned_lower:
        interests.append("Industrial Automation & Clean Energy")
    if "brand" in cleaned_lower or "creative" in cleaned_lower:
        interests.append("Brand Architecture & Digital Strategy")
    if "clinical" in cleaned_lower or "hospital" in cleaned_lower:
        interests.append("Pediatric & Clinical Healthcare")
    if not interests:
        interests = [f"{field_of_study} Progression", "Professional Practice"]

    # 8. Bio / Summary Generation
    bio = ""
    # Look for Summary / Profile section in CV
    summary_match = re.search(r"(?:profile|summary|about\s+me|objective)\s*[:\-]?\s*([^\n\r]+(?:\n[^\n\r]+){1,3})", text, re.I)
    if summary_match:
        bio = summary_match.group(1).strip()
    else:
        # Generate an executive synthesis
        skills_summary = ", ".join(detected_skills[:5]) if detected_skills else "strategic core competencies"
        bio = (
            f"Candidate specializing in {field_of_study} with foundational focus in {skills_summary}. "
            f"Demonstrated technical proficiency and collaborative execution in institutional academic programs."
        )

    return {
        "full_name": name or "Candidate Profile",
        "qualification": qualification or f"Bachelor in {field_of_study}",
        "field_of_study": field_of_study,
        "skills": ", ".join(detected_skills) if detected_skills else "Communication, Project Management, Analysis",
        "interests": ", ".join(interests),
        "bio": bio,
        "location": location,
        "experience_years": experience_years,
        "skills_count": len(detected_skills),
    }

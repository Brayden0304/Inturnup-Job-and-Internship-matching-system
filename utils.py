"""
Utility functions for scoring, data normalization, title-case formatting,
and comprehensive input validation.
"""
from datetime import datetime, date
import re
from urllib.parse import urlparse


def format_title_case(text):
    """
    Format names, institutions, and job titles to title case with proper
    capitalization of each word while preserving common industry acronyms.
    """
    if not text or not isinstance(text, str):
        return text or ""

    # Clean multiple spaces
    text = " ".join(text.strip().split())
    if not text:
        return ""

    acronyms = {
        "IT", "AI", "AWS", "UI", "UX", "ML", "SQL", "SAICA", "CISA",
        "LLB", "BSC", "BCOM", "BA", "CA(SA)", "HR", "CEO", "CTO", "CFO",
        "SME", "API", "QA"
    }
    minor_words = {"and", "of", "in", "the", "for", "to", "at", "by", "with", "&"}

    words = text.split(" ")
    formatted = []

    for i, word in enumerate(words):
        clean = word.strip("(),.-/").upper()
        if clean in acronyms:
            prefix = word[: len(word) - len(word.lstrip("(),.-/"))]
            suffix = word[len(word.rstrip("(),.-/")) :]
            formatted.append(f"{prefix}{clean}{suffix}")
        elif i > 0 and word.lower() in minor_words:
            formatted.append(word.lower())
        else:
            formatted.append(word.capitalize())

    return " ".join(formatted)


def compute_match_score(student_skills, student_field, opportunity):
    """
    Compute explainable match score (0-100) based on skill overlap and
    field-of-study alignment to power recommendations and search ranking.
    """
    required = set(s.lower() for s in opportunity.required_skills_list())
    student_set = set(s.lower() for s in student_skills)

    if required:
        overlap = len(required & student_set) / len(required)
    else:
        overlap = 0.5  # neutral if listing didn't specify skills

    field_bonus = 0.0
    if student_field and opportunity.field_of_study:
        if student_field.strip().lower() == opportunity.field_of_study.strip().lower():
            field_bonus = 0.2

    score = min(1.0, overlap * 0.8 + field_bonus + (0.0 if required else 0.0))
    return round(score * 100, 1)


# ============================================================================
# Robust Validation & Sanitization Helpers
# ============================================================================

def validate_email(email):
    """
    Validates that the email address and email name (local-part) are syntactically and logically valid.
    Checks:
      - Valid email name (1-64 chars, no consecutive dots, proper alphanumeric start/end)
      - Exactly one '@' symbol
      - Valid domain structure with labels and top-level domain (TLD >= 2 chars)
      - No invalid symbols or spaces
    Returns (is_valid: bool, error_or_cleaned_email: str).
    """
    if not email or not isinstance(email, str):
        return False, "Email address is required."

    cleaned = email.strip().lower()
    if len(cleaned) < 5 or len(cleaned) > 254:
        return False, "Email address must be between 5 and 254 characters long."

    if " " in cleaned:
        return False, "Email address cannot contain spaces."

    if cleaned.count("@") != 1:
        return False, "Email address must contain exactly one '@' symbol."

    local_part, domain_part = cleaned.split("@")

    # Local-part (email name) validation
    if not local_part or len(local_part) > 64:
        return False, "Email name portion must be between 1 and 64 characters."

    if local_part.startswith(".") or local_part.endswith("."):
        return False, "Email name cannot start or end with a dot."

    if ".." in local_part:
        return False, "Email name cannot contain consecutive dots."

    # RFC 5322 compliant characters in local-part
    if not re.match(r"^[a-zA-Z0-9_!#$%&'*+/=?`{|}~^-]+(?:\.[a-zA-Z0-9_!#$%&'*+/=?`{|}~^-]+)*$", local_part):
        return False, "Email name contains invalid characters."

    # Domain-part validation
    if not domain_part or len(domain_part) > 253:
        return False, "Email domain portion is invalid."

    if domain_part.startswith(".") or domain_part.endswith("."):
        return False, "Email domain cannot start or end with a dot."

    if ".." in domain_part:
        return False, "Email domain cannot contain consecutive dots."

    if "." not in domain_part:
        return False, "Email domain must contain a valid domain extension (e.g. .com or .ac.za)."

    domain_labels = domain_part.split(".")
    for label in domain_labels:
        if not label:
            return False, "Email domain label cannot be empty."
        if len(label) > 63:
            return False, "Email domain label is too long."
        if label.startswith("-") or label.endswith("-"):
            return False, "Email domain label cannot start or end with a hyphen."
        if not re.match(r"^[a-zA-Z0-9-]+$", label):
            return False, "Email domain contains invalid characters."

    tld = domain_labels[-1]
    if len(tld) < 2 or not tld.isalpha():
        return False, "Email must have a valid top-level domain with at least 2 letters (e.g. .com, .za)."

    return True, cleaned


# Carefully reviewed, explicit domains for public self-registration. Adding a
# custom university/employer domain is a policy decision; add it to this set
# after checking the exact official domain. This is not mailbox verification.
APPROVED_REGISTRATION_EMAIL_DOMAINS = frozenset({
    # Major public email services (exact domains only)
    "gmail.com", "googlemail.com", "outlook.com", "hotmail.com",
    "live.com", "msn.com", "yahoo.com", "yahoo.co.uk",
    "icloud.com", "me.com", "mac.com", "aol.com", "proton.me",
    "protonmail.com", "zoho.com", "fastmail.com",
    # South African universities and institution/student domains
    "wits.ac.za", "students.wits.ac.za", "uct.ac.za", "students.uct.ac.za",
    "up.ac.za", "students.up.ac.za", "ukzn.ac.za", "students.ukzn.ac.za",
    "sun.ac.za", "students.sun.ac.za", "uj.ac.za",
    "unisa.ac.za", "mylife.unisa.ac.za", "nwu.ac.za",
    "ufs.ac.za", "uwc.ac.za",
    "ru.ac.za", "dut.ac.za", "tut.ac.za", "cput.ac.za",
    "cut.ac.za", "ul.ac.za", "ufh.ac.za", "unizulu.ac.za",
    "mandela.ac.za", "wsu.ac.za", "vut.ac.za",
    "richfield.ac.za",
    # Selected established employers with public official domains
    "standardbank.co.za", "discovery.co.za", "sasol.com",
    "deloitte.co.za", "bowmanslaw.com", "capitecbank.co.za",
    "absa.co.za", "fnb.co.za", "nedbank.co.za", "microsoft.com",
    "google.com", "apple.com", "amazon.com", "ibm.com",
    "accenture.com", "pwc.com", "ey.com", "vodacom.co.za",
    "mtn.com", "wbho.co.za",  # WBHO official contact: wbhoho@wbho.co.za
})


def validate_registration_email(email):
    """Allow only expressly approved exact public domains for new sign-ups.

    A real-looking domain, DNS records, or even a live website do not prove an
    individual email inbox exists or is controlled by the person signing up.
    Login remains backwards compatible with users already in the database.
    """
    valid, normalized_or_error = validate_email(email)
    if not valid:
        return False, normalized_or_error
    domain = normalized_or_error.rsplit("@", 1)[1]
    if domain not in APPROVED_REGISTRATION_EMAIL_DOMAINS:
        return False, ("Email domain is not approved for new accounts. "
                       "Use an email from an approved provider, university, or verified company domain.")
    return True, normalized_or_error


def validate_student_name(name):
    """
    Validates a student/candidate full name.
    Accepts letters (including international characters), spaces, hyphens, apostrophes, and periods.
    Rejects numbers, special symbols, and purely whitespace or single characters.
    Returns (is_valid: bool, error_or_formatted_name: str).
    """
    if not name or not isinstance(name, str):
        return False, "Full name is required."

    cleaned = " ".join(name.strip().split())
    if len(cleaned) < 2:
        return False, "Full name must be at least 2 characters long."
    if len(cleaned) > 100:
        return False, "Full name cannot exceed 100 characters."

    letter_count = sum(1 for c in cleaned if c.isalpha())
    if letter_count < 2:
        return False, "Full name must contain at least 2 letters."

    if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s'.-]+$", cleaned):
        return False, "Full name cannot contain numbers or special symbols."

    if re.search(r"\bhitler\b", cleaned, flags=re.IGNORECASE):
        return False, "Please choose an appropriate display name."

    return True, format_title_case(cleaned)


def validate_company_name(name):
    """
    Validates an enterprise / corporate partner company name.
    Accepts letters, numbers, spaces, and standard business punctuation (&, ., -, ', ,, (), /).
    Requires at least one letter and minimum 2 characters.
    Returns (is_valid: bool, error_or_formatted_name: str).
    """
    if not name or not isinstance(name, str):
        return False, "Company name is required."

    cleaned = " ".join(name.strip().split())
    if len(cleaned) < 2:
        return False, "Company name must be at least 2 characters long."
    if len(cleaned) > 120:
        return False, "Company name cannot exceed 120 characters."

    if not any(c.isalpha() for c in cleaned):
        return False, "Company name must contain letters."

    if not re.match(r"^[A-Za-z0-9À-ÖØ-öø-ÿ\s&',.\(\)/\-]+$", cleaned):
        return False, "Company name contains invalid characters."

    if re.search(r"\bhitler\b", cleaned, flags=re.IGNORECASE):
        return False, "Please choose an appropriate company name."

    return True, format_title_case(cleaned)


def validate_url(url, optional=True):
    """
    Validates and normalizes website URLs.
    Ensures safe schemes (http, https) and valid domain syntax.
    Returns (is_valid: bool, error_or_normalized_url: str).
    """
    if not url or not isinstance(url, str):
        if optional:
            return True, ""
        return False, "Website URL is required."

    cleaned = url.strip()
    if not cleaned:
        if optional:
            return True, ""
        return False, "Website URL is required."

    lower = cleaned.lower()
    if lower.startswith(("javascript:", "data:", "file:", "vbscript:", "blob:")):
        return False, "Invalid URL protocol."

    if not lower.startswith(("http://", "https://")):
        cleaned = "https://" + cleaned

    try:
        parsed = urlparse(cleaned)
        if parsed.scheme not in ("http", "https"):
            return False, "Website URL must use http:// or https://"

        netloc = parsed.netloc.split(":")[0]
        if not netloc or "." not in netloc:
            return False, "Website URL must include a valid domain name."

        labels = netloc.split(".")
        if any(not l for l in labels) or len(labels[-1]) < 2:
            return False, "Website URL contains an invalid domain name."

        return True, cleaned
    except Exception:
        return False, "Invalid website URL format."


def validate_number(value, field_name="Value", min_val=0.0, max_val=None, is_int=False, default=0):
    """
    Validates numeric input within specified bounds.
    Returns (is_valid: bool, cleaned_value, error_message: str).
    """
    if value is None or str(value).strip() == "":
        return True, default, ""

    try:
        num = int(value) if is_int else float(value)
    except (ValueError, TypeError):
        return False, default, f"{field_name} must be a valid number."

    if min_val is not None and num < min_val:
        return False, default, f"{field_name} cannot be less than {min_val}."

    if max_val is not None and num > max_val:
        return False, default, f"{field_name} cannot exceed {max_val}."

    return True, num, ""


def validate_closing_date(date_str):
    """
    Validates an opportunity closing date string (YYYY-MM-DD).
    Ensures format is valid and not in the past.
    Returns (is_valid: bool, date_obj, error_message: str).
    """
    if not date_str or not str(date_str).strip():
        return True, None, ""

    cleaned = str(date_str).strip()
    try:
        parsed_date = datetime.strptime(cleaned, "%Y-%m-%d").date()
    except ValueError:
        return False, None, "Closing date must be in YYYY-MM-DD format."

    today = date.today()
    if parsed_date < today:
        return False, None, "Closing date cannot be in the past."

    return True, parsed_date, ""


def clean_comma_separated(text, max_items=50, max_item_len=60):
    """
    Cleans, deduplicates, and limits comma-separated entries (skills, interests).
    """
    if not text or not isinstance(text, str):
        return ""

    tokens = [t.strip() for t in text.split(",") if t.strip()]
    seen = set()
    cleaned = []

    for t in tokens:
        sanitized = re.sub(r"[<>]", "", t).strip()
        if not sanitized:
            continue
        if len(sanitized) > max_item_len:
            sanitized = sanitized[:max_item_len].strip()
        lower_t = sanitized.lower()
        if lower_t not in seen:
            seen.add(lower_t)
            cleaned.append(sanitized)
        if len(cleaned) >= max_items:
            break

    return ", ".join(cleaned)


def sanitize_text(text, max_length=2000):
    """
    Sanitizes free-form text by stripping HTML tags and excess whitespace.
    """
    if not text or not isinstance(text, str):
        return ""

    cleaned = re.sub(r"<[^>]*>", "", text)
    cleaned = " ".join(cleaned.split())
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length].strip()
    return cleaned

def validate_password(password):
    """
    Validates that a password:
    - Is at least 6 characters long
    - Contains at least one letter (alphabet)
    - Contains at least one number (digit)
    - Contains at least one special character
    Returns (is_valid, error_message_or_none)
    """
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must include at least one letter (alphabet)."
    if not re.search(r'\d', password):
        return False, "Password must include at least one number."
    if not re.search(r'[^A-Za-z0-9]', password):
        return False, "Password must include at least one special character (e.g. @, #, $, %, !)."
    return True, None

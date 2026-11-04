/**
 * Client-Side Validation and Interactivity Suite
 * Provides rigorous validation for emails, names, URLs, and data-specific inputs.
 */

// Exact approved domains come from the server, not a separately maintained JS list.
function approvedEmailDomains() {
  const data = document.getElementById("approvedEmailDomains");
  if (!data) return new Set();
  try { return new Set(JSON.parse(data.textContent || "[]")); }
  catch (_) { return new Set(); }
}

// Email syntax plus exact approved domain. This checks domain policy, not mailbox
// ownership; a confirmation email would be needed to verify ownership.
function isValidEmail(email) {
  if (!email || typeof email !== 'string') return false;
  const cleaned = email.trim();
  if (cleaned.length < 5 || cleaned.length > 254) return false;
  if (cleaned.includes(' ') || (cleaned.match(/@/g) || []).length !== 1) return false;

  const parts = cleaned.split('@');
  const local = parts[0];
  const domain = parts[1];

  // Local-part (email name) checks
  if (!local || local.length > 64) return false;
  if (local.startsWith('.') || local.endsWith('.') || local.includes('..')) return false;
  if (!/^[a-zA-Z0-9_!#$%&'*+/=?`{|}~^-]+(?:\.[a-zA-Z0-9_!#$%&'*+/=?`{|}~^-]+)*$/.test(local)) return false;

  // Domain checks
  if (!domain || domain.length > 253 || !domain.includes('.')) return false;
  if (domain.startsWith('.') || domain.endsWith('.') || domain.includes('..')) return false;

  const labels = domain.split('.');
  for (const label of labels) {
    if (!label || label.length > 63 || label.startsWith('-') || label.endsWith('-')) return false;
    if (!/^[a-zA-Z0-9-]+$/.test(label)) return false;
  }

  const tld = labels[labels.length - 1];
  if (tld.length < 2 || !/^[a-zA-Z]+$/.test(tld)) return false;
  return approvedEmailDomains().has(domain.toLowerCase());
}

// Student full name validation: letters, spaces, hyphens, apostrophes only
function isValidStudentName(name) {
  if (!name || typeof name !== 'string') return false;
  const cleaned = name.trim();
  if (cleaned.length < 2 || cleaned.length > 100) return false;
  const letters = (cleaned.match(/[a-zA-ZÀ-ÖØ-öø-ÿ]/g) || []).length;
  if (letters < 2) return false;
  if (/\bhitler\b/i.test(cleaned)) return false;
  return /^[A-Za-zÀ-ÖØ-öø-ÿ\s'.-]+$/.test(cleaned);
}

// Company name validation: letters, digits, and standard punctuation (&, ., -, ', ,, (), /)
function isValidCompanyName(name) {
  if (!name || typeof name !== 'string') return false;
  const cleaned = name.trim();
  if (cleaned.length < 2 || cleaned.length > 120) return false;
  if (!/[a-zA-Z]/.test(cleaned)) return false;
  if (/\bhitler\b/i.test(cleaned)) return false;
  return /^[A-Za-z0-9À-ÖØ-öø-ÿ\s&',.()/\\-]+$/.test(cleaned);
}

document.addEventListener("DOMContentLoaded", function () {
  // -------------------------------------------------------------
  // Registration Form Controls
  // -------------------------------------------------------------
  const loginForm = document.getElementById("loginForm");
  const loginEmail = document.getElementById("loginEmail");
  const loginEmailHint = document.getElementById("loginEmailHint");
  if (loginForm && loginEmail && loginEmailHint) {
    function validateLoginEmail() {
      const email = loginEmail.value.trim();
      if (!email) { loginEmailHint.style.display = "none"; return false; }
      // Existing accounts using legacy/demo domains must still be able to sign in.
      const approved = isValidEmail(email);
      loginEmailHint.style.display = approved ? "none" : "block";
      if (!approved) {
        loginEmailHint.textContent = "This domain is not approved for new accounts. Existing registered accounts may still sign in.";
      }
      return true;
    }
    loginEmail.addEventListener("input", validateLoginEmail);
    loginEmail.addEventListener("blur", validateLoginEmail);
    loginForm.addEventListener("submit", validateLoginEmail);
  }

  const tabStudent = document.getElementById("tabStudent");
  const tabCompany = document.getElementById("tabCompany");
  const nameLabel = document.getElementById("nameLabel");
  const registerName = document.getElementById("registerName");
  const registerEmail = document.getElementById("registerEmail");
  const registerPassword = document.getElementById("registerPassword");
  const registerForm = document.getElementById("registerForm");

  const nameHint = document.getElementById("nameHint");
  const emailHint = document.getElementById("emailHint");
  const passwordHint = document.getElementById("passwordHint");
  const strengthFill = document.getElementById("strengthFill");
  const strengthText = document.getElementById("strengthText");

  let currentRole = "student";
  const registerHeading = document.getElementById("registerHeading");

  function emailValidationMessage() {
    return currentRole === "company"
      ? "Enter a valid email at an approved employer domain (such as wbho.co.za) or recognized email provider."
      : "Enter a valid email at an approved email provider or university domain (such as gmail.com or wits.ac.za).";
  }

  if (tabStudent && tabCompany && registerForm) {
    function setActive(role) {
      currentRole = role === "company" ? "company" : "student";
      tabStudent.classList.toggle("active", currentRole === "student");
      tabCompany.classList.toggle("active", currentRole === "company");
      if (registerHeading) {
        registerHeading.textContent = currentRole === "company"
          ? "Register Your Company" : "Register As A Student";
      }
      if (nameLabel) nameLabel.textContent = currentRole === "company" ? "Company Name" : "Full Name";
      if (registerName) registerName.placeholder = currentRole === "company" ? "Enter company name" : "Enter your full name";
      validateNameField();
      if (registerEmail && registerEmail.value.trim()) validateEmailField();
    }

    const roleRadios = registerForm.querySelectorAll('input[name="role"]');
    roleRadios.forEach(radio => radio.addEventListener("change", () => setActive(radio.value)));
    const selectedRole = registerForm.querySelector('input[name="role"]:checked');
    setActive(selectedRole ? selectedRole.value : "student");
  }

  function validateNameField() {
    if (!registerName || !nameHint) return true;
    const val = registerName.value.trim();
    if (!val) {
      nameHint.style.display = "none";
      return false;
    }

    if (currentRole === "student") {
      if (!isValidStudentName(val)) {
        nameHint.style.display = "block";
        nameHint.textContent = "Please enter an appropriate full name using letters, spaces, and hyphens (minimum 2 characters).";
        return false;
      }
    } else {
      if (!isValidCompanyName(val)) {
        nameHint.style.display = "block";
        nameHint.textContent = "Please enter a valid company name (at least 2 characters with letters).";
        return false;
      }
    }
    nameHint.style.display = "none";
    return true;
  }

  function validateEmailField() {
    if (!registerEmail || !emailHint) return true;
    const val = registerEmail.value.trim();
    if (!val) {
      emailHint.style.display = "none";
      return false;
    }

    if (!isValidEmail(val)) {
      emailHint.style.display = "block";
      emailHint.textContent = emailValidationMessage();
      return false;
    }
    emailHint.style.display = "none";
    return true;
  }

  function validatePasswordField() {
    if (!registerPassword || !passwordHint) return true;
    const val = registerPassword.value;
    if (!val) {
      passwordHint.style.display = "none";
      return false;
    }

    if (val.length < 6) {
      passwordHint.style.display = "block";
      passwordHint.textContent = "Password must be at least 6 characters long.";
      return false;
    }
    if (!/[A-Za-z]/.test(val)) {
      passwordHint.style.display = "block";
      passwordHint.textContent = "Password must contain at least one letter.";
      return false;
    }
    if (!/[0-9]/.test(val)) {
      passwordHint.style.display = "block";
      passwordHint.textContent = "Password must contain at least one number.";
      return false;
    }
    if (!/[^A-Za-z0-9]/.test(val)) {
      passwordHint.style.display = "block";
      passwordHint.textContent = "Password must contain at least one special character (e.g. @, #, $, %, !).";
      return false;
    }
    passwordHint.style.display = "none";
    return true;
  }

  if (registerName) {
    registerName.addEventListener("input", validateNameField);
    registerName.addEventListener("blur", validateNameField);
  }

  if (registerEmail) {
    registerEmail.addEventListener("input", validateEmailField);
    registerEmail.addEventListener("blur", validateEmailField);
  }

  if (registerPassword) {
    registerPassword.addEventListener("input", function () {
      validatePasswordField();

      // Password strength meter with strict requirements
      if (strengthFill && strengthText) {
        const password = this.value;
        const hasLength = password.length >= 6;
        const hasLetter = /[A-Za-z]/.test(password);
        const hasNumber = /[0-9]/.test(password);
        const hasSpecial = /[^A-Za-z0-9]/.test(password);
        const hasUpper = /[A-Z]/.test(password);
        const hasLong = password.length >= 10;

        strengthFill.className = "strength-fill";
        strengthText.className = "strength-text";

        if (password.length === 0) {
          strengthFill.style.width = "0%";
          strengthText.textContent = "Password strength";
          strengthText.className = "strength-text";
        } else if (!hasLength || !hasLetter || !hasNumber || !hasSpecial) {
          strengthFill.style.width = "33%";
          strengthFill.classList.add("weak");
          strengthText.classList.add("weak");
          strengthText.textContent = "Weak — Needs letters, numbers & symbols";
        } else if (!hasLong && !hasUpper) {
          strengthFill.style.width = "66%";
          strengthFill.classList.add("fair");
          strengthText.classList.add("fair");
          strengthText.textContent = "Good password";
        } else {
          strengthFill.style.width = "100%";
          strengthFill.classList.add("strong");
          strengthText.classList.add("strong");
          strengthText.textContent = "Strong password";
        }
      }
    });
  }

  if (registerForm) {
    registerForm.addEventListener("submit", function (e) {
      const nameOk = validateNameField();
      const emailOk = validateEmailField();
      const passOk = validatePasswordField();

      const nameVal = registerName ? registerName.value.trim() : "";
      const emailVal = registerEmail ? registerEmail.value.trim() : "";
      const passVal = registerPassword ? registerPassword.value : "";

      if (!nameVal || !nameOk) {
        e.preventDefault();
        if (nameHint) {
          nameHint.style.display = "block";
          nameHint.textContent = currentRole === "student"
            ? "Please enter a valid candidate full name."
            : "Please enter a valid corporate entity name.";
        }
        if (registerName) registerName.focus();
        return;
      }

      if (!emailVal || !emailOk) {
        e.preventDefault();
        if (emailHint) {
          emailHint.style.display = "block";
          emailHint.textContent = emailValidationMessage();
        }
        if (registerEmail) registerEmail.focus();
        return;
      }

      if (!passVal || !passOk) {
        e.preventDefault();
        if (passwordHint) {
          passwordHint.style.display = "block";
          if (!passVal || passVal.length < 6) {
            passwordHint.textContent = "Password must be at least 6 characters long.";
          } else if (!/[A-Za-z]/.test(passVal)) {
            passwordHint.textContent = "Password must contain at least one letter.";
          } else if (!/[0-9]/.test(passVal)) {
            passwordHint.textContent = "Password must contain at least one number.";
          } else if (!/[^A-Za-z0-9]/.test(passVal)) {
            passwordHint.textContent = "Password must contain at least one special character (e.g. @, #, $, %, !).";
          }
        }
        if (registerPassword) registerPassword.focus();
        return;
      }
    });
  }

  // -------------------------------------------------------------
  // Date Restrictions on Opportunity Postings (No Old / Past Dates)
  // -------------------------------------------------------------
  const closingDateInput = document.getElementById("postClosingDate") || document.querySelector('input[name="closing_date"]');
  const closingDateHint = document.getElementById("closingDateHint");
  const postForm = document.getElementById("postOpportunityForm") || (closingDateInput ? closingDateInput.closest("form") : null);

  // Helper to format local date as YYYY-MM-DD
  function getLocalDateString() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  const todayStr = getLocalDateString();

  if (closingDateInput) {
    closingDateInput.setAttribute("min", todayStr);

    function validateClosingDate() {
      const val = closingDateInput.value;
      if (!val) {
        if (closingDateHint) closingDateHint.style.display = "none";
        closingDateInput.style.borderColor = "";
        return false;
      }

      if (val < todayStr) {
        if (closingDateHint) {
          closingDateHint.style.display = "block";
          closingDateHint.textContent = "Closing date cannot be in the past (" + val + "). Please select today or a future date.";
        }
        closingDateInput.style.borderColor = "var(--danger, #dc2626)";
        return false;
      }

      if (closingDateHint) closingDateHint.style.display = "none";
      closingDateInput.style.borderColor = "";
      return true;
    }

    closingDateInput.addEventListener("input", validateClosingDate);
    closingDateInput.addEventListener("change", validateClosingDate);

    if (postForm) {
      postForm.addEventListener("submit", function (e) {
        if (!validateClosingDate()) {
          e.preventDefault();
          if (closingDateHint) {
            closingDateHint.style.display = "block";
            if (!closingDateInput.value) {
              closingDateHint.textContent = "Please specify a valid closing date.";
            } else {
              closingDateHint.textContent = "Closing date cannot be in the past (" + closingDateInput.value + "). Please select today or a future date.";
            }
          }
          closingDateInput.focus();
        }
      });
    }
  }

  // -------------------------------------------------------------
  // Student profile help: show ABOVE the tapped icon, not at page bottom.
  // A single body-level popover avoids clipping from overflow:hidden cards.
  // -------------------------------------------------------------
  const profileHelpButtons = document.querySelectorAll('#profileForm .tooltip[data-help]');
  if (profileHelpButtons.length) {
    const popover = document.createElement('div');
    popover.id = 'profileHelpPopover';
    popover.className = 'profile-help-popover';
    popover.setAttribute('role', 'tooltip');
    popover.hidden = true;
    document.body.appendChild(popover);
    let activeHelpButton = null;

    function closeProfileHelp() {
      if (activeHelpButton) {
        activeHelpButton.setAttribute('aria-expanded', 'false');
        activeHelpButton.removeAttribute('aria-describedby');
        activeHelpButton = null;
      }
      popover.hidden = true;
    }

    function positionProfileHelp(button) {
      const rect = button.getBoundingClientRect();
      const width = popover.offsetWidth;
      const height = popover.offsetHeight;
      const gutter = 12;
      const gap = 11;
      const center = rect.left + rect.width / 2;
      const left = Math.max(gutter, Math.min(center - width / 2, window.innerWidth - gutter - width));
      // Above is the default. Only use below when the top of the screen
      // leaves insufficient room to display the full explanation.
      const fitsAbove = rect.top - gap - height >= gutter;
      const top = fitsAbove
        ? rect.top - gap - height
        : Math.min(rect.bottom + gap, window.innerHeight - gutter - height);
      popover.dataset.placement = fitsAbove ? 'above' : 'below';
      popover.style.left = `${left}px`;
      popover.style.top = `${Math.max(gutter, top)}px`;
      popover.style.setProperty('--popover-arrow-x', `${Math.max(12, Math.min(width - 12, center - left))}px`);
    }

    function toggleProfileHelp(button) {
      if (activeHelpButton === button) {
        closeProfileHelp();
        return;
      }
      closeProfileHelp();
      popover.textContent = button.dataset.help || '';
      if (!popover.textContent) return;
      activeHelpButton = button;
      button.setAttribute('aria-expanded', 'true');
      button.setAttribute('aria-describedby', popover.id);
      popover.hidden = false;
      positionProfileHelp(button);
    }

    profileHelpButtons.forEach(function (button) {
      button.setAttribute('aria-expanded', 'false');
      button.setAttribute('aria-controls', popover.id);
      button.addEventListener('click', function (event) {
        event.preventDefault(); // icon sits inside a form label
        event.stopPropagation();
        toggleProfileHelp(button);
      });
      button.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          toggleProfileHelp(button);
        }
      });
    });

    document.addEventListener('pointerdown', function (event) {
      if (activeHelpButton && !event.target.closest('#profileForm .tooltip[data-help]')) {
        closeProfileHelp();
      }
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') closeProfileHelp();
    });
    window.addEventListener('scroll', closeProfileHelp, true);
    window.addEventListener('resize', closeProfileHelp);
  }

  // -------------------------------------------------------------
  // Student Profile Experience Years bounds
  // -------------------------------------------------------------
  const expInput = document.getElementById("field_experience_years");
  if (expInput) {
    expInput.setAttribute("min", "0");
    expInput.setAttribute("max", "50");
    expInput.setAttribute("step", "0.5");
  }

  // -------------------------------------------------------------
  // Company Profile Years in Operation bounds
  // -------------------------------------------------------------
  const compAgeInput = document.querySelector('input[name="company_age_years"]');
  if (compAgeInput) {
    compAgeInput.setAttribute("min", "0");
    compAgeInput.setAttribute("max", "200");
    compAgeInput.setAttribute("step", "0.5");
  }

  // -------------------------------------------------------------
  // Number inputs protection against negative values
  // -------------------------------------------------------------
  document.querySelectorAll('input[type="number"][min="0"]').forEach(function (input) {
    input.addEventListener("input", function () {
      if (parseFloat(this.value) < 0) {
        this.value = "0";
      }
    });
  });
});

InternUp MOBILE FOOTER - LINK ORDER FIX
======================================
This update changes only: static/css/style.css

On mobile (width 768px and below), the footer navigation now displays
one link per row in the original order. In particular:
  Salaries & Stipends
  Universities

  DropGuard Intelligence
  Admin Portal

  About InternUp
  Help & Support

Desktop navigation remains unchanged.

INSTALL PATCH (recommended for an already-running InternUp project):
1. Close the running InternUp terminal, then extract this patch.
2. Copy the static folder from this patch into your current InternUp
   project folder (where app.py is), replacing the ONE matching CSS file.
3. Restart InternUp and refresh the page on your phone. If needed,
   clear cached data for your trycloudflare.com site or use an incognito tab.

IMPORTANT: The patch does not replace the database, users, admin accounts,
login information, or quarantine/dark-mode updates. Keep your current
instance/app.db file.

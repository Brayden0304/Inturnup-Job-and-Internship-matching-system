INTERNUP - QUARANTINE ACCESS & DARK MODE FIXES
=============================================
This build is based on the corrected original InternUp project.
Only these five application files were changed:
  app.py, models.py, routes/auth.py, routes/admin.py, templates/base.html

WHAT WAS FIXED
1. Quarantined users cannot sign in, even with a correct password.
2. Existing sessions for quarantined users are invalidated on their next request.
3. Restored users must sign in again after a revoked session.
4. Private pages are marked no-store to discourage browser-back display of old dashboards.
5. Dark mode works while signed in and resets to light after logging out,
   and it no longer carries over between different users on one browser.

PRESERVED
- Original instance/app.db, seed.py, demo users and credentials.
- All other project functionality, including the Cloudflare launcher.
- All original project backups and ML model files.

RUN ON WINDOWS (Python 3.12)
1. Extract ZIP, open the folder containing app.py, then type cmd in
   the File Explorer address bar and press Enter.
2. py -3.12 -m venv venv
3. venv\Scripts\python.exe -m pip install -r requirements.txt
4. venv\Scripts\python.exe run_cloudflare.py
   Or use: venv\Scripts\python.exe app.py

NOTE: The full ZIP omits the old Windows venv directory, since a copied
virtual environment can point at the wrong Python installation. Recreate it
using steps 2-3 above. This keeps the download around 21 MB rather than 193 MB.

IF USING THE SMALL PATCH
Extract its five files into the ROOT of your existing InternUp project,
merging the routes and templates folders and replacing only matching files.
DO NOT overwrite or delete instance/app.db and DO NOT run reseed_database.bat.
Restart Flask/Cloudflare after applying the patch.

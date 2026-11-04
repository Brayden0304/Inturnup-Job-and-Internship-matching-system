# How to Run InternUp (Student Job & Internship Matching Architecture)

This platform can be run **Offline** (100% locally with zero internet) or **Online** (via Cloudflare encrypted tunnel for testing on mobile phones, tablets, and remote presentations).

---

## ⚡ 1-Click Launchers (No Typing Required)

### 1. New Device Setup
- **Windows**: Double-click `SETUP_NEW_DEVICE.bat`
- **Linux / macOS**: Run `./setup_new_device.sh`
*Automatically configures the Python virtual environment, installs dependencies, verifies the database, and creates desktop links.*

### 2. Offline / Local Development
- **Windows**: Double-click `run_local.bat`
- **Linux / macOS**: Run `./run_local.sh`
*Access in your browser at: `http://localhost:5000`*

### 3. Online Public Hosting (Cloudflare Tunnel)
- **Windows**: Double-click `RUN_ONLINE_CLOUDFLARE.bat`
- **Linux / macOS**: Run `./run_online_cloudflare.sh`
*Generates an encrypted public HTTPS link (`https://....trycloudflare.com`) accessible on any smartphone, tablet, or external PC.*

---

## 🛡️ Automated & Periodic Database Backups

The system includes multiple levels of periodic database protection:

### Option A: Built-in Automatic Background Backups
Whenever the web application is running (offline or online), InternUp automatically takes periodic snapshots in the background every **30 minutes** without any manual action.
- Saved into: `backups/internup_auto_YYYYMMDD_HHMMSS.db`
- Retention policy: Keeps the latest 20 snapshots automatically and prunes older ones to save disk space.

### Option B: Dedicated Periodic Auto-Backup Service
- **Windows**: Double-click `START_PERIODIC_BACKUPS.bat`
- **Linux / macOS**: Run `./start_periodic_backups.sh`
*Lets you choose your preferred interval: every 15 minutes, 30 minutes, 1 hour, or 6 hours.*

### Option C: 1-Click Instant Snapshot
- Double-click `backup_database.bat` to create an immediate timestamped snapshot and view record health statistics.

### Option D: Windows Task Scheduler Automation
- Double-click `SCHEDULE_WINDOWS_BACKUP.bat` to register an automated background backup in Windows Task Scheduler (e.g., Daily at 12:00 PM or Hourly) that runs even when no terminal window is open.

### Option E: Interactive Backup, Restore & Sync Manager
- Double-click `manage_database.bat` to view, restore previous backups, export for USB transfer, or import from another computer.

---

## 🔑 Demo Login Credentials

- **Admin Portal**: `admin@internup.ac.za` or `admin@launchpad.local` (Password: `Admin@123`)
- **Student Profile**: `thabo@student.com` (Password: `Student@123`)
- **Company Profile**: `standardbank@company.com` (Password: `Company@123`)

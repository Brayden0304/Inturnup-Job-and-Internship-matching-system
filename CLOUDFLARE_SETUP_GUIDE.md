# LaunchPad — Cloudflare Laptop Hosting Guide

This guide explains how to host the **LaunchPad** platform on an old laptop and expose it securely to the internet using **Cloudflare Tunnel**.

With Cloudflare Tunnel, you **do not need**:
- A public static IP address
- Port forwarding on your Wi-Fi router
- Complex SSL certificates (Cloudflare provides automatic HTTPS)

---

## 🚀 1-Click Quick Setup (Windows)

1. Copy or extract the `student-job-matching` folder onto your old laptop.
2. Ensure **Python 3.10 or newer** is installed from [python.org](https://www.python.org/downloads/).
   *(Be sure to check the box **"Add Python to PATH"** during installation!)*
3. Double-click **`RUN_ONLINE_CLOUDFLARE.bat`**.

### What the script automatically does:
1. Detects Python and creates a clean virtual environment (`venv`).
2. Installs required Python dependencies (`requirements.txt`).
3. Seeds the demo database (`instance/app.db`) with test accounts (students, corporate partners, admin).
4. Automatically checks for or downloads the official Cloudflare tunnel binary (`cloudflared.exe`).
5. Starts the Flask web server on `http://127.0.0.1:5000`.
6. Launches Cloudflare Tunnel to generate a free, encrypted public web link (e.g., `https://xxxx.trycloudflare.com`).
7. **Generates the `LaunchPad.url` desktop web link shortcut** and copies the public URL directly to your clipboard.

---

## 🌐 How to Access LaunchPad

- **Public Internet Link**: Check the terminal output or open `CLOUDFLARE_URL.txt` for your live `https://...trycloudflare.com` link.
- **Desktop Web Link Shortcut**: Double-click `LaunchPad.url` on your desktop.
- **Local Access (on the laptop itself)**: Open `http://127.0.0.1:5000`.

---

## 🔑 Demo Accounts for Testing

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@launchpad.local`<br>*(also aliases: `admin@internup.local`, `admin@internup.ac.za`)* | `Admin@123` | Institutional Dean console & DropGuard™ Fraud Detection |
| **Student** | `thabo@student.com` | `Student@123` | Thabo Nkosi — Wits CS Honors (Cloud, Go, AWS) |
| **Student** | `ayanda@student.com` | `Student@123` | Ayanda Mthembu — UCT Accounting (SAICA Stream) |
| **Company** | `standardbank@company.com` | `Company@123` | Standard Bank Corporate & Investment Banking |
| **Company** | `deloitte@company.com` | `Company@123` | Deloitte & Touche South Africa |
| **Scam Demo** | `quickcash@company.com` | `Company@123` | QuickCash Capital (quarantined by ML Fraud Detection) |

---

## ⚙️ Advanced: Using a Custom Domain (Optional)

If you own a domain registered on Cloudflare (e.g., `internup.yourdomain.com`):

1. Go to the [Cloudflare Zero Trust Dashboard](https://one.dash.cloudflare.com/).
2. Navigate to **Networks** → **Tunnels** → **Create a Tunnel**.
3. Choose **Cloudflared**, name it (e.g. `internup`), and copy the tunnel token.
4. Under Public Hostname, route your subdomain to `http://localhost:5000`.
5. Run `RUN_ONLINE_CLOUDFLARE.bat`, select option `[2]`, and paste your token.

---

## 💡 Tips for Laptop Hosting

- **Prevent Laptop from Sleeping**: On Windows, go to **Settings → System → Power & battery** (or Control Panel → Power Options) and set **"When plugged in, turn off after: Never"** and **"When plugged in, put my device to sleep: Never"**.
- **Close the Lid without Sleeping**: In Control Panel → Power Options → **"Choose what closing the lid does"**, set **"When plugged in"** to **"Do nothing"**. This lets you close the laptop and keep it tucked away while it serves the website!

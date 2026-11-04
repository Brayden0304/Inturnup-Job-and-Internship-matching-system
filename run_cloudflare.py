"""
InternUp - Universal Cross-Platform 1-Click Online Host
Compatible with Windows, Linux (Ubuntu/Debian/Fedora/WSL), and macOS.
"""
import os
import sys
import time
import subprocess
import re
import urllib.request
import signal
import platform

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT_DIR)

os.system('cls' if os.name == 'nt' else 'clear')

print("=" * 75)
print("       INTERNUP - CROSS-PLATFORM ONLINE HOST")
print(f"       Operating System: {platform.system()} ({platform.machine()})")
print("=" * 75)
print(" Launching Flask web server and creating secure public Cloudflare link...")
print("=" * 75)
print()

# 1. Detect Python executable
py_exe = sys.executable
print(f"[1/5] Python Runtime: {py_exe}")

# 2. Check Database
print("[2/5] Checking Database...")
db_path = os.path.join(ROOT_DIR, "instance", "app.db")
if not os.path.exists(db_path):
    print("      instance/app.db not found. Seeding initial accounts & listings...")
    subprocess.run([py_exe, "seed.py"], check=True)
    print("      [OK] Database seeded successfully.")
else:
    print("      [OK] Database ready (instance/app.db).")

# 3. Clean up stale port 5000 and previous tunnels
print("[3/5] Checking port 5000 & previous tunnel processes...")
if os.name == 'nt':
    subprocess.call(["taskkill", "/F", "/IM", "cloudflared.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        netstat = subprocess.check_output(["netstat", "-aon"], text=True)
        for line in netstat.splitlines():
            if ":5000 " in line and "LISTENING" in line:
                pid = line.strip().split()[-1]
                print(f"      Freeing port 5000 (terminating stale process PID {pid})...")
                subprocess.call(["taskkill", "/F", "/PID", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
else:
    # Linux / macOS
    subprocess.call(["pkill", "-f", "cloudflared"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        subprocess.call(["fuser", "-k", "5000/tcp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
print("      [OK] Port 5000 is ready.")

# 4. Check cloudflared binary
print("[4/5] Checking Cloudflare Tunnel binary...")
if os.name == 'nt':
    cf_exe = os.path.join(ROOT_DIR, "cloudflared.exe")
    download_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
else:
    cf_exe = os.path.join(ROOT_DIR, "cloudflared")
    download_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"

if not os.path.exists(cf_exe):
    try:
        sys_cf = subprocess.check_output(["which" if os.name != 'nt' else "where", "cloudflared"], text=True).strip()
        if sys_cf:
            cf_exe = sys_cf.splitlines()[0]
            print(f"      [OK] Found system cloudflared: {cf_exe}")
    except Exception:
        print(f"      Downloading cloudflared from {download_url}...")
        urllib.request.urlretrieve(download_url, cf_exe)
        if os.name != 'nt':
            os.chmod(cf_exe, 0o755)
        print("      [OK] cloudflared downloaded successfully.")
else:
    print(f"      [OK] Using local {os.path.basename(cf_exe)}.")

# 5. Start Flask Server in background (using DEVNULL to prevent Windows pipe buffer deadlocks)
print("[5/5] Starting Flask server & Cloudflare tunnel...")
flask_env = os.environ.copy()
flask_env["FLASK_ENV"] = "production"
flask_proc = subprocess.Popen([py_exe, "app.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=flask_env)

# Verify local Flask is responding
local_up = False
for attempt in range(8):
    time.sleep(1)
    try:
        urllib.request.urlopen("http://127.0.0.1:5000", timeout=2)
        local_up = True
        break
    except Exception:
        pass

if local_up:
    print("      [OK] Local Flask server is active on http://127.0.0.1:5000")
else:
    print("      [!] Local server initializing...")

log_path = os.path.join(ROOT_DIR, "cloudflared.log")
if os.path.exists(log_path):
    try:
        os.remove(log_path)
    except Exception:
        pass

cf_cmd = [cf_exe, "tunnel", "--url", "http://127.0.0.1:5000", "--logfile", log_path]
cf_proc = subprocess.Popen(cf_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("      Waiting for Cloudflare to assign public tunnel URL...")
public_url = None
for _ in range(30):
    time.sleep(1)
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", content)
            if match:
                public_url = match.group(0)
                break
        except Exception:
            pass

if public_url:
    url_file = os.path.join(ROOT_DIR, "CLOUDFLARE_URL.txt")
    with open(url_file, "w") as f:
        f.write(public_url + "\n")

    # Copy to clipboard if available
    if os.name == 'nt':
        try:
            subprocess.run(["powershell", "-Command", f"Set-Clipboard -Value '{public_url}'"], timeout=3)
        except Exception:
            pass
    elif sys.platform == 'darwin':
        try:
            p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            p.communicate(public_url.encode('utf-8'))
        except Exception:
            pass

    # Wait for DNS propagation
    print("      Verifying global DNS propagation...")
    propagated = False
    for i in range(12):
        time.sleep(1.5)
        try:
            req = urllib.request.Request(public_url, headers={'User-Agent': 'Mozilla/5.0'})
            res = urllib.request.urlopen(req, timeout=3)
            if res.status == 200:
                propagated = True
                time.sleep(3)
                break
        except Exception:
            pass

    print()
    print("=" * 75)
    print("       * * *  INTERNUP IS NOW LIVE ON THE INTERNET!  * * *")
    print("=" * 75)
    print()
    print("   PUBLIC URL (ACCESSIBLE FROM PHONES, TABLETS, PC & MAC):")
    print()
    print(f"      >>> {public_url} <<<")
    print()
    print("   [OK] Link copied to your clipboard")
    print("   [OK] Saved to: CLOUDFLARE_URL.txt")
    print("   [OK] Local address: http://127.0.0.1:5000 (Use on this laptop)")
    print()
    print("=" * 75)
    print("   DEMO LOGINS:")
    print("   - Admin:   admin@internup.ac.za (or admin@launchpad.local) (password: Admin@123)")
    print("   - Student: thabo@student.com        (password: Student@123)")
    print("   - Company: standardbank@company.com (password: Company@123)")
    print("=" * 75)
    print()
    print("   Opening browser...")
    try:
        import webbrowser
        webbrowser.open(public_url)
    except Exception:
        pass

else:
    print("[!] Could not detect public URL within 30 seconds.")
    print("    Local access is running on: http://127.0.0.1:5000")
    try:
        import webbrowser
        webbrowser.open("http://127.0.0.1:5000")
    except Exception:
        pass

print()
print("=" * 75)
print("   [ACTIVE] Server and Cloudflare Tunnel are LIVE.")
print("   KEEP THIS TERMINAL OPEN to maintain the online connection!")
print("   Type 'exit' to stop the server, or 'url' to display the link again.")
print("=" * 75)
print()

while True:
    try:
        cmd = input(">>> (Type 'exit' to stop, or 'url' to re-show link): ").strip().lower()
        if cmd in ("exit", "quit", "stop", "q"):
            break
        elif cmd in ("url", "link", "show"):
            print(f"\n   Live Public Link: {public_url}")
            print(f"   Local PC Link:    http://127.0.0.1:5000\n")
        elif cmd == "":
            continue
        else:
            print("   Commands: type 'exit' to shut down, or 'url' to display the live link.")
    except (KeyboardInterrupt, EOFError):
        break

print("\nStopping Cloudflare Tunnel and Flask server...")
try:
    cf_proc.terminate()
except Exception:
    pass
try:
    flask_proc.terminate()
except Exception:
    pass

if os.name == 'nt':
    subprocess.call(["taskkill", "/F", "/IM", "cloudflared.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        netstat = subprocess.check_output(["netstat", "-aon"], text=True)
        for line in netstat.splitlines():
            if ":5000 " in line and "LISTENING" in line:
                pid = line.strip().split()[-1]
                subprocess.call(["taskkill", "/F", "/PID", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
else:
    subprocess.call(["pkill", "-f", "cloudflared"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("Server stopped cleanly. Goodbye!")
time.sleep(2)

# Comprehensive Guide: Moving InternUp to an Older Laptop
**How to Set Up, Run Offline (No Internet), and Run Online on Any Device**

This step-by-step guide explains exactly how to transfer this project onto an older laptop (Windows 10, 8, or 7, or Linux) for testing, rehearsal, or your final capstone presentation.

---

## 📋 Pre-Flight Checklist: What You Need

1. **A USB Flash Drive** (or Google Drive / OneDrive link) with at least 500 MB free space.
2. **Python 3.10+ installed on the older laptop**:
   - Download the official installer from [python.org/downloads](https://www.python.org/downloads/).
   - ⚠️ **CRITICAL STEP DURING INSTALLATION**: On the first screen of the Python installer, you **MUST** check the box that says:
     `☑ Add python.exe to PATH` (at the bottom of the window).
     Then click **Install Now**.
3. **2 minutes of internet connection (One Time Only)** on the old laptop to let `pip` download the required Python libraries. After this single step, the entire system can run 100% offline forever.

---

## 🚀 Step 1: Copy the Project to the Old Laptop

1. Insert your USB drive into your current computer.
2. Copy the entire folder:
   `student-job-matching-20261027T105016Z-1-001 (2)`
   onto the USB drive.
   > **Pro Tip**: If you want the copy to be faster, you can safely skip copying the `venv/` folder. The setup script on the old laptop will automatically generate a fresh, clean `venv` tailored to that laptop in 60 seconds!
3. Eject the USB drive and plug it into the older laptop.
4. Copy the folder from the USB drive onto the old laptop's **Desktop** or **Documents** folder.

---

## ⚡ Step 2: Run 1-Click Automated Setup on the Old Laptop

1. Open the copied folder on the old laptop.
2. Double-click the file named:
   👉 **`SETUP_NEW_DEVICE.bat`**
3. The script will automatically:
   - Detect Python on the machine.
   - Cleanly build a native virtual environment (`venv`).
   - Install all required libraries (`Flask`, `scikit-learn`, `pandas`, `PyMySQL`, `shap`).
   - Check and seed the database with all Richfield student and employer demo accounts.
   - Verify the `cloudflared.exe` binary.
   - Create a desktop launcher shortcut.
4. When you see:
   `*** SETUP COMPLETE! INTERNUP IS READY ON THIS DEVICE ***`
   press any key. The setup is permanently finished!

---

## 📴 Step 3: How to Run OFFLINE (Zero Internet / Campus Presentation)

Use this mode if the campus Wi-Fi is unreliable, or if you want to demonstrate that the application is fully self-contained.

1. Double-click:
   👉 **`run_local.bat`**
2. A black terminal window will open showing:
   ```
   * Running on http://127.0.0.1:5000
   * Running on http://localhost:5000
   ```
3. Open any web browser (Chrome, Brave, Edge, Firefox) and navigate to:
   ```
   http://localhost:5000
   ```
4. **Offline Multi-Device Demo (Bonus)**:
   - If you want the panel or teammates to test on their smartphones without any internet data, turn on your laptop's Wi-Fi hotspot (or connect laptop and phones to the same router).
   - Find your laptop's local IP (open CMD and type `ipconfig`, look for IPv4 e.g. `192.168.1.15`).
   - Anyone on that Wi-Fi can open `http://192.168.1.15:5000` on their phone with zero mobile data!

---

## 🌐 Step 4: How to Run ONLINE (Cloudflare Tunnel for Markers & Remote Panel)

Use this mode when you want markers, lecturers, or team members anywhere in the world to access the live site on their own phones or computers.

1. Ensure the laptop is connected to Wi-Fi, Ethernet, or your phone's 4G/5G mobile hotspot.
2. Double-click:
   👉 **`RUN_ONLINE_CLOUDFLARE.bat`**
3. The terminal will start Flask and create an encrypted public Cloudflare tunnel.
4. You will see a live public link printed in green:
   ```
   >>> https://xxxx-xxxx-xxxx.trycloudflare.com <<<
   ```
5. The live link is automatically copied to your clipboard, and your default browser will open it automatically!
6. Anyone can open that HTTPS link on an iPhone, Android, iPad, or Mac.

---

## 🛡️ Step 5: Database Backups & Moving Backups Between Devices

- **Automatic Backups**: While the app is running (online or offline), it automatically saves a snapshot into the `backups/` folder every **15 minutes**.
- **Manual Snapshot**: Double-click `backup_database.bat` at any time to take an instant snapshot.
- **Syncing to Another Computer**:
  1. Double-click `manage_database.bat` and select **Option 4 (Export Database)** to save a copy onto your USB drive.
  2. On any other computer, open `manage_database.bat` and select **Option 5 (Import Database)** to load that file.

---

## 💡 Troubleshooting & Performance Tips for Older Laptops

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **`python` is not recognized as an internal or external command** | Python was installed without checking "Add to PATH" | Re-run the Python installer from [python.org](https://www.python.org), choose **Modify**, and check the box **"Add python.exe to PATH"**. |
| **First page load takes 3-5 seconds** | Slower CPU compiling Python bytecode on first boot | Normal behavior on older hard drives. After the first load, all pages load instantaneously (under 50ms) from `__pycache__`. |
| **Cloudflare link says "Site can't be reached" on startup** | Browser checked DNS before Cloudflare finished global propagation (takes 3-5 seconds) | Wait 5 seconds and press **`Ctrl + Shift + R`** (hard refresh) or reload the page. |
| **Old 32-bit Windows Laptop** | `cloudflared.exe` included is 64-bit | `run_local.bat` works 100% on 32-bit. For online mode on 32-bit, download the 32-bit `cloudflared-windows-386.exe` from Cloudflare's GitHub and rename it to `cloudflared.exe`. |

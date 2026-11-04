"""
InternUp Database Backup, Restore, and Multi-Device Sync Manager
Supports automated snapshots, multi-device database transfers, and statistics.
"""
import os
import sys
import shutil
import sqlite3
import argparse
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(ROOT_DIR, "instance")
DB_PATH = os.path.join(INSTANCE_DIR, "app.db")
BACKUP_DIR = os.path.join(ROOT_DIR, "backups")

os.makedirs(INSTANCE_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)


def backup_database():
    """Create a timestamped backup of the current database."""
    if not os.path.exists(DB_PATH):
        print(f"[!] Primary database not found at: {DB_PATH}")
        print("    Run seed.py or start the application first.")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"internup_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    # Use SQLite backup API for transactional integrity
    try:
        src = sqlite3.connect(DB_PATH)
        dst = sqlite3.connect(backup_path)
        with dst:
            src.backup(dst)
        dst.close()
        src.close()
        size_kb = os.path.getsize(backup_path) / 1024
        print(f"[SUCCESS] Database snapshot created: {backup_filename} ({size_kb:.1f} KB)")
        print(f"          Saved in: {BACKUP_DIR}")
        return backup_path
    except Exception as e:
        # Fallback to copy
        shutil.copy2(DB_PATH, backup_path)
        print(f"[SUCCESS] File copied to backup: {backup_filename}")
        return backup_path


def list_backups():
    """List all available backup snapshots."""
    files = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".db")]
    files.sort(reverse=True)
    return files


def restore_backup(backup_name=None):
    """Restore database from a chosen backup snapshot."""
    backups = list_backups()
    if not backups:
        print("[!] No backups found in backups/ directory.")
        return False

    if not backup_name:
        print("\nAvailable Backups:")
        print("-" * 60)
        for i, b in enumerate(backups, start=1):
            b_path = os.path.join(BACKUP_DIR, b)
            mtime = datetime.fromtimestamp(os.path.getmtime(b_path)).strftime("%Y-%m-%d %H:%M:%S")
            size_kb = os.path.getsize(b_path) / 1024
            print(f"  [{i}] {b}  ({size_kb:.1f} KB) - {mtime}")
        print("-" * 60)
        choice = input("Enter backup number to restore (or Enter to cancel): ").strip()
        if not choice or not choice.isdigit():
            print("Restore cancelled.")
            return False
        idx = int(choice) - 1
        if idx < 0 or idx >= len(backups):
            print("[!] Invalid selection.")
            return False
        selected_file = backups[idx]
    else:
        selected_file = backup_name

    selected_path = os.path.join(BACKUP_DIR, selected_file)
    if not os.path.exists(selected_path):
        print(f"[!] Backup file not found: {selected_path}")
        return False

    # Safety auto-backup of current before overwriting
    if os.path.exists(DB_PATH):
        safety_path = os.path.join(BACKUP_DIR, "pre_restore_safety_backup.db")
        shutil.copy2(DB_PATH, safety_path)
        print("  [i] Current database backed up to pre_restore_safety_backup.db before replacing.")

    shutil.copy2(selected_path, DB_PATH)
    print(f"[SUCCESS] Database successfully restored from: {selected_file}")
    return True


def export_sync(destination_path=None):
    """Export the database to a sync folder or USB drive."""
    if not os.path.exists(DB_PATH):
        print("[!] No database found to export.")
        return

    if not destination_path:
        destination_path = input("Enter destination directory or file path for sync export: ").strip()

    if not destination_path:
        print("Export cancelled.")
        return

    destination_path = os.path.expanduser(os.path.expandvars(destination_path))
    if os.path.isdir(destination_path):
        target_file = os.path.join(destination_path, "internup_sync_data.db")
    else:
        target_file = destination_path

    try:
        shutil.copy2(DB_PATH, target_file)
        print(f"[SUCCESS] Database exported for device sync: {target_file}")
    except Exception as e:
        print(f"[ERROR] Export failed: {e}")


def import_sync(source_path=None):
    """Import a database sync file from another computer or USB."""
    if not source_path:
        source_path = input("Enter path to external internup database (.db) to import: ").strip()

    if not source_path:
        print("Import cancelled.")
        return

    source_path = os.path.expanduser(os.path.expandvars(source_path))
    if not os.path.exists(source_path):
        print(f"[!] Source file not found: {source_path}")
        return

    # Create safety backup of current
    if os.path.exists(DB_PATH):
        backup_database()

    try:
        shutil.copy2(source_path, DB_PATH)
        print(f"[SUCCESS] Successfully synced and replaced database from: {source_path}")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")


def show_database_stats():
    """Show live summary stats of data stored in database."""
    if not os.path.exists(DB_PATH):
        print(f"[!] Database not found at: {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        print("\n" + "=" * 60)
        print("           INTERNUP DATABASE HEALTH & RECORD STATS")
        print("=" * 60)
        tables = [
            ("Users", "users"),
            ("Students", "student_profiles"),
            ("Companies", "company_profiles"),
            ("Opportunities / Jobs", "opportunities"),
            ("Applications", "applications"),
            ("DropGuard Risk Audits", "risk_assessments"),
            ("Live Notifications", "notifications"),
        ]
        for label, table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"  - {label:<22}: {count:>5} records")
            except Exception:
                print(f"  - {label:<22}: (not created)")
        size_kb = os.path.getsize(DB_PATH) / 1024
        print(f"  - Total Database Size   : {size_kb:.1f} KB")
        print("=" * 60)
        conn.close()
    except Exception as e:
        print(f"[ERROR] Could not read database stats: {e}")


def interactive_menu():
    while True:
        print("\n" + "=" * 65)
        print("       INTERNUP - DATABASE BACKUP, RESTORE & SYNC MANAGER")
        print("=" * 65)
        print("  1. Create Instant Database Backup (Snapshot)")
        print("  2. View Backups & Restore a Snapshot")
        print("  3. View Database Record Counts & Health")
        print("  4. Export Database for Transfer to Another Device (USB/Cloud)")
        print("  5. Import Database from Another Device")
        print("  6. Reseed Database to Factory Demo Data (seed.py)")
        print("  0. Exit")
        print("=" * 65)
        choice = input("Select an option [0-6]: ").strip()

        if choice == "1":
            backup_database()
        elif choice == "2":
            restore_backup()
        elif choice == "3":
            show_database_stats()
        elif choice == "4":
            export_sync()
        elif choice == "5":
            import_sync()
        elif choice == "6":
            confirm = input("Are you sure you want to reset & reseed the database? (y/N): ").strip().lower()
            if confirm == "y":
                os.system(f'"{sys.executable}" "{os.path.join(ROOT_DIR, "seed.py")}"')
        elif choice == "0":
            print("Exiting Database Manager.")
            break
        else:
            print("[!] Invalid option. Please choose between 0 and 6.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="InternUp Database Manager")
    parser.add_argument("--backup", action="store_true", help="Run automated backup")
    parser.add_argument("--stats", action="store_true", help="Print database stats")
    parser.add_argument("--restore", type=str, help="Restore from specific backup filename")
    parser.add_argument("--export", type=str, help="Export db to destination path")
    parser.add_argument("--import-file", type=str, help="Import db from source path")

    args = parser.parse_args()

    if args.backup:
        backup_database()
    elif args.stats:
        show_database_stats()
    elif args.restore:
        restore_backup(args.restore)
    elif args.export:
        export_sync(args.export)
    elif args.import_file:
        import_sync(args.import_file)
    else:
        interactive_menu()

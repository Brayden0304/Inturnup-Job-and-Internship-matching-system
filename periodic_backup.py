"""
InternUp Periodic Database Auto-Backup Service
Provides automated background snapshots at regular intervals with retention pruning.
Can run as a background thread inside Flask or as a standalone service.
"""
import os
import sys
import time
import shutil
import sqlite3
import threading
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(ROOT_DIR, "instance")
DB_PATH = os.path.join(INSTANCE_DIR, "app.db")
BACKUP_DIR = os.path.join(ROOT_DIR, "backups")

os.makedirs(INSTANCE_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)


class PeriodicBackupManager:
    def __init__(self, interval_minutes=15, retention_count=20):
        self.interval_seconds = int(interval_minutes * 60)
        self.retention_count = int(retention_count)
        self._running = False
        self._thread = None
        self._stop_event = threading.Event()

    def create_snapshot(self, tag="auto"):
        """Create a consistent SQLite snapshot using transactional backup API."""
        if not os.path.exists(DB_PATH):
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"internup_{tag}_{timestamp}.db"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)

        try:
            src = sqlite3.connect(DB_PATH)
            dst = sqlite3.connect(backup_path)
            with dst:
                src.backup(dst)
            dst.close()
            src.close()
        except Exception:
            try:
                shutil.copy2(DB_PATH, backup_path)
            except Exception as e:
                print(f"[!] [AUTO-BACKUP ERROR] Could not copy database: {e}")
                return None

        size_kb = os.path.getsize(backup_path) / 1024
        self._prune_old_backups(tag)

        now_str = datetime.now().strftime("%H:%M:%S")
        total_backups = len([f for f in os.listdir(BACKUP_DIR) if f.endswith(".db")])
        print(f"[{now_str}] [AUTO-BACKUP] Created {backup_filename} ({size_kb:.1f} KB) | Total retained: {total_backups}")
        return backup_path

    def _prune_old_backups(self, tag="auto"):
        """Retain only the latest N backups with the given tag."""
        try:
            files = [
                os.path.join(BACKUP_DIR, f)
                for f in os.listdir(BACKUP_DIR)
                if f.startswith(f"internup_{tag}_") and f.endswith(".db")
            ]
            files.sort(key=os.path.getmtime, reverse=True)

            if len(files) > self.retention_count:
                to_delete = files[self.retention_count :]
                for old_file in to_delete:
                    try:
                        os.remove(old_file)
                    except Exception:
                        pass
        except Exception as e:
            print(f"[!] [AUTO-BACKUP] Prune warning: {e}")

    def run_loop(self):
        """Continuous execution loop with clean shutdown support."""
        self._running = True
        interval_min = self.interval_seconds // 60
        print("=" * 70)
        print("       INTERNUP - PERIODIC DATABASE AUTO-BACKUP ACTIVE")
        print("=" * 70)
        print(f"  Target Database   : {DB_PATH}")
        print(f"  Backup Directory  : {BACKUP_DIR}")
        print(f"  Backup Interval   : Every {interval_min} minutes ({self.interval_seconds}s)")
        print(f"  Retention Policy  : Retaining latest {self.retention_count} snapshots")
        print("=" * 70)
        print()

        # Take initial backup on start
        self.create_snapshot(tag="auto")

        while not self._stop_event.is_set():
            # Wait for next interval in 1s increments so stop is instant
            for _ in range(self.interval_seconds):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

            if not self._stop_event.is_set():
                self.create_snapshot(tag="auto")

        print("\n[AUTO-BACKUP] Periodic backup service stopped.")

    def start_background(self):
        """Start the backup manager in a background daemon thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self.run_loop, daemon=True, name="InternUpAutoBackup")
        self._thread.start()

    def stop(self):
        """Signal the background thread to stop."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)


# Global singleton for in-app imports
_global_backup_manager = None


def start_in_app_periodic_backup(interval_minutes=15, retention_count=20):
    """Safely start periodic backups inside Flask or server runners."""
    global _global_backup_manager
    if _global_backup_manager is None:
        _global_backup_manager = PeriodicBackupManager(interval_minutes, retention_count)
        _global_backup_manager.start_background()
    return _global_backup_manager


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="InternUp Periodic Database Auto-Backup Service")
    parser.add_argument("--interval", type=int, default=15, help="Backup interval in minutes (default: 15)")
    parser.add_argument("--retention", type=int, default=20, help="Number of backups to keep (default: 20)")
    parser.add_argument("--once", action="store_true", help="Take a single snapshot and exit")

    args = parser.parse_args()

    manager = PeriodicBackupManager(interval_minutes=args.interval, retention_count=args.retention)

    if args.once:
        path = manager.create_snapshot(tag="manual")
        if path:
            print(f"Snapshot successful: {path}")
        else:
            print("Snapshot failed.")
    else:
        try:
            manager.run_loop()
        except KeyboardInterrupt:
            manager.stop()

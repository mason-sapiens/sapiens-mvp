#!/usr/bin/env python3
"""
Cleanup script to remove old conversation state files.
Run this on the server to ensure fresh room-specific conversations.
"""

import shutil
from pathlib import Path

def cleanup_state():
    """Remove all conversation state files."""

    logs_dir = Path("./data/logs")

    if not logs_dir.exists():
        print("✅ No logs directory found - nothing to clean")
        return

    print(f"🧹 Cleaning up state files in {logs_dir}")

    # Count directories
    user_dirs = list(logs_dir.iterdir())

    if not user_dirs:
        print("✅ No state files found - already clean")
        return

    print(f"Found {len(user_dirs)} state directories")

    # Ask for confirmation
    response = input("\n⚠️  This will delete all conversation state. Continue? (yes/no): ")

    if response.lower() != 'yes':
        print("❌ Cancelled")
        return

    # Remove all state directories
    for user_dir in user_dirs:
        if user_dir.is_dir():
            print(f"  Removing {user_dir.name}...")
            shutil.rmtree(user_dir)

    print(f"\n✅ Cleaned up {len(user_dirs)} state directories")
    print("All users will start fresh conversations in each room")

if __name__ == "__main__":
    cleanup_state()

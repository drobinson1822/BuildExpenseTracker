# Script to update old project status values to new enum values
# Usage: python scripts/fix_project_status_enum.py

import sqlite3
import os

def main():
    db_path = os.environ.get("DATABASE_URL", "test.db")
    if db_path.startswith("sqlite:///"):
        db_path = db_path.replace("sqlite:///", "")
    print(f"Connecting to DB at: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Update old values to new enum values
    cur.execute("UPDATE projects SET status = 'not_started' WHERE status = 'planned'")
    cur.execute("UPDATE projects SET status = 'completed' WHERE status = 'complete'")
    conn.commit()
    print("Project status values updated.")
    conn.close()

if __name__ == "__main__":
    main()

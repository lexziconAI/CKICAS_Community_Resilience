#!/usr/bin/env python3
"""
Fix database schema for triggers table
"""

import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "ckcias.db")

def check_and_fix_database():
    """Check the current schema and fix if needed"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check current schema
    print("Checking current database schema...")
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='triggers'")
    result = cursor.fetchone()

    if result:
        print(f"\nCurrent schema:\n{result[0]}\n")

        # Check if conditions column exists
        cursor.execute("PRAGMA table_info(triggers)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        print(f"Current columns: {column_names}\n")

        if 'conditions' not in column_names:
            print("✗ 'conditions' column is missing! Recreating table...\n")

            # Drop the old table
            cursor.execute("DROP TABLE IF EXISTS triggers")

            # Create the table with correct schema
            cursor.execute("""
                CREATE TABLE triggers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    region TEXT NOT NULL,
                    conditions TEXT NOT NULL,
                    combination_rule TEXT NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

            # Verify the new schema
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='triggers'")
            result = cursor.fetchone()
            print(f"New schema:\n{result[0]}\n")

            print("✓ Table recreated successfully!")
        else:
            print("✓ Database schema is correct!")
    else:
        print("✗ Table 'triggers' does not exist. Creating...\n")

        # Create the table
        cursor.execute("""
            CREATE TABLE triggers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                region TEXT NOT NULL,
                conditions TEXT NOT NULL,
                combination_rule TEXT NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✓ Table created successfully!")

    conn.close()

if __name__ == "__main__":
    check_and_fix_database()

"""
CKCIAS Drought Monitor Database Layer
SQLite database for user authentication and drought trigger alerts
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
import os


# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), "ckcias.db")


@contextmanager
def get_db_connection():
    """
    Context manager for database connections with atomic transactions.
    Ensures proper connection handling and automatic rollback on errors.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database() -> None:
    """
    Initialize SQLite database with required tables.
    Creates tables if they don't exist.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                region TEXT NOT NULL,
                organization TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Triggers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS triggers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                region TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                combination_rule TEXT NOT NULL CHECK(combination_rule IN ('any_1', 'any_2', 'any_3', 'all')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Trigger conditions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trigger_conditions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trigger_id INTEGER NOT NULL,
                indicator TEXT NOT NULL CHECK(indicator IN ('temp', 'rainfall', 'humidity', 'wind_speed')),
                operator TEXT NOT NULL CHECK(operator IN ('>', '<', '>=', '<=', '==')),
                threshold_value REAL NOT NULL,
                FOREIGN KEY (trigger_id) REFERENCES triggers(id) ON DELETE CASCADE
            )
        """)

        # Notification log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notification_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trigger_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notification_type TEXT DEFAULT 'email',
                trigger_conditions_met TEXT NOT NULL,
                FOREIGN KEY (trigger_id) REFERENCES triggers(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_triggers_user_id ON triggers(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trigger_conditions_trigger_id ON trigger_conditions(trigger_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notification_log_user_id ON notification_log(user_id)
        """)

        print("✅ Database tables created successfully")


def seed_users() -> None:
    """
    Insert hardcoded users for the MVP skateboard.
    - Regan (Auckland, Axiom Intelligence)
    - Tim House (Taranaki, Fonterra)
    """
    users = [
        {
            "email": "regan@axiomintelligence.co.nz",
            "name": "Regan",
            "region": "Auckland",
            "organization": "Axiom Intelligence"
        },
        {
            "email": "tim.house@fonterra.com",
            "name": "Tim House",
            "region": "Taranaki",
            "organization": "Fonterra"
        }
    ]

    with get_db_connection() as conn:
        cursor = conn.cursor()

        for user in users:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO users (email, name, region, organization)
                    VALUES (?, ?, ?, ?)
                """, (user["email"], user["name"], user["region"], user["organization"]))
                print(f"✅ User seeded: {user['name']} ({user['email']})")
            except Exception as e:
                print(f"❌ Error seeding user {user['name']}: {str(e)}")


def seed_default_triggers() -> None:
    """
    Create Tim House's default drought trigger for Taranaki.
    - Name: "Taranaki Drought Alert"
    - Region: Taranaki
    - Combination: any_2 (any 2 conditions must be met)
    - Conditions:
      * temp > 25
      * rainfall < 2
      * humidity < 60
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get Tim House's user ID
        cursor.execute("SELECT id FROM users WHERE email = ?", ("tim.house@fonterra.com",))
        tim_user = cursor.fetchone()

        if not tim_user:
            print("❌ Error: Tim House user not found. Run seed_users() first.")
            return

        tim_user_id = tim_user["id"]

        # Check if trigger already exists
        cursor.execute("""
            SELECT id FROM triggers
            WHERE user_id = ? AND name = ?
        """, (tim_user_id, "Taranaki Drought Alert"))

        existing_trigger = cursor.fetchone()

        if existing_trigger:
            print("⚠️  Taranaki Drought Alert trigger already exists")
            return

        # Create the trigger
        cursor.execute("""
            INSERT INTO triggers (user_id, name, region, is_active, combination_rule)
            VALUES (?, ?, ?, ?, ?)
        """, (tim_user_id, "Taranaki Drought Alert", "Taranaki", 1, "any_2"))

        trigger_id = cursor.lastrowid

        # Create the three conditions
        conditions = [
            {"indicator": "temp", "operator": ">", "threshold_value": 25.0},
            {"indicator": "rainfall", "operator": "<", "threshold_value": 2.0},
            {"indicator": "humidity", "operator": "<", "threshold_value": 60.0}
        ]

        for condition in conditions:
            cursor.execute("""
                INSERT INTO trigger_conditions (trigger_id, indicator, operator, threshold_value)
                VALUES (?, ?, ?, ?)
            """, (trigger_id, condition["indicator"], condition["operator"], condition["threshold_value"]))

        print(f"✅ Default trigger created: Taranaki Drought Alert (ID: {trigger_id})")
        print(f"   Conditions: temp>25, rainfall<2, humidity<60")
        print(f"   Combination rule: any_2")


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email address"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_users() -> List[Dict[str, Any]]:
    """Get all users"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY id")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_user_triggers(user_id: int) -> List[Dict[str, Any]]:
    """Get all triggers for a specific user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM triggers
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_trigger_conditions(trigger_id: int) -> List[Dict[str, Any]]:
    """Get all conditions for a specific trigger"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM trigger_conditions
            WHERE trigger_id = ?
        """, (trigger_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def log_notification(
    trigger_id: int,
    user_id: int,
    trigger_conditions_met: Dict[str, Any],
    notification_type: str = "email"
) -> int:
    """
    Log a notification sent to a user.

    Args:
        trigger_id: ID of the trigger that was activated
        user_id: ID of the user receiving the notification
        trigger_conditions_met: Dictionary of conditions and their values (stored as JSON)
        notification_type: Type of notification (default: 'email')

    Returns:
        ID of the created notification log entry
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Convert conditions dict to JSON string
        conditions_json = json.dumps(trigger_conditions_met)

        cursor.execute("""
            INSERT INTO notification_log
            (trigger_id, user_id, notification_type, trigger_conditions_met)
            VALUES (?, ?, ?, ?)
        """, (trigger_id, user_id, notification_type, conditions_json))

        return cursor.lastrowid


def get_notification_history(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get notification history for a user.

    Args:
        user_id: ID of the user
        limit: Maximum number of notifications to return (default: 50)

    Returns:
        List of notification log entries with parsed JSON conditions
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nl.*, t.name as trigger_name, t.region
            FROM notification_log nl
            JOIN triggers t ON nl.trigger_id = t.id
            WHERE nl.user_id = ?
            ORDER BY nl.sent_at DESC
            LIMIT ?
        """, (user_id, limit))

        rows = cursor.fetchall()

        # Parse JSON conditions for each row
        notifications = []
        for row in rows:
            notification = dict(row)
            notification["trigger_conditions_met"] = json.loads(notification["trigger_conditions_met"])
            notifications.append(notification)

        return notifications


def initialize_mvp_database() -> None:
    """
    Complete database initialization for MVP skateboard.
    Creates tables, seeds users, and creates default triggers.
    """
    print("🚀 Initializing CKCIAS Drought Monitor Database...")

    try:
        # Create tables
        init_database()

        # Seed users
        print("\n📝 Seeding users...")
        seed_users()

        # Seed default triggers
        print("\n⚡ Creating default triggers...")
        seed_default_triggers()

        print("\n✅ Database initialization complete!")
        print(f"📁 Database location: {DB_PATH}")

        # Display summary
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM users")
            user_count = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) as count FROM triggers")
            trigger_count = cursor.fetchone()["count"]

            print(f"\n📊 Summary:")
            print(f"   Users: {user_count}")
            print(f"   Triggers: {trigger_count}")

    except Exception as e:
        print(f"\n❌ Database initialization failed: {str(e)}")
        raise


if __name__ == "__main__":
    # Run initialization when script is executed directly
    initialize_mvp_database()

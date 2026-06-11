import sqlite3
from contextlib import contextmanager
import datetime

class BMIDataStore:
    """Manages persistent storage for BMI tracking data."""
    
    def __init__(self, database_file="health_records.db"):
        self.database_file = database_file
        self._initialize_schema()
    
    @contextmanager
    def _get_db_connection(self):
        """Context manager for database connections."""
        connection = sqlite3.connect(self.database_file)
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
    
    def _initialize_schema(self):
        """Create database tables if they don't exist."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # BMI records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bmi_entries (
                    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    body_weight REAL NOT NULL,
                    body_height REAL NOT NULL,
                    bmi_value REAL NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            """)
    
    def register_user(self, username):
        """Add a new user to the system."""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO user_profiles (username) VALUES (?)",
                    (username,)
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None  # Username already exists
    
    def fetch_all_users(self):
        """Retrieve all registered users."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, username FROM user_profiles ORDER BY username ASC"
            )
            return cursor.fetchall()
    
    def save_bmi_entry(self, user_id, weight, height, bmi):
        """Store a new BMI calculation record."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO bmi_entries (user_id, body_weight, body_height, bmi_value)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, weight, height, bmi)
            )
            return cursor.lastrowid
    
    def fetch_user_history(self, user_id):
        """Get all BMI records for a specific user."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT body_weight, body_height, bmi_value, recorded_at
                FROM bmi_entries
                WHERE user_id = ?
                ORDER BY recorded_at ASC
                """,
                (user_id,)
            )
            return cursor.fetchall()
    
    def remove_user_history(self, user_id):
        """Delete all BMI records for a specific user."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM bmi_entries WHERE user_id = ?",
                (user_id,)
            )
    
    def delete_user(self, user_id):
        """Delete a user and all their BMI records from the system."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            # First delete all BMI entries for this user
            cursor.execute(
                "DELETE FROM bmi_entries WHERE user_id = ?",
                (user_id,)
            )
            # Then delete the user profile
            cursor.execute(
                "DELETE FROM user_profiles WHERE user_id = ?",
                (user_id,)
            )
            return cursor.rowcount > 0

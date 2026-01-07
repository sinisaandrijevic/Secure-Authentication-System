import bcrypt
import sqlite3
import datetime

# ======================================================
# CONFIG
# ======================================================

DB_NAME = "users.db"
MAX_FAILED_ATTEMPTS = 3

# Toggle this to True ONLY for demonstrations
# NEVER enable in real applications
VULNERABLE_MODE = False

AUDIT_LOG_FILE = "auth_audit.log"


# ======================================================
# DATABASE
# ======================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,
            failed_attempts INTEGER DEFAULT 0,
            locked INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ======================================================
# AUDIT LOGGING
# ======================================================

def audit_log(event: str, username: str, success: bool, details: str = ""):
    ts = datetime.datetime.utcnow().isoformat()
    line = f"{ts} | {event.upper()} | user={username} | success={success} | {details}\n"
    with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


# ======================================================
# PASSWORD UTILITIES
# ======================================================

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed)


# ======================================================
# USER MANAGEMENT
# ======================================================

def register_user(username: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    try:
        password_hash = hash_password(password)
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, failed_attempts, locked, created_at)
            VALUES (?, ?, 0, 0, ?)
            """,
            (username, password_hash, datetime.datetime.utcnow().isoformat()),
        )
        conn.commit()
        audit_log("register", username, True)
        return True

    except sqlite3.IntegrityError:
        audit_log("register", username, False, "username_exists")
        return False

    finally:
        conn.close()


def _get_user_safe(username: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password_hash, failed_attempts, locked FROM users WHERE username = ?",
        (username,),
    )

    row = cursor.fetchone()
    conn.close()
    return row


def _get_user_vulnerable(username: str):
    # INTENTIONALLY VULNERABLE (for demo purposes only)
    conn = get_connection()
    cursor = conn.cursor()

    query = f"""
        SELECT password_hash, failed_attempts, locked
        FROM users
        WHERE username = '{username}'
    """

    cursor.execute(query)
    row = cursor.fetchone()
    conn.close()
    return row


def _update_attempts(username: str, failed: int, locked: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET failed_attempts = ?, locked = ?
        WHERE username = ?
        """,
        (failed, locked, username),
    )

    conn.commit()
    conn.close()


# ======================================================
# AUTHENTICATION
# ======================================================

def login_user(username: str, password: str):
    """
    Secure authentication (default)

    Returns:
      ("ok", None)
      ("not_found", None)
      ("locked", None)
      ("invalid", remaining_attempts)
    """

    if VULNERABLE_MODE:
        return login_user_vulnerable(username, password)

    row = _get_user_safe(username)

    if row is None:
        audit_log("login", username, False, "user_not_found")
        return ("not_found", None)

    password_hash, failed_attempts, locked = row

    if locked:
        audit_log("login", username, False, "account_locked")
        return ("locked", None)

    if check_password(password, password_hash):
        _update_attempts(username, 0, 0)
        audit_log("login", username, True)
        return ("ok", None)

    failed_attempts += 1
    locked = 1 if failed_attempts >= MAX_FAILED_ATTEMPTS else 0
    _update_attempts(username, failed_attempts, locked)

    if locked:
        audit_log("login", username, False, "locked_after_failures")
        return ("locked", None)

    audit_log("login", username, False, f"invalid_password remaining={MAX_FAILED_ATTEMPTS - failed_attempts}")
    return ("invalid", MAX_FAILED_ATTEMPTS - failed_attempts)


# ======================================================
# VULNERABLE AUTH (SQL INJECTION DEMO)
# ======================================================

def login_user_vulnerable(username: str, password: str):
    """
    ❌ INTENTIONALLY INSECURE
    Demonstrates SQL Injection vulnerability.
    DO NOT USE IN PRODUCTION.
    """

    row = _get_user_vulnerable(username)

    if row is None:
        audit_log("login_vulnerable", username, False, "user_not_found")
        return ("not_found", None)

    password_hash, failed_attempts, locked = row

    # In vulnerable mode we *pretend* password matches
    audit_log("login_vulnerable", username, True, "sql_injection_possible")
    return ("ok", None)


# ======================================================
# INITIALIZATION
# ======================================================

if __name__ == "__main__":
    init_db()
    print("Auth database initialized.")
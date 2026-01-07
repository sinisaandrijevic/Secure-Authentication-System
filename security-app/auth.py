import bcrypt
import sqlite3

DB_NAME = "users.db"
MAX_FAILED_ATTEMPTS = 3


def get_connection():
    return sqlite3.connect(DB_NAME)


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)


def register_user(username: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, failed_attempts, locked) VALUES (?, ?, 0, 0)",
            (username, password_hash),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def _get_user(username: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password_hash, failed_attempts, locked FROM users WHERE username = ?",
        (username,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def _update_attempts(username: str, failed: int, locked: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET failed_attempts = ?, locked = ? WHERE username = ?",
        (failed, locked, username),
    )
    conn.commit()
    conn.close()


def login_user(username: str, password: str):
    """
    Returns:
      ("ok", None)
      ("not_found", None)
      ("locked", None)
      ("invalid", remaining_attempts)
    """
    row = _get_user(username)
    if row is None:
        return ("not_found", None)

    password_hash, failed_attempts, locked = row

    if locked:
        return ("locked", None)

    if check_password(password, password_hash):
        _update_attempts(username, 0, 0)
        return ("ok", None)

    failed_attempts += 1
    locked = 1 if failed_attempts >= MAX_FAILED_ATTEMPTS else 0
    _update_attempts(username, failed_attempts, locked)

    if locked:
        return ("locked", None)

    return ("invalid", MAX_FAILED_ATTEMPTS - failed_attempts)
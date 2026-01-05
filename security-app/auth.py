import bcrypt
import sqlite3

DB_NAME = "users.db"


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
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_user(username: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return False

    return check_password(password, row[0])

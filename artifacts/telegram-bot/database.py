import sqlite3
import secrets
import string
from datetime import datetime, timedelta
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            subscription_expiry TEXT,
            join_date TEXT,
            total_generations INTEGER DEFAULT 0,
            total_cards_generated INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS licenses (
            key TEXT PRIMARY KEY,
            duration_value INTEGER NOT NULL,
            duration_unit TEXT NOT NULL,
            is_used INTEGER DEFAULT 0,
            used_by INTEGER,
            used_at TEXT,
            created_at TEXT,
            created_by INTEGER
        );

        CREATE TABLE IF NOT EXISTS stats (
            stat_name TEXT PRIMARY KEY,
            stat_value INTEGER DEFAULT 0
        );
    """)
    for stat in ("total_users", "total_licenses_generated", "total_licenses_redeemed", "total_cc_generated"):
        c.execute("INSERT OR IGNORE INTO stats (stat_name, stat_value) VALUES (?, 0)", (stat,))
    conn.commit()
    conn.close()


def increment_stat(stat_name: str, amount: int = 1):
    conn = get_conn()
    conn.execute("UPDATE stats SET stat_value = stat_value + ? WHERE stat_name = ?", (amount, stat_name))
    conn.commit()
    conn.close()


def get_stats() -> dict:
    conn = get_conn()
    rows = conn.execute("SELECT stat_name, stat_value FROM stats").fetchall()
    conn.close()
    return {r["stat_name"]: r["stat_value"] for r in rows}


def get_user(user_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_or_update_user(user_id: int, username: str, first_name: str):
    conn = get_conn()
    existing = conn.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO users (user_id, username, first_name, join_date) VALUES (?, ?, ?, ?)",
            (user_id, username, first_name, datetime.utcnow().isoformat())
        )
        increment_stat("total_users")
    else:
        conn.execute(
            "UPDATE users SET username = ?, first_name = ? WHERE user_id = ?",
            (username, first_name, user_id)
        )
    conn.commit()
    conn.close()


def is_user_active(user_id: int) -> bool:
    user = get_user(user_id)
    if not user or not user.get("subscription_expiry"):
        return False
    expiry = datetime.fromisoformat(user["subscription_expiry"])
    return datetime.utcnow() < expiry


def get_subscription_expiry(user_id: int):
    user = get_user(user_id)
    if not user or not user.get("subscription_expiry"):
        return None
    return datetime.fromisoformat(user["subscription_expiry"])


def apply_license_to_user(user_id: int, duration_value: int, duration_unit: str):
    unit_map = {"M": "minutes", "H": "hours", "D": "days"}
    unit = unit_map.get(duration_unit.upper(), "hours")
    delta = timedelta(**{unit: duration_value})
    now = datetime.utcnow()
    user = get_user(user_id)
    if user and user.get("subscription_expiry"):
        current_expiry = datetime.fromisoformat(user["subscription_expiry"])
        if current_expiry > now:
            new_expiry = current_expiry + delta
        else:
            new_expiry = now + delta
    else:
        new_expiry = now + delta
    conn = get_conn()
    conn.execute(
        "UPDATE users SET subscription_expiry = ? WHERE user_id = ?",
        (new_expiry.isoformat(), user_id)
    )
    conn.commit()
    conn.close()
    return new_expiry


def generate_license_keys(count: int, duration_value: int, duration_unit: str, created_by: int) -> list:
    alphabet = string.ascii_uppercase + string.digits
    keys = []
    conn = get_conn()
    for _ in range(count):
        key = "-".join("".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(4))
        conn.execute(
            "INSERT INTO licenses (key, duration_value, duration_unit, created_at, created_by) VALUES (?, ?, ?, ?, ?)",
            (key, duration_value, duration_unit.upper(), datetime.utcnow().isoformat(), created_by)
        )
        keys.append(key)
    conn.commit()
    conn.close()
    increment_stat("total_licenses_generated", count)
    return keys


def redeem_license(key: str, user_id: int):
    conn = get_conn()
    lic = conn.execute("SELECT * FROM licenses WHERE key = ?", (key.upper(),)).fetchone()
    if not lic:
        conn.close()
        return False, "❌ Invalid license key."
    lic = dict(lic)
    if lic["is_used"]:
        conn.close()
        return False, "❌ This license key has already been redeemed."
    conn.execute(
        "UPDATE licenses SET is_used = 1, used_by = ?, used_at = ? WHERE key = ?",
        (user_id, datetime.utcnow().isoformat(), key.upper())
    )
    conn.commit()
    conn.close()
    expiry = apply_license_to_user(user_id, lic["duration_value"], lic["duration_unit"])
    increment_stat("total_licenses_redeemed")
    return True, expiry


def update_user_stats(user_id: int, cards_count: int):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET total_generations = total_generations + 1, total_cards_generated = total_cards_generated + ? WHERE user_id = ?",
        (cards_count, user_id)
    )
    conn.commit()
    conn.close()
    increment_stat("total_cc_generated", cards_count)


def get_all_users() -> list:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM users ORDER BY join_date DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_active_users_count() -> int:
    conn = get_conn()
    now = datetime.utcnow().isoformat()
    count = conn.execute(
        "SELECT COUNT(*) as cnt FROM users WHERE subscription_expiry > ?", (now,)
    ).fetchone()["cnt"]
    conn.close()
    return count


def revoke_user(user_id: int):
    conn = get_conn()
    conn.execute("UPDATE users SET subscription_expiry = NULL WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_all_licenses(limit: int = 20) -> list:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM licenses ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

import sqlite3
import secrets
import string
import threading
from datetime import datetime, timedelta
from config import DB_PATH

_lock = threading.Lock()
_conn: sqlite3.Connection = None


def _get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("PRAGMA synchronous=NORMAL")
        _conn.execute("PRAGMA busy_timeout=30000")
    return _conn


def init_db():
    with _lock:
        c = _get_conn()
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

            CREATE TABLE IF NOT EXISTS custom_bins (
                bin TEXT PRIMARY KEY,
                bank_name TEXT NOT NULL,
                country_code TEXT NOT NULL,
                country_name TEXT NOT NULL,
                network TEXT NOT NULL,
                card_type TEXT NOT NULL,
                added_by INTEGER,
                added_at TEXT
            );
        """)
        for stat in ("total_users", "total_licenses_generated", "total_licenses_redeemed", "total_cc_generated", "total_custom_bins"):
            c.execute("INSERT OR IGNORE INTO stats (stat_name, stat_value) VALUES (?, 0)", (stat,))
        c.commit()


def increment_stat(stat_name: str, amount: int = 1):
    with _lock:
        db = _get_conn()
        db.execute("UPDATE stats SET stat_value = stat_value + ? WHERE stat_name = ?", (amount, stat_name))
        db.commit()


def get_stats() -> dict:
    with _lock:
        db = _get_conn()
        rows = db.execute("SELECT stat_name, stat_value FROM stats").fetchall()
    return {r["stat_name"]: r["stat_value"] for r in rows}


def get_user(user_id: int):
    with _lock:
        db = _get_conn()
        row = db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def add_or_update_user(user_id: int, username: str, first_name: str):
    is_new = False
    with _lock:
        db = _get_conn()
        existing = db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not existing:
            db.execute(
                "INSERT INTO users (user_id, username, first_name, join_date) VALUES (?, ?, ?, ?)",
                (user_id, username, first_name, datetime.utcnow().isoformat())
            )
            is_new = True
        else:
            db.execute(
                "UPDATE users SET username = ?, first_name = ? WHERE user_id = ?",
                (username, first_name, user_id)
            )
        db.commit()
    if is_new:
        increment_stat("total_users")


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
        new_expiry = (current_expiry + delta) if current_expiry > now else (now + delta)
    else:
        new_expiry = now + delta
    with _lock:
        db = _get_conn()
        db.execute(
            "UPDATE users SET subscription_expiry = ? WHERE user_id = ?",
            (new_expiry.isoformat(), user_id)
        )
        db.commit()
    return new_expiry


def generate_license_keys(count: int, duration_value: int, duration_unit: str, created_by: int) -> list:
    alphabet = string.ascii_uppercase + string.digits
    keys = []
    with _lock:
        db = _get_conn()
        for _ in range(count):
            key = "-".join("".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(4))
            db.execute(
                "INSERT INTO licenses (key, duration_value, duration_unit, created_at, created_by) VALUES (?, ?, ?, ?, ?)",
                (key, duration_value, duration_unit.upper(), datetime.utcnow().isoformat(), created_by)
            )
            keys.append(key)
        db.commit()
    increment_stat("total_licenses_generated", count)
    return keys


def redeem_license(key: str, user_id: int):
    with _lock:
        db = _get_conn()
        lic = db.execute("SELECT * FROM licenses WHERE key = ?", (key.upper(),)).fetchone()
        if not lic:
            return False, "❌ Invalid license key."
        lic = dict(lic)
        if lic["is_used"]:
            return False, "❌ This license key has already been redeemed."
        db.execute(
            "UPDATE licenses SET is_used = 1, used_by = ?, used_at = ? WHERE key = ?",
            (user_id, datetime.utcnow().isoformat(), key.upper())
        )
        db.commit()
    expiry = apply_license_to_user(user_id, lic["duration_value"], lic["duration_unit"])
    increment_stat("total_licenses_redeemed")
    return True, expiry


def update_user_stats(user_id: int, cards_count: int):
    with _lock:
        db = _get_conn()
        db.execute(
            "UPDATE users SET total_generations = total_generations + 1, total_cards_generated = total_cards_generated + ? WHERE user_id = ?",
            (cards_count, user_id)
        )
        db.commit()
    increment_stat("total_cc_generated", cards_count)


def get_all_users() -> list:
    with _lock:
        db = _get_conn()
        rows = db.execute("SELECT * FROM users ORDER BY join_date DESC").fetchall()
    return [dict(r) for r in rows]


def get_active_users_count() -> int:
    with _lock:
        db = _get_conn()
        now = datetime.utcnow().isoformat()
        count = db.execute(
            "SELECT COUNT(*) as cnt FROM users WHERE subscription_expiry > ?", (now,)
        ).fetchone()["cnt"]
    return count


def revoke_user(user_id: int):
    with _lock:
        db = _get_conn()
        db.execute("UPDATE users SET subscription_expiry = NULL WHERE user_id = ?", (user_id,))
        db.commit()


def get_all_licenses(limit: int = 20) -> list:
    with _lock:
        db = _get_conn()
        rows = db.execute(
            "SELECT * FROM licenses ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


# ─── Custom BIN Management ───────────────────────────────────────────────────

def bin_exists(bin_code: str) -> bool:
    with _lock:
        db = _get_conn()
        row = db.execute("SELECT bin FROM custom_bins WHERE bin = ?", (bin_code.strip(),)).fetchone()
    return row is not None


def add_custom_bin(bin_code: str, bank_name: str, country_code: str, country_name: str,
                   network: str, card_type: str, added_by: int) -> bool:
    bin_code = bin_code.strip()
    if bin_exists(bin_code):
        return False
    with _lock:
        db = _get_conn()
        db.execute(
            "INSERT INTO custom_bins (bin, bank_name, country_code, country_name, network, card_type, added_by, added_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (bin_code, bank_name, country_code.upper(), country_name,
             network, card_type, added_by, datetime.utcnow().isoformat())
        )
        db.commit()
    increment_stat("total_custom_bins")
    return True


def delete_custom_bin(bin_code: str) -> bool:
    with _lock:
        db = _get_conn()
        result = db.execute("DELETE FROM custom_bins WHERE bin = ?", (bin_code.strip(),))
        db.commit()
    if result.rowcount > 0:
        increment_stat("total_custom_bins", -1)
        return True
    return False


def get_custom_bins(limit: int = 50, country_code: str = None) -> list:
    with _lock:
        db = _get_conn()
        if country_code:
            rows = db.execute(
                "SELECT * FROM custom_bins WHERE country_code = ? ORDER BY added_at DESC LIMIT ?",
                (country_code.upper(), limit)
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM custom_bins ORDER BY added_at DESC LIMIT ?", (limit,)
            ).fetchall()
    return [dict(r) for r in rows]


def get_all_custom_bins() -> list:
    with _lock:
        db = _get_conn()
        rows = db.execute("SELECT * FROM custom_bins").fetchall()
    return [dict(r) for r in rows]


def get_custom_bins_count() -> int:
    with _lock:
        db = _get_conn()
        count = db.execute("SELECT COUNT(*) as cnt FROM custom_bins").fetchone()["cnt"]
    return count

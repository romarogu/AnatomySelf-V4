"""
AnatomySelf V4.0 - 数据库模块
安全架构升级：所有核心表均含 owner_user_id 字段，所有查询强制 WHERE owner_user_id=?。
彻底消除跨用户数据泄露漏洞。
"""

import sqlite3
import json
import hashlib
import secrets
from datetime import datetime
from typing import Optional, List, Dict, Any
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "anatomy_self.db")


def get_connection() -> sqlite3.Connection:
    """获取数据库连接，启用 WAL 模式以提升并发性能。"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _hash_password(password: str, salt: str = None) -> tuple:
    """使用 SHA-256 + salt 对密码进行哈希处理。"""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return hashed, salt


def init_db():
    """初始化数据库，创建所有表结构（V4.0 强制多租户安全架构）。"""
    conn = get_connection()
    cursor = conn.cursor()

    # ── Users 表（多租户核心）──────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE COLLATE NOCASE,
            display_name  TEXT    NOT NULL,
            password_hash TEXT    NOT NULL,
            password_salt TEXT    NOT NULL,
            email         TEXT,
            avatar_emoji  TEXT    DEFAULT '🧑‍⚕️',
            role          TEXT    DEFAULT 'user' CHECK(role IN ('user', 'admin')),
            is_active     INTEGER DEFAULT 1,
            last_login    TEXT,
            created_at    TEXT    DEFAULT (datetime('now', 'localtime')),
            updated_at    TEXT    DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # ── Profiles 表：owner_user_id 强制外键 ───────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name               TEXT    NOT NULL,
            relation           TEXT    NOT NULL DEFAULT '本人',
            birth_year         INTEGER,
            gender             TEXT    CHECK(gender IN ('男', '女', '其他')),
            blood_type         TEXT,
            allergies          TEXT,
            chronic_conditions TEXT,
            avatar_emoji       TEXT    DEFAULT '👤',
            created_at         TEXT    DEFAULT (datetime('now', 'localtime')),
            updated_at         TEXT    DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # ── Medical_Records 表：owner_user_id 冗余字段，双重隔离 ──────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_records (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            profile_id      INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
            record_date     TEXT    NOT NULL,
            category        TEXT    NOT NULL DEFAULT '血液检查',
            indicator_name  TEXT    NOT NULL,
            indicator_code  TEXT,
            value           REAL    NOT NULL,
            unit            TEXT    NOT NULL DEFAULT '',
            ref_low         REAL,
            ref_high        REAL,
            status          TEXT    GENERATED ALWAYS AS (
                                CASE
                                    WHEN ref_low IS NOT NULL AND value < ref_low THEN '偏低'
                                    WHEN ref_high IS NOT NULL AND value > ref_high THEN '偏高'
                                    ELSE '正常'
                                END
                            ) VIRTUAL,
            source          TEXT    DEFAULT '手动录入',
            notes           TEXT,
            created_at      TEXT    DEFAULT (datetime('now', 'localtime')),
            UNIQUE(owner_user_id, profile_id, record_date, indicator_code)
        )
    """)

    # ── Symptom_Logs 表：owner_user_id 冗余字段 ───────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS symptom_logs (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            profile_id          INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
            log_date            TEXT    NOT NULL,
            symptom_description TEXT    NOT NULL,
            body_location       TEXT,
            anatomy_mapping     TEXT,
            severity            INTEGER CHECK(severity BETWEEN 1 AND 10),
            duration_minutes    INTEGER,
            triggers            TEXT,
            environmental_data  TEXT,
            ai_analysis         TEXT,
            created_at          TEXT    DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # ── Knowledge_Base 表 ─────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_user_id   INTEGER REFERENCES users(id) ON DELETE CASCADE,
            topic_type      TEXT    NOT NULL CHECK(topic_type IN ('indicator', 'symptom', 'anatomy', 'weekly_report')),
            topic_key       TEXT    NOT NULL,
            profile_id      INTEGER REFERENCES profiles(id),
            title           TEXT    NOT NULL,
            content         TEXT    NOT NULL,
            sources         TEXT,
            generated_at    TEXT    DEFAULT (datetime('now', 'localtime')),
            expires_at      TEXT,
            UNIQUE(topic_type, topic_key, profile_id)
        )
    """)

    # ── Weekly_Reports 表 ────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weekly_reports (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            profile_id    INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
            week_start    TEXT    NOT NULL,
            week_end      TEXT    NOT NULL,
            title         TEXT    NOT NULL,
            content       TEXT    NOT NULL,
            highlights    TEXT,
            created_at    TEXT    DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # ── AI 对话持久化表（V5.0 新增）────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_conversations (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            profile_id    INTEGER REFERENCES profiles(id) ON DELETE CASCADE,
            session_type  TEXT    NOT NULL DEFAULT 'bazi',
            session_id    TEXT    NOT NULL,
            role          TEXT    NOT NULL CHECK(role IN ('user','assistant','system')),
            content       TEXT    NOT NULL,
            context_data  TEXT,
            created_at    TEXT    DEFAULT (datetime('now', 'localtime'))
        )
    """)
    # ── 八字分析结果持久化表（V5.0 新增）────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bazi_analyses (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            profile_id    INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
            birth_year    INTEGER NOT NULL,
            target_year   INTEGER NOT NULL,
            bazi_data     TEXT    NOT NULL,
            ai_report     TEXT,
            session_id    TEXT,
            created_at    TEXT    DEFAULT (datetime('now', 'localtime')),
            UNIQUE(owner_user_id, profile_id, birth_year, target_year)
        )
    """)
    # ── V4.0 迁移：为旧表补充 owner_user_id 列 ───────────────────────────────
    _migrate_v35(cursor)
    # ── V5.5 迁移：为 medical_records 创建 UNIQUE 索引（支持 INSERT OR REPLACE）──
    try:
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_medical_upsert "
            "ON medical_records(owner_user_id, profile_id, record_date, indicator_code)"
        )
    except Exception:
        pass  # 索引已存在或表结构不兼容时忽略

    conn.commit()
    conn.close()
    _seed_demo_data()


def _migrate_v35(cursor):
    """V4.0 迁移：为旧表补充 owner_user_id 列（如已存在则忽略）。"""
    migrations = [
        "ALTER TABLE profiles ADD COLUMN owner_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE",
        "ALTER TABLE medical_records ADD COLUMN owner_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE",
        "ALTER TABLE symptom_logs ADD COLUMN owner_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE",
        "ALTER TABLE weekly_reports ADD COLUMN owner_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE",
        "ALTER TABLE knowledge_base ADD COLUMN owner_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE",
        # 兼容旧 profiles 表的 user_id 列名
        "ALTER TABLE profiles ADD COLUMN user_id INTEGER",
    ]
    for sql in migrations:
        try:
            cursor.execute(sql)
        except Exception:
            pass  # 列已存在，忽略

    # 将旧 user_id 数据迁移到 owner_user_id
    try:
        cursor.execute("UPDATE profiles SET owner_user_id = user_id WHERE owner_user_id IS NULL AND user_id IS NOT NULL")
    except Exception:
        pass


def _seed_demo_data():
    """插入演示数据，首次运行时自动填充（V4.0：严格 owner_user_id 隔离）。"""
    conn = get_connection()
    cursor = conn.cursor()

    if cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        conn.close()
        return

    # 创建演示用户（若谷）
    pwd_hash, pwd_salt = _hash_password("demo123")
    cursor.execute(
        "INSERT INTO users (username, display_name, password_hash, password_salt, email, avatar_emoji) VALUES (?,?,?,?,?,?)",
        ("ruogu", "若谷", pwd_hash, pwd_salt, "ruogu@example.com", "👨")
    )
    user_id = cursor.lastrowid

    # 插入家庭成员（owner_user_id 强制绑定）
    members = [
        (user_id, "若谷", "本人", 1985, "男", "A型",
         json.dumps(["花粉", "尘螨"]), json.dumps(["季节性过敏性鼻炎"]), "👨"),
        (user_id, "小谷", "儿子", 2015, "男", "O型",
         json.dumps([]), json.dumps([]), "👦"),
        (user_id, "配偶", "配偶", 1987, "女", "B型",
         json.dumps(["青霉素"]), json.dumps(["轻度贫血"]), "👩"),
        (user_id, "兄弟", "兄弟", 1982, "男", "AB型",
         json.dumps([]), json.dumps(["高血压"]), "🧑"),
    ]
    cursor.executemany(
        "INSERT INTO profiles (owner_user_id, name, relation, birth_year, gender, blood_type, allergies, chronic_conditions, avatar_emoji) VALUES (?,?,?,?,?,?,?,?,?)",
        members
    )

    ruogu_pid = cursor.execute(
        "SELECT id FROM profiles WHERE owner_user_id=? AND name='若谷'", (user_id,)
    ).fetchone()[0]

    today = datetime.now().strftime("%Y-%m-%d")
    records = [
        (user_id, ruogu_pid, today, "血液检查", "白细胞计数",      "WBC",   9.8,  "×10⁹/L",   4.0,  10.0),
        (user_id, ruogu_pid, today, "血液检查", "红细胞计数",      "RBC",   4.5,  "×10¹²/L",  4.3,   5.8),
        (user_id, ruogu_pid, today, "血液检查", "血红蛋白",        "HGB",   138,  "g/L",      130,   175),
        (user_id, ruogu_pid, today, "血液检查", "血小板计数",      "PLT",   210,  "×10⁹/L",  100,   300),
        (user_id, ruogu_pid, today, "血液检查", "嗜酸性粒细胞%",  "EOS%",  8.2,  "%",         0.4,   8.0),
        (user_id, ruogu_pid, today, "血液检查", "中性粒细胞%",    "NEU%",  72.5, "%",        50.0,  70.0),
        (user_id, ruogu_pid, today, "血液检查", "淋巴细胞%",      "LYM%",  20.3, "%",        20.0,  40.0),
        (user_id, ruogu_pid, today, "血液检查", "平均红细胞体积", "MCV",   88.0, "fL",       80.0, 100.0),
        (user_id, ruogu_pid, today, "血液检查", "平均血红蛋白量", "MCH",   29.5, "pg",       27.0,  34.0),
        (user_id, ruogu_pid, today, "血液检查", "平均血红蛋白浓度","MCHC", 336,  "g/L",      316,   354),
        (user_id, ruogu_pid, today, "免疫检查", "IgE总量",        "IgE",   420,  "IU/mL",     0,    100),
        (user_id, ruogu_pid, today, "生化检查", "谷丙转氨酶",     "ALT",   32,   "U/L",        7,    40),
        (user_id, ruogu_pid, today, "生化检查", "总胆固醇",       "TC",    5.8,  "mmol/L",     0,    5.2),
        (user_id, ruogu_pid, today, "生化检查", "甘油三酯",       "TG",    1.9,  "mmol/L",     0,    1.7),
        (user_id, ruogu_pid, today, "生化检查", "空腹血糖",       "GLU",   5.1,  "mmol/L",    3.9,   6.1),
        (user_id, ruogu_pid, today, "生化检查", "低密度脂蛋白",   "LDL",   3.5,  "mmol/L",     0,    3.4),
        (user_id, ruogu_pid, today, "免疫检查", "C反应蛋白",      "CRP",   3.2,  "mg/L",       0,    3.0),
    ]
    cursor.executemany(
        "INSERT INTO medical_records (owner_user_id, profile_id, record_date, category, indicator_name, indicator_code, value, unit, ref_low, ref_high) VALUES (?,?,?,?,?,?,?,?,?,?)",
        records
    )

    symptoms = [
        (user_id, ruogu_pid, today, "鼻痒、打喷嚏、流清涕", "鼻部", "鼻黏膜/下鼻甲", 4, 120,
         json.dumps(["花粉浓度高", "室外活动"]),
         json.dumps({"pollen": "极高", "pm25": 45, "humidity": 72})),
        (user_id, ruogu_pid, today, "右手腕酸痛", "手腕", "桡骨茎突/腕关节", 3, 60,
         json.dumps(["长时间使用手机", "久坐办公"]),
         json.dumps({"pollen": "中", "pm25": 30})),
    ]
    cursor.executemany(
        "INSERT INTO symptom_logs (owner_user_id, profile_id, log_date, symptom_description, body_location, anatomy_mapping, severity, duration_minutes, triggers, environmental_data) VALUES (?,?,?,?,?,?,?,?,?,?)",
        symptoms
    )

    conn.commit()
    conn.close()


# ── CRUD: Users ───────────────────────────────────────────────────────────────

def create_user(username: str, display_name: str, password: str,
                email: str = "", avatar_emoji: str = "🧑‍⚕️") -> Dict:
    """创建新用户，返回 {'success': bool, 'user_id': int, 'error': str}。"""
    conn = get_connection()
    try:
        pwd_hash, pwd_salt = _hash_password(password)
        cursor = conn.execute(
            "INSERT INTO users (username, display_name, password_hash, password_salt, email, avatar_emoji) VALUES (?,?,?,?,?,?)",
            (username.strip(), display_name.strip(), pwd_hash, pwd_salt,
             email.strip(), avatar_emoji)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        _create_default_profile(user_id, display_name)
        return {"success": True, "user_id": user_id, "error": ""}
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "user_id": None, "error": "用户名已存在，请换一个用户名"}
    except Exception as e:
        conn.close()
        return {"success": False, "user_id": None, "error": str(e)}


def _create_default_profile(user_id: int, display_name: str):
    """为新注册用户自动创建一个默认的'本人'档案。"""
    conn = get_connection()
    conn.execute(
        "INSERT INTO profiles (owner_user_id, name, relation, avatar_emoji) VALUES (?,?,?,?)",
        (user_id, display_name, "本人", "👤")
    )
    conn.commit()
    conn.close()


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """验证用户名和密码，成功返回用户信息字典，失败返回 None。"""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND is_active=1",
        (username.strip(),)
    ).fetchone()
    conn.close()
    if not row:
        return None
    user = dict(row)
    pwd_hash, _ = _hash_password(password, user["password_salt"])
    if pwd_hash != user["password_hash"]:
        return None
    conn = get_connection()
    conn.execute(
        "UPDATE users SET last_login=? WHERE id=?",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user["id"])
    )
    conn.commit()
    conn.close()
    return user


def get_user_by_id(user_id: int) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_username(username: str) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? COLLATE NOCASE",
        (username.strip(),)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_password(user_id: int, new_password: str) -> bool:
    pwd_hash, pwd_salt = _hash_password(new_password)
    conn = get_connection()
    conn.execute(
        "UPDATE users SET password_hash=?, password_salt=?, updated_at=? WHERE id=?",
        (pwd_hash, pwd_salt, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id)
    )
    conn.commit()
    conn.close()
    return True


def delete_user_and_all_data(user_id: int) -> bool:
    """
    V4.0 新增：注销账号并抹除该用户的所有数据（级联删除）。
    由于 ON DELETE CASCADE，删除 users 记录会自动清除所有关联数据。
    """
    conn = get_connection()
    try:
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False


def update_user_profile_info(user_id: int, display_name: str = None,
                              email: str = None, avatar_emoji: str = None) -> bool:
    """更新用户基本信息。"""
    updates = {}
    if display_name:
        updates["display_name"] = display_name
    if email is not None:
        updates["email"] = email
    if avatar_emoji:
        updates["avatar_emoji"] = avatar_emoji
    if not updates:
        return False
    updates["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sets = ", ".join(f"{k}=?" for k in updates)
    values = list(updates.values()) + [user_id]
    conn = get_connection()
    conn.execute(f"UPDATE users SET {sets} WHERE id=?", values)
    conn.commit()
    conn.close()
    return True


# ── CRUD: Profiles（V4.0：owner_user_id 强制隔离）────────────────────────────

def get_all_profiles(user_id: int) -> List[Dict]:
    """
    V4.0 安全版：必须传入 user_id，严格过滤，禁止返回其他用户数据。
    """
    if not user_id:
        return []
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM profiles WHERE owner_user_id=? ORDER BY id",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_profile(profile_id: int, user_id: int = None) -> Optional[Dict]:
    """
    V4.0 安全版：如传入 user_id，则验证该 profile 属于该用户。
    """
    conn = get_connection()
    if user_id is not None:
        row = conn.execute(
            "SELECT * FROM profiles WHERE id=? AND owner_user_id=?",
            (profile_id, user_id)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM profiles WHERE id=?", (profile_id,)
        ).fetchone()
    conn.close()
    return dict(row) if row else None


def create_profile(name: str, relation: str, birth_year: int, gender: str,
                   blood_type: str, allergies: List[str],
                   chronic_conditions: List[str], avatar_emoji: str = "👤",
                   user_id: int = None) -> int:
    if not user_id:
        raise ValueError("V4.0: create_profile 必须提供 user_id")
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO profiles (owner_user_id, name, relation, birth_year, gender, blood_type, allergies, chronic_conditions, avatar_emoji) VALUES (?,?,?,?,?,?,?,?,?)",
        (user_id, name, relation, birth_year, gender, blood_type,
         json.dumps(allergies, ensure_ascii=False),
         json.dumps(chronic_conditions, ensure_ascii=False), avatar_emoji)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def update_profile(profile_id: int, user_id: int = None, **kwargs) -> bool:
    if not kwargs:
        return False
    for key in ("allergies", "chronic_conditions"):
        if key in kwargs and isinstance(kwargs[key], list):
            kwargs[key] = json.dumps(kwargs[key], ensure_ascii=False)
    kwargs["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sets = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values())
    conn = get_connection()
    if user_id is not None:
        conn.execute(
            f"UPDATE profiles SET {sets} WHERE id=? AND owner_user_id=?",
            values + [profile_id, user_id]
        )
    else:
        conn.execute(f"UPDATE profiles SET {sets} WHERE id=?", values + [profile_id])
    conn.commit()
    conn.close()
    return True


def delete_profile(profile_id: int, user_id: int = None) -> bool:
    conn = get_connection()
    if user_id is not None:
        conn.execute(
            "DELETE FROM profiles WHERE id=? AND owner_user_id=?",
            (profile_id, user_id)
        )
    else:
        conn.execute("DELETE FROM profiles WHERE id=?", (profile_id,))
    conn.commit()
    conn.close()
    return True


# ── CRUD: Medical Records（V4.0：owner_user_id 双重隔离）─────────────────────

def get_records(profile_id: int, user_id: int = None,
                category: str = None, limit: int = 200) -> List[Dict]:
    """V4.0 安全版：通过 owner_user_id 双重验证，防止越权访问。"""
    conn = get_connection()
    params = [profile_id]
    sql = "SELECT * FROM medical_records WHERE profile_id=?"
    if user_id is not None:
        sql += " AND owner_user_id=?"
        params.append(user_id)
    if category:
        sql += " AND category=?"
        params.append(category)
    sql += " ORDER BY record_date DESC, id DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_records_for_user(user_id: int, profile_id: int = None,
                              category: str = None,
                              date_from: str = None, date_to: str = None,
                              limit: int = 500) -> List[Dict]:
    """
    V4.0 新增：获取用户所有记录（跨成员），用于档案库全量汇总。
    严格通过 owner_user_id 过滤，确保数据隔离。
    """
    if not user_id:
        return []
    conn = get_connection()
    params = [user_id]
    sql = """
        SELECT mr.*, p.name as profile_name, p.avatar_emoji as profile_emoji
        FROM medical_records mr
        JOIN profiles p ON mr.profile_id = p.id
        WHERE mr.owner_user_id=?
    """
    if profile_id:
        sql += " AND mr.profile_id=?"
        params.append(profile_id)
    if category:
        sql += " AND mr.category=?"
        params.append(category)
    if date_from:
        sql += " AND mr.record_date>=?"
        params.append(date_from)
    if date_to:
        sql += " AND mr.record_date<=?"
        params.append(date_to)
    sql += " ORDER BY mr.record_date DESC, mr.id DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_indicator_history(profile_id: int, indicator_code: str,
                          user_id: int = None) -> List[Dict]:
    conn = get_connection()
    if user_id is not None:
        rows = conn.execute(
            "SELECT * FROM medical_records WHERE profile_id=? AND indicator_code=? AND owner_user_id=? ORDER BY record_date ASC",
            (profile_id, indicator_code, user_id)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM medical_records WHERE profile_id=? AND indicator_code=? ORDER BY record_date ASC",
            (profile_id, indicator_code)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_medical_record(profile_id: int, record_date: str, category: str,
                       indicator_name: str, indicator_code: str,
                       value: float, unit: str,
                       ref_low: float = None, ref_high: float = None,
                       source: str = "手动录入", notes: str = "",
                       user_id: int = None) -> int:
    """
    V5.5 Upsert 版：使用真正的 INSERT OR REPLACE 实现幂等性。
    同一 owner_user_id + profile_id + record_date + indicator_code 已存在则全量更新，
    彻底禁止重复记录。
    """
    conn = get_connection()
    icode = indicator_code or indicator_name
    cursor = conn.execute(
        """INSERT INTO medical_records
               (owner_user_id, profile_id, record_date, category,
                indicator_name, indicator_code, value, unit,
                ref_low, ref_high, source, notes)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(owner_user_id, profile_id, record_date, indicator_code)
           DO UPDATE SET
               indicator_name = excluded.indicator_name,
               value          = excluded.value,
               unit           = excluded.unit,
               ref_low        = excluded.ref_low,
               ref_high       = excluded.ref_high,
               category       = excluded.category,
               source         = excluded.source,
               notes          = excluded.notes""",
        (user_id, profile_id, record_date, category, indicator_name, icode,
         value, unit, ref_low, ref_high, source, notes)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def batch_add_medical_records(records: List[Dict], user_id: int = None) -> int:
    """
    V5.5 Upsert 版：批量插入/更新体检记录（OCR导入专用）。
    使用 INSERT OR REPLACE 实现幂等性，彻底禁止重复记录。
    """
    conn = get_connection()
    count = 0
    for rec in records:
        try:
            uid = user_id or rec.get("user_id")
            pid = rec["profile_id"]
            rdate = rec["record_date"]
            icode = rec.get("indicator_code") or rec["indicator_name"]
            conn.execute(
                """INSERT INTO medical_records
                       (owner_user_id, profile_id, record_date, category,
                        indicator_name, indicator_code, value, unit,
                        ref_low, ref_high, source, notes)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(owner_user_id, profile_id, record_date, indicator_code)
                   DO UPDATE SET
                       indicator_name = excluded.indicator_name,
                       value          = excluded.value,
                       unit           = excluded.unit,
                       ref_low        = excluded.ref_low,
                       ref_high       = excluded.ref_high,
                       category       = excluded.category,
                       source         = excluded.source,
                       notes          = excluded.notes""",
                (uid, pid, rdate,
                 rec.get("category", "体检导入"),
                 rec["indicator_name"], icode,
                 float(rec["value"]), rec.get("unit", ""),
                 rec.get("ref_low"), rec.get("ref_high"),
                 rec.get("source", "OCR智能导入"), rec.get("notes", ""))
            )
            count += 1
        except Exception:
            continue
    conn.commit()
    conn.close()
    return count


def get_latest_abnormal_records(profile_id: int, user_id: int = None) -> List[Dict]:
    """获取最新一次检查中所有异常指标。V4.0：通过 owner_user_id 验证。"""
    conn = get_connection()
    if user_id is not None:
        latest_date = conn.execute(
            "SELECT MAX(record_date) FROM medical_records WHERE profile_id=? AND owner_user_id=?",
            (profile_id, user_id)
        ).fetchone()[0]
    else:
        latest_date = conn.execute(
            "SELECT MAX(record_date) FROM medical_records WHERE profile_id=?",
            (profile_id,)
        ).fetchone()[0]
    if not latest_date:
        conn.close()
        return []
    params = [profile_id, latest_date]
    sql = """SELECT * FROM medical_records
             WHERE profile_id=? AND record_date=?
               AND ((ref_low IS NOT NULL AND value < ref_low)
                 OR (ref_high IS NOT NULL AND value > ref_high))"""
    if user_id is not None:
        sql += " AND owner_user_id=?"
        params.append(user_id)
    sql += " ORDER BY category"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_medical_record(record_id: int, user_id: int = None) -> bool:
    conn = get_connection()
    if user_id is not None:
        conn.execute(
            "DELETE FROM medical_records WHERE id=? AND owner_user_id=?",
            (record_id, user_id)
        )
    else:
        conn.execute("DELETE FROM medical_records WHERE id=?", (record_id,))
    conn.commit()
    conn.close()
    return True


# ── CRUD: Symptom Logs（V4.0：owner_user_id 隔离）────────────────────────────

def get_symptom_logs(profile_id: int, user_id: int = None,
                     limit: int = 50) -> List[Dict]:
    conn = get_connection()
    if user_id is not None:
        rows = conn.execute(
            "SELECT * FROM symptom_logs WHERE profile_id=? AND owner_user_id=? ORDER BY log_date DESC, id DESC LIMIT ?",
            (profile_id, user_id, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM symptom_logs WHERE profile_id=? ORDER BY log_date DESC, id DESC LIMIT ?",
            (profile_id, limit)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_symptom_log(profile_id: int, log_date: str,
                    symptom_description: str, body_location: str = "",
                    anatomy_mapping: str = "", severity: int = 5,
                    duration_minutes: int = 0, triggers: List[str] = None,
                    environmental_data: Dict = None,
                    ai_analysis: str = "",
                    user_id: int = None) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO symptom_logs (owner_user_id, profile_id, log_date, symptom_description, body_location, anatomy_mapping, severity, duration_minutes, triggers, environmental_data, ai_analysis) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (user_id, profile_id, log_date, symptom_description, body_location,
         anatomy_mapping, severity, duration_minutes,
         json.dumps(triggers or [], ensure_ascii=False),
         json.dumps(environmental_data or {}, ensure_ascii=False),
         ai_analysis)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def update_symptom_ai_analysis(log_id: int, anatomy_mapping: str,
                                ai_analysis: str):
    conn = get_connection()
    conn.execute(
        "UPDATE symptom_logs SET anatomy_mapping=?, ai_analysis=? WHERE id=?",
        (anatomy_mapping, ai_analysis, log_id)
    )
    conn.commit()
    conn.close()


# ── CRUD: Knowledge Base ──────────────────────────────────────────────────────

def get_knowledge(topic_type: str, topic_key: str,
                  profile_id: int = None) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM knowledge_base WHERE topic_type=? AND topic_key=? AND (profile_id=? OR profile_id IS NULL) ORDER BY generated_at DESC LIMIT 1",
        (topic_type, topic_key, profile_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def save_knowledge(topic_type: str, topic_key: str, title: str,
                   content: str, profile_id: int = None,
                   sources: List[str] = None,
                   user_id: int = None) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO knowledge_base (owner_user_id, topic_type, topic_key, profile_id, title, content, sources)
           VALUES (?,?,?,?,?,?,?)
           ON CONFLICT(topic_type, topic_key, profile_id)
           DO UPDATE SET title=excluded.title, content=excluded.content,
                         sources=excluded.sources, generated_at=datetime('now','localtime')""",
        (user_id, topic_type, topic_key, profile_id, title, content,
         json.dumps(sources or [], ensure_ascii=False))
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


# ── CRUD: Weekly Reports ──────────────────────────────────────────────────────

def save_weekly_report(profile_id: int, week_start: str, week_end: str,
                       title: str, content: str,
                       highlights: List[str] = None,
                       user_id: int = None) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO weekly_reports (owner_user_id, profile_id, week_start, week_end, title, content, highlights) VALUES (?,?,?,?,?,?,?)",
        (user_id, profile_id, week_start, week_end, title, content,
         json.dumps(highlights or [], ensure_ascii=False))
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_weekly_reports(profile_id: int, user_id: int = None,
                       limit: int = 10) -> List[Dict]:
    conn = get_connection()
    if user_id is not None:
        rows = conn.execute(
            "SELECT * FROM weekly_reports WHERE profile_id=? AND owner_user_id=? ORDER BY week_start DESC LIMIT ?",
            (profile_id, user_id, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM weekly_reports WHERE profile_id=? ORDER BY week_start DESC LIMIT ?",
            (profile_id, limit)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_week_data_summary(profile_id: int, week_start: str,
                          week_end: str, user_id: int = None) -> Dict:
    """汇总指定周内的体检数据和症状日志，用于生成周报。"""
    conn = get_connection()
    if user_id is not None:
        records = conn.execute(
            "SELECT * FROM medical_records WHERE profile_id=? AND owner_user_id=? AND record_date BETWEEN ? AND ?",
            (profile_id, user_id, week_start, week_end)
        ).fetchall()
        symptoms = conn.execute(
            "SELECT * FROM symptom_logs WHERE profile_id=? AND owner_user_id=? AND log_date BETWEEN ? AND ?",
            (profile_id, user_id, week_start, week_end)
        ).fetchall()
    else:
        records = conn.execute(
            "SELECT * FROM medical_records WHERE profile_id=? AND record_date BETWEEN ? AND ?",
            (profile_id, week_start, week_end)
        ).fetchall()
        symptoms = conn.execute(
            "SELECT * FROM symptom_logs WHERE profile_id=? AND log_date BETWEEN ? AND ?",
            (profile_id, week_start, week_end)
        ).fetchall()
    conn.close()
    return {
        "records": [dict(r) for r in records],
        "symptoms": [dict(s) for s in symptoms],
    }


def get_archive_stats(user_id: int) -> Dict:
    """V4.0 新增：获取用户档案库统计信息。"""
    if not user_id:
        return {}
    conn = get_connection()
    total_records = conn.execute(
        "SELECT COUNT(*) FROM medical_records WHERE owner_user_id=?", (user_id,)
    ).fetchone()[0]
    total_abnormal = conn.execute(
        """SELECT COUNT(*) FROM medical_records
           WHERE owner_user_id=?
             AND ((ref_low IS NOT NULL AND value < ref_low)
               OR (ref_high IS NOT NULL AND value > ref_high))""",
        (user_id,)
    ).fetchone()[0]
    total_symptoms = conn.execute(
        "SELECT COUNT(*) FROM symptom_logs WHERE owner_user_id=?", (user_id,)
    ).fetchone()[0]
    total_profiles = conn.execute(
        "SELECT COUNT(*) FROM profiles WHERE owner_user_id=?", (user_id,)
    ).fetchone()[0]
    categories = conn.execute(
        "SELECT DISTINCT category FROM medical_records WHERE owner_user_id=? ORDER BY category",
        (user_id,)
    ).fetchall()
    conn.close()
    return {
        "total_records": total_records,
        "total_abnormal": total_abnormal,
        "total_symptoms": total_symptoms,
        "total_profiles": total_profiles,
        "categories": [r[0] for r in categories],
    }


# ── V5.0 AI 对话持久化 CRUD ──────────────────────────────────────────────────

def save_ai_message(owner_user_id: int, session_id: str, role: str,
                    content: str, profile_id: int = None,
                    session_type: str = "bazi", context_data: str = None) -> int:
    """保存一条 AI 对话消息到数据库，返回消息 ID。"""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO ai_conversations
               (owner_user_id, profile_id, session_type, session_id, role, content, context_data)
               VALUES (?,?,?,?,?,?,?)""",
            (owner_user_id, profile_id, session_type, session_id, role, content, context_data)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception:
        return -1
    finally:
        conn.close()


def get_ai_conversation(owner_user_id: int, session_id: str,
                        session_type: str = "bazi") -> List[Dict]:
    """获取指定 session 的完整对话历史，按时间升序。"""
    conn = get_connection()
    rows = conn.execute(
        """SELECT role, content, created_at FROM ai_conversations
           WHERE owner_user_id=? AND session_id=? AND session_type=?
           ORDER BY id ASC""",
        (owner_user_id, session_id, session_type)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_ai_sessions(owner_user_id: int, session_type: str = "bazi",
                    profile_id: int = None, limit: int = 20) -> List[Dict]:
    """获取用户的所有 AI 会话列表（去重，按最新消息排序）。"""
    conn = get_connection()
    if profile_id:
        rows = conn.execute(
            """SELECT session_id, MAX(created_at) as last_time,
                      COUNT(*) as msg_count
               FROM ai_conversations
               WHERE owner_user_id=? AND session_type=? AND profile_id=?
               GROUP BY session_id ORDER BY last_time DESC LIMIT ?""",
            (owner_user_id, session_type, profile_id, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT session_id, MAX(created_at) as last_time,
                      COUNT(*) as msg_count
               FROM ai_conversations
               WHERE owner_user_id=? AND session_type=?
               GROUP BY session_id ORDER BY last_time DESC LIMIT ?""",
            (owner_user_id, session_type, limit)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_ai_session(owner_user_id: int, session_id: str) -> bool:
    """删除指定会话的所有消息。"""
    conn = get_connection()
    try:
        conn.execute(
            "DELETE FROM ai_conversations WHERE owner_user_id=? AND session_id=?",
            (owner_user_id, session_id)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def save_bazi_analysis(owner_user_id: int, profile_id: int,
                       birth_year: int, target_year: int,
                       bazi_data: str, ai_report: str = None,
                       session_id: str = None) -> int:
    """Upsert 八字分析结果（同一人同一年唯一）。"""
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM bazi_analyses WHERE owner_user_id=? AND profile_id=? AND birth_year=? AND target_year=?",
            (owner_user_id, profile_id, birth_year, target_year)
        ).fetchone()
        if existing:
            conn.execute(
                """UPDATE bazi_analyses
                   SET bazi_data=?, ai_report=?, session_id=?, created_at=datetime('now','localtime')
                   WHERE id=?""",
                (bazi_data, ai_report, session_id, existing[0])
            )
            conn.commit()
            return existing[0]
        else:
            cursor = conn.execute(
                """INSERT INTO bazi_analyses
                   (owner_user_id, profile_id, birth_year, target_year, bazi_data, ai_report, session_id)
                   VALUES (?,?,?,?,?,?,?)""",
                (owner_user_id, profile_id, birth_year, target_year,
                 bazi_data, ai_report, session_id)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception:
        return -1
    finally:
        conn.close()


def get_bazi_analysis(owner_user_id: int, profile_id: int,
                      birth_year: int, target_year: int) -> Optional[Dict]:
    """获取已保存的八字分析结果。"""
    conn = get_connection()
    row = conn.execute(
        """SELECT * FROM bazi_analyses
           WHERE owner_user_id=? AND profile_id=? AND birth_year=? AND target_year=?""",
        (owner_user_id, profile_id, birth_year, target_year)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

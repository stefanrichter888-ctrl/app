"""
记忆库数据库模块
三层记忆：CORE（身份）/ WARM（近期重要）/ ARCHIVE（碎片库）
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "memory.db"
CONFIG_PATH = "config.json"


def load_config():
    """读取配置文件，拿到所有可调数值"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库，建表（如果还没建过）"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS core_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS warm_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            episode_tag TEXT,
            entity_tags TEXT,
            free_tag TEXT,
            created_at TEXT NOT NULL,
            last_accessed_at TEXT NOT NULL,
            access_count INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS archive_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            episode_tag TEXT,
            entity_tags TEXT,
            free_tag TEXT,
            created_at TEXT NOT NULL,
            last_accessed_at TEXT,
            access_count INTEGER DEFAULT 0,
            temperature REAL DEFAULT 1.0
        )
    """)

    conn.commit()
    conn.close()


def now():
    """当前时间戳字符串"""
    return datetime.now().isoformat()
  # ══════════════════════════════════════
# 第一层：CORE 核心记忆
# ══════════════════════════════════════

def get_core_memory():
    """获取核心记忆内容"""
    conn = get_connection()
    row = conn.execute("SELECT content FROM core_memory ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return row["content"] if row else ""


def set_core_memory(content):
    """设置/更新核心记忆"""
    config = load_config()
    hard_stop = config["core_memory"]["hard_stop_chars"]

    if len(content) > hard_stop:
        content = content[:hard_stop]

    conn = get_connection()
    existing = conn.execute("SELECT id FROM core_memory ORDER BY id DESC LIMIT 1").fetchone()

    if existing:
        conn.execute(
            "UPDATE core_memory SET content = ?, updated_at = ? WHERE id = ?",
            (content, now(), existing["id"])
        )
    else:
        conn.execute(
            "INSERT INTO core_memory (content, created_at, updated_at) VALUES (?, ?, ?)",
            (content, now(), now())
        )
    conn.commit()
    conn.close()


# ══════════════════════════════════════
# 第二层：WARM 近期重要记忆
# ══════════════════════════════════════

def add_warm_memory(content, episode_tag=None, entity_tags=None, free_tag=None):
    """新增一条第二层记忆"""
    entity_tags_json = json.dumps(entity_tags or [], ensure_ascii=False)
    conn = get_connection()
    conn.execute(
        """INSERT INTO warm_memory
           (content, episode_tag, entity_tags, free_tag, created_at, last_accessed_at, access_count)
           VALUES (?, ?, ?, ?, ?, ?, 0)""",
        (content, episode_tag, entity_tags_json, free_tag, now(), now())
    )
    conn.commit()
    conn.close()


def get_all_warm_memories():
    """获取所有第二层记忆"""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM warm_memory ORDER BY last_accessed_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def touch_warm_memory(memory_id):
    """记忆被调用时：更新最后访问时间，使用次数+1"""
    conn = get_connection()
    conn.execute(
        "UPDATE warm_memory SET last_accessed_at = ?, access_count = access_count + 1 WHERE id = ?",
        (now(), memory_id)
    )
    conn.commit()
    conn.close()


def delete_warm_memory(memory_id):
    """删除一条第二层记忆"""
    conn = get_connection()
    conn.execute("DELETE FROM warm_memory WHERE id = ?", (memory_id,))
    conn.commit()
    conn.close()


# ══════════════════════════════════════
# 第三层：ARCHIVE 碎片记忆库
# ══════════════════════════════════════

def add_archive_memory(content, episode_tag=None, entity_tags=None, free_tag=None, start_temp=None):
    """新增一条第三层记忆"""
    config = load_config()
    if start_temp is None:
        start_temp = config["archive_memory"]["start_temperature"]

    entity_tags_json = json.dumps(entity_tags or [], ensure_ascii=False)
    conn = get_connection()
    conn.execute(
        """INSERT INTO archive_memory
           (content, episode_tag, entity_tags, free_tag, created_at, last_accessed_at, access_count, temperature)
           VALUES (?, ?, ?, ?, ?, ?, 0, ?)""",
        (content, episode_tag, entity_tags_json, free_tag, now(), now(), start_temp)
    )
    conn.commit()
    conn.close()


def get_all_archive_memories():
    """获取所有第三层记忆"""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM archive_memory ORDER BY temperature DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_archive_memory(memory_id):
    """彻底删除一条第三层记忆"""
    conn = get_connection()
    conn.execute("DELETE FROM archive_memory WHERE id = ?", (memory_id,))
    conn.commit()
    conn.close()


def move_warm_to_archive(memory_id):
    """将一条第二层记忆移动到第三层"""
    conn = get_connection()
    row = conn.execute("SELECT * FROM warm_memory WHERE id = ?", (memory_id,)).fetchone()
    if row:
        config = load_config()
        start_temp = config["archive_memory"]["start_temperature"]

        conn.execute(
            """INSERT INTO archive_memory
               (content, episode_tag, entity_tags, free_tag, created_at, last_accessed_at, access_count, temperature)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (row["content"], row["episode_tag"], row["entity_tags"], row["free_tag"],
             row["created_at"], row["last_accessed_at"], row["access_count"], start_temp)
        )
        conn.execute("DELETE FROM warm_memory WHERE id = ?", (memory_id,))
        conn.commit()
    conn.close()


if not os.path.exists(DB_PATH):
    init_db()
else:
    init_db()

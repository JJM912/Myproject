"""
db.py — SQLite 기반 공유 데이터 관리
여러 학생이 동시에 접속해도 데이터 충돌 없이 저장/취합됩니다.
"""
import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db")


@contextmanager
def get_conn():
    """스레드 안전한 DB 연결 컨텍스트 매니저."""
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """앱 시작 시 한 번 호출 — 테이블을 생성합니다."""
    with get_conn() as conn:
        c = conn.cursor()

        # ── Flip & Recall ──────────────────────────────────────────────
        # 교사가 등록한 단어 세트
        c.execute("""
            CREATE TABLE IF NOT EXISTS flip_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                meaning TEXT NOT NULL,
                example TEXT DEFAULT ''
            )
        """)
        # 수업 진행 상태 (현재 카드 인덱스, 진행 여부 등) — key/value
        c.execute("""
            CREATE TABLE IF NOT EXISTS flip_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        # 학생 자기평가 결과
        c.execute("""
            CREATE TABLE IF NOT EXISTS flip_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student TEXT NOT NULL,
                word_id INTEGER NOT NULL,
                rating TEXT NOT NULL,        -- 'known' / 'unsure' / 'unknown'
                UNIQUE(student, word_id)
            )
        """)

        # ── Text Spotlight ─────────────────────────────────────────────
        # 교사가 등록한 지문 (문장 단위로 저장)
        c.execute("""
            CREATE TABLE IF NOT EXISTS ts_sentences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idx INTEGER NOT NULL,
                text TEXT NOT NULL
            )
        """)
        # 날개 문제
        c.execute("""
            CREATE TABLE IF NOT EXISTS ts_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idx INTEGER NOT NULL,
                text TEXT NOT NULL
            )
        """)
        # 학생 태그
        c.execute("""
            CREATE TABLE IF NOT EXISTS ts_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student TEXT NOT NULL,
                sentence_idx INTEGER NOT NULL,
                tag TEXT NOT NULL,
                UNIQUE(student, sentence_idx, tag)
            )
        """)
        # 학생 메모
        c.execute("""
            CREATE TABLE IF NOT EXISTS ts_memos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student TEXT NOT NULL,
                sentence_idx INTEGER NOT NULL,
                memo TEXT NOT NULL,
                UNIQUE(student, sentence_idx)
            )
        """)
        # 제출 완료한 학생
        c.execute("""
            CREATE TABLE IF NOT EXISTS ts_submitted (
                student TEXT PRIMARY KEY
            )
        """)
        # 상태 (결과 공개 여부 등)
        c.execute("""
            CREATE TABLE IF NOT EXISTS ts_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)


# ══════════════════════════════════════════════════════════════════════
# 상태 관리 헬퍼 (key/value)
# ══════════════════════════════════════════════════════════════════════
def set_state(table, key, value):
    with get_conn() as conn:
        conn.execute(
            f"INSERT INTO {table} (key, value) VALUES (?, ?) "
            f"ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value)),
        )


def get_state(table, key, default=None):
    with get_conn() as conn:
        row = conn.execute(
            f"SELECT value FROM {table} WHERE key=?", (key,)
        ).fetchone()
        return row["value"] if row else default


# ══════════════════════════════════════════════════════════════════════
# Flip & Recall 함수
# ══════════════════════════════════════════════════════════════════════
def flip_add_word(word, meaning, example=""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO flip_words (word, meaning, example) VALUES (?, ?, ?)",
            (word, meaning, example),
        )


def flip_get_words():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM flip_words ORDER BY id").fetchall()
        return [dict(r) for r in rows]


def flip_delete_word(word_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM flip_words WHERE id=?", (word_id,))
        conn.execute("DELETE FROM flip_responses WHERE word_id=?", (word_id,))


def flip_clear_words():
    with get_conn() as conn:
        conn.execute("DELETE FROM flip_words")
        conn.execute("DELETE FROM flip_responses")


def flip_save_response(student, word_id, rating):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO flip_responses (student, word_id, rating) VALUES (?, ?, ?) "
            "ON CONFLICT(student, word_id) DO UPDATE SET rating=excluded.rating",
            (student, word_id, rating),
        )


def flip_get_responses(word_id=None):
    with get_conn() as conn:
        if word_id is not None:
            rows = conn.execute(
                "SELECT * FROM flip_responses WHERE word_id=?", (word_id,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM flip_responses").fetchall()
        return [dict(r) for r in rows]


def flip_clear_responses():
    with get_conn() as conn:
        conn.execute("DELETE FROM flip_responses")


# ══════════════════════════════════════════════════════════════════════
# Text Spotlight 함수
# ══════════════════════════════════════════════════════════════════════
def ts_set_text(sentences):
    """지문 등록 — 기존 데이터를 모두 초기화하고 새로 저장."""
    with get_conn() as conn:
        conn.execute("DELETE FROM ts_sentences")
        conn.execute("DELETE FROM ts_tags")
        conn.execute("DELETE FROM ts_memos")
        conn.execute("DELETE FROM ts_submitted")
        for i, s in enumerate(sentences):
            conn.execute(
                "INSERT INTO ts_sentences (idx, text) VALUES (?, ?)", (i, s)
            )


def ts_get_sentences():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM ts_sentences ORDER BY idx"
        ).fetchall()
        return [dict(r) for r in rows]


def ts_set_questions(questions):
    with get_conn() as conn:
        conn.execute("DELETE FROM ts_questions")
        for i, q in enumerate(questions):
            conn.execute(
                "INSERT INTO ts_questions (idx, text) VALUES (?, ?)", (i, q)
            )


def ts_get_questions():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM ts_questions ORDER BY idx"
        ).fetchall()
        return [dict(r) for r in rows]


def ts_save_tags(student, sentence_idx, tags):
    """한 문장에 대한 학생의 태그를 갱신 (기존 삭제 후 재삽입)."""
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM ts_tags WHERE student=? AND sentence_idx=?",
            (student, sentence_idx),
        )
        for tag in tags:
            conn.execute(
                "INSERT OR IGNORE INTO ts_tags (student, sentence_idx, tag) "
                "VALUES (?, ?, ?)",
                (student, sentence_idx, tag),
            )


def ts_get_student_tags(student, sentence_idx):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT tag FROM ts_tags WHERE student=? AND sentence_idx=?",
            (student, sentence_idx),
        ).fetchall()
        return [r["tag"] for r in rows]


def ts_save_memo(student, sentence_idx, memo):
    with get_conn() as conn:
        if memo.strip():
            conn.execute(
                "INSERT INTO ts_memos (student, sentence_idx, memo) VALUES (?, ?, ?) "
                "ON CONFLICT(student, sentence_idx) DO UPDATE SET memo=excluded.memo",
                (student, sentence_idx, memo.strip()),
            )
        else:
            conn.execute(
                "DELETE FROM ts_memos WHERE student=? AND sentence_idx=?",
                (student, sentence_idx),
            )


def ts_get_student_memo(student, sentence_idx):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT memo FROM ts_memos WHERE student=? AND sentence_idx=?",
            (student, sentence_idx),
        ).fetchone()
        return row["memo"] if row else ""


def ts_get_all_tags():
    """전체 태그 — 히트맵 집계용."""
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM ts_tags").fetchall()
        return [dict(r) for r in rows]


def ts_get_all_memos():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM ts_memos ORDER BY sentence_idx").fetchall()
        return [dict(r) for r in rows]


def ts_mark_submitted(student):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO ts_submitted (student) VALUES (?)", (student,)
        )


def ts_is_submitted(student):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT student FROM ts_submitted WHERE student=?", (student,)
        ).fetchone()
        return row is not None


def ts_get_submitted_list():
    with get_conn() as conn:
        rows = conn.execute("SELECT student FROM ts_submitted").fetchall()
        return [r["student"] for r in rows]


def ts_get_participants():
    """태그나 메모를 남긴 전체 학생 목록."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT student FROM ts_tags "
            "UNION SELECT DISTINCT student FROM ts_memos"
        ).fetchall()
        return [r["student"] for r in rows]


def ts_reset_all():
    """전체 초기화 (지문은 유지, 학생 데이터만 삭제)."""
    with get_conn() as conn:
        conn.execute("DELETE FROM ts_tags")
        conn.execute("DELETE FROM ts_memos")
        conn.execute("DELETE FROM ts_submitted")

"""
db.py — SQLite 기반 공유 데이터 관리

기능
1. Word
   - 교사 단어 등록
   - 학생 I Know It / Save to My Words 응답 저장
   - 학번별 My Words 저장

2. Reading
   - 지문과 날개 문제 저장
   - 학생 태그와 메모 저장
   - 교사 공개 여부 저장
"""

import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        c = conn.cursor()

        # 앱 전체 상태
        c.execute("""
            CREATE TABLE IF NOT EXISTS app_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # Word 단어
        c.execute("""
            CREATE TABLE IF NOT EXISTS flip_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                meaning TEXT NOT NULL,
                example TEXT DEFAULT ''
            )
        """)

        # Word 진행 상태
        c.execute("""
            CREATE TABLE IF NOT EXISTS flip_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # Word 학생 응답
        # 기존 Claude 코드와 호환되도록 컬럼명을 rating으로 유지
        # 값은 know / save 사용
        c.execute("""
            CREATE TABLE IF NOT EXISTS flip_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student TEXT NOT NULL,
                word_id INTEGER NOT NULL,
                rating TEXT NOT NULL,
                UNIQUE(student, word_id)
            )
        """)

        # 학번별 개인 단어장
        c.execute("""
            CREATE TABLE IF NOT EXISTS my_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student TEXT NOT NULL,
                word_id INTEGER,
                word TEXT NOT NULL,
                meaning TEXT NOT NULL,
                example TEXT DEFAULT '',
                UNIQUE(student, word)
            )
        """)

        # Reading 지문 문장
        c.execute("""
            CREATE TABLE IF NOT EXISTS ts_sentences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idx INTEGER NOT NULL,
                text TEXT NOT NULL
            )
        """)

        # Reading 날개 문제
        c.execute("""
            CREATE TABLE IF NOT EXISTS ts_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idx INTEGER NOT NULL,
                text TEXT NOT NULL
            )
        """)

        # Reading 태그
        c.execute("""
            CREATE TABLE IF NOT EXISTS ts_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student TEXT NOT NULL,
                sentence_idx INTEGER NOT NULL,
                tag TEXT NOT NULL,
                UNIQUE(student, sentence_idx, tag)
            )
        """)

        # Reading 메모
        c.execute("""
            CREATE TABLE IF NOT EXISTS ts_memos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student TEXT NOT NULL,
                sentence_idx INTEGER NOT NULL,
                memo TEXT NOT NULL,
                UNIQUE(student, sentence_idx)
            )
        """)

        # Reading 제출 완료 학생
        c.execute("""
            CREATE TABLE IF NOT EXISTS ts_submitted (
                student TEXT PRIMARY KEY
            )
        """)

        # Reading 공개 여부
        c.execute("""
            CREATE TABLE IF NOT EXISTS ts_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)


# -----------------------------
# 상태 관리
# -----------------------------
def set_state(table, key, value):
    with get_conn() as conn:
        conn.execute(
            f"""
            INSERT INTO {table} (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """,
            (key, str(value)),
        )


def get_state(table, key, default=None):
    with get_conn() as conn:
        row = conn.execute(
            f"SELECT value FROM {table} WHERE key=?",
            (key,)
        ).fetchone()
        return row["value"] if row else default


def set_app_state(key, value):
    set_state("app_state", key, value)


def get_app_state(key, default=None):
    return get_state("app_state", key, default)


# -----------------------------
# Word: Flip & Recall
# -----------------------------
def flip_add_word(word, meaning, example=""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO flip_words (word, meaning, example) VALUES (?, ?, ?)",
            (word, meaning, example),
        )


def flip_get_words():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM flip_words ORDER BY id"
        ).fetchall()
        return [dict(r) for r in rows]


def flip_delete_word(word_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM flip_words WHERE id=?", (word_id,))
        conn.execute("DELETE FROM flip_responses WHERE word_id=?", (word_id,))
        conn.execute("DELETE FROM my_words WHERE word_id=?", (word_id,))


def flip_clear_words():
    with get_conn() as conn:
        conn.execute("DELETE FROM flip_words")
        conn.execute("DELETE FROM flip_responses")
        conn.execute("DELETE FROM my_words")


def flip_save_response(student, word_id, response):
    """
    response 값:
    - know
    - save
    """
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO flip_responses (student, word_id, rating)
            VALUES (?, ?, ?)
            ON CONFLICT(student, word_id)
            DO UPDATE SET rating=excluded.rating
            """,
            (student, word_id, response),
        )


def flip_get_responses(word_id=None):
    with get_conn() as conn:
        if word_id is None:
            rows = conn.execute(
                "SELECT * FROM flip_responses"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM flip_responses WHERE word_id=?",
                (word_id,),
            ).fetchall()

        results = []

        for row in rows:
            item = dict(row)

            # 기존 값 known / unsure / unknown이 남아 있어도 새 구조에 맞게 변환
            old_value = item.get("rating", "")

            if old_value == "known":
                new_value = "know"
            elif old_value in ["unsure", "unknown"]:
                new_value = "save"
            else:
                new_value = old_value

            item["response"] = new_value
            results.append(item)

        return results


def flip_clear_responses():
    with get_conn() as conn:
        conn.execute("DELETE FROM flip_responses")


def my_words_add(student, word_id, word, meaning, example=""):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO my_words
            (student, word_id, word, meaning, example)
            VALUES (?, ?, ?, ?, ?)
            """,
            (student, word_id, word, meaning, example),
        )


def my_words_get(student):
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM my_words
            WHERE student=?
            ORDER BY id DESC
            """,
            (student,),
        ).fetchall()
        return [dict(r) for r in rows]


def my_words_delete(item_id, student):
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM my_words WHERE id=? AND student=?",
            (item_id, student),
        )


# -----------------------------
# Reading: Text Spotlight
# -----------------------------
def ts_set_text(sentences):
    with get_conn() as conn:
        conn.execute("DELETE FROM ts_sentences")
        conn.execute("DELETE FROM ts_tags")
        conn.execute("DELETE FROM ts_memos")
        conn.execute("DELETE FROM ts_submitted")

        for i, sentence in enumerate(sentences):
            conn.execute(
                "INSERT INTO ts_sentences (idx, text) VALUES (?, ?)",
                (i, sentence),
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

        for i, question in enumerate(questions):
            conn.execute(
                "INSERT INTO ts_questions (idx, text) VALUES (?, ?)",
                (i, question),
            )


def ts_get_questions():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM ts_questions ORDER BY idx"
        ).fetchall()
        return [dict(r) for r in rows]


def ts_save_tags(student, sentence_idx, tags):
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM ts_tags WHERE student=? AND sentence_idx=?",
            (student, sentence_idx),
        )

        for tag in tags:
            conn.execute(
                """
                INSERT OR IGNORE INTO ts_tags
                (student, sentence_idx, tag)
                VALUES (?, ?, ?)
                """,
                (student, sentence_idx, tag),
            )


def ts_get_student_tags(student, sentence_idx):
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT tag FROM ts_tags
            WHERE student=? AND sentence_idx=?
            """,
            (student, sentence_idx),
        ).fetchall()
        return [r["tag"] for r in rows]


def ts_save_memo(student, sentence_idx, memo):
    memo = memo.strip()

    with get_conn() as conn:
        if memo:
            conn.execute(
                """
                INSERT INTO ts_memos (student, sentence_idx, memo)
                VALUES (?, ?, ?)
                ON CONFLICT(student, sentence_idx)
                DO UPDATE SET memo=excluded.memo
                """,
                (student, sentence_idx, memo),
            )
        else:
            conn.execute(
                "DELETE FROM ts_memos WHERE student=? AND sentence_idx=?",
                (student, sentence_idx),
            )


def ts_get_student_memo(student, sentence_idx):
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT memo FROM ts_memos
            WHERE student=? AND sentence_idx=?
            """,
            (student, sentence_idx),
        ).fetchone()
        return row["memo"] if row else ""


def ts_get_all_tags():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM ts_tags"
        ).fetchall()
        return [dict(r) for r in rows]


def ts_get_all_memos():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM ts_memos ORDER BY sentence_idx"
        ).fetchall()
        return [dict(r) for r in rows]


def ts_mark_submitted(student):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO ts_submitted (student) VALUES (?)",
            (student,),
        )


def ts_is_submitted(student):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT student FROM ts_submitted WHERE student=?",
            (student,),
        ).fetchone()
        return row is not None


def ts_get_submitted_list():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT student FROM ts_submitted ORDER BY student"
        ).fetchall()
        return [r["student"] for r in rows]


def ts_get_participants():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT student FROM ts_tags
            UNION
            SELECT DISTINCT student FROM ts_memos
            """
        ).fetchall()
        return [r["student"] for r in rows]


def ts_reset_all():
    with get_conn() as conn:
        conn.execute("DELETE FROM ts_tags")
        conn.execute("DELETE FROM ts_memos")
        conn.execute("DELETE FROM ts_submitted")

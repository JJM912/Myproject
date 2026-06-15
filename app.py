"""
app.py — Daea High School 1학년 영어 수업 (단일 파일 버전)

실행:
    pip install streamlit
    streamlit run app.py

이 파일 하나로 Overview / Word / Reading 모든 기능이 동작합니다.
사이드바에서 페이지와 역할을 선택하세요.
"""
import streamlit as st
import sqlite3
import os
import re
from contextlib import contextmanager
from collections import defaultdict

st.set_page_config(
    page_title="Daea High School · 1학년 영어",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════
# DB (SQLite 공유 데이터)
# ══════════════════════════════════════════════════════════════════════════
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


# ══════════════════════════════════════════════════════════════════════════
# WORD — Flip & Recall
# ══════════════════════════════════════════════════════════════════════════
# 자기평가 등급 정의
RATINGS = {
    "known":   {"label": "✅ 알았어",   "color": "#085041", "bg": "#E1F5EE"},
    "unsure":  {"label": "🤔 헷갈렸어", "color": "#633806", "bg": "#FAEEDA"},
    "unknown": {"label": "❌ 몰랐어",   "color": "#A32D2D", "bg": "#FCEBEB"},
}

SAMPLE_WORDS = [
    ("ambiguous", "모호한, 불분명한", "The instructions were ambiguous and confusing."),
    ("inevitable", "불가피한", "Change is inevitable as time goes by."),
    ("persevere", "인내하며 계속하다", "She persevered despite many failures."),
    ("contemplate", "심사숙고하다", "He contemplated his future quietly."),
    ("eloquent", "웅변의, 설득력 있는", "Her eloquent speech moved the audience."),
]


# ══════════════════════════════════════════════════════════════════════
# 교사 화면
# ══════════════════════════════════════════════════════════════════════
def flip_teacher_view():
    st.markdown("## 👩‍🏫 Flip & Recall — 교사 화면")
    st.caption("단어를 등록하고 카드 진행을 제어하세요. 학생 자기평가가 실시간으로 집계됩니다.")

    # ── 단어 등록 ──────────────────────────────────────────────────────
    with st.expander("📝 단어 세트 등록 / 관리", expanded=True):
        with st.form("add_word", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 2, 3])
            w = c1.text_input("영단어", placeholder="ambiguous")
            m = c2.text_input("뜻", placeholder="모호한")
            e = c3.text_input("예문 (선택)", placeholder="The instructions were ambiguous.")
            if st.form_submit_button("➕ 추가") and w and m:
                flip_add_word(w.strip(), m.strip(), e.strip())
                st.rerun()

        col_a, col_b = st.columns(2)
        if col_a.button("📚 샘플 단어 5개 불러오기"):
            for w, m, e in SAMPLE_WORDS:
                flip_add_word(w, m, e)
            st.rerun()
        if col_b.button("🗑️ 전체 단어 삭제"):
            flip_clear_words()
            set_state("flip_state", "active", "false")
            st.rerun()

        words = flip_get_words()
        st.markdown(f"**등록된 단어: {len(words)}개**")
        for word in words:
            wc1, wc2, wc3, wc4 = st.columns([2, 2, 3, 1])
            wc1.markdown(f"**{word['word']}**")
            wc2.markdown(word["meaning"])
            wc3.caption(word["example"] or "—")
            if wc4.button("삭제", key=f"del_w_{word['id']}"):
                flip_delete_word(word["id"])
                st.rerun()

    if not words:
        st.info("단어를 먼저 등록해 주세요.")
        return

    st.markdown("---")

    # ── 카드 진행 제어 ─────────────────────────────────────────────────
    active = get_state("flip_state", "active", "false") == "true"
    current_idx = int(get_state("flip_state", "current_idx", "0"))
    flipped = get_state("flip_state", "flipped", "false") == "true"

    st.markdown("### 🎬 카드 진행 제어")

    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns(4)
    if ctrl1.button("▶ 시작 / 첫 카드", type="primary"):
        set_state("flip_state", "active", "true")
        set_state("flip_state", "current_idx", "0")
        set_state("flip_state", "flipped", "false")
        flip_clear_responses()
        st.rerun()

    if ctrl2.button("🔄 카드 뒤집기", disabled=not active):
        set_state("flip_state", "flipped", "true")
        st.rerun()

    if ctrl3.button("⏭ 다음 카드", disabled=not active):
        if current_idx < len(words) - 1:
            set_state("flip_state", "current_idx", str(current_idx + 1))
            set_state("flip_state", "flipped", "false")
        else:
            set_state("flip_state", "active", "false")
        st.rerun()

    if ctrl4.button("⏹ 종료"):
        set_state("flip_state", "active", "false")
        st.rerun()

    # ── 현재 카드 + 실시간 집계 ─────────────────────────────────────────
    if active and current_idx < len(words):
        word = words[current_idx]
        st.markdown("---")
        st.markdown(f"#### 현재 카드 ({current_idx + 1} / {len(words)})")

        # 카드 표시
        if flipped:
            st.markdown(f"""
            <div style="background:white; border:2px solid #085041; border-radius:14px;
                        padding:1.5rem; text-align:center;">
              <div style="font-size:2rem; font-weight:700; color:#3C3489;">{word['word']}</div>
              <div style="font-size:1.3rem; color:#085041; margin-top:10px;">{word['meaning']}</div>
              <div style="color:#888; font-style:italic; margin-top:8px;">{word['example']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:white; border:2px solid #3C3489; border-radius:14px;
                        padding:2rem; text-align:center;">
              <div style="font-size:2.5rem; font-weight:700; color:#3C3489;">{word['word']}</div>
              <div style="color:#aaa; margin-top:10px;">학생들이 뜻을 떠올리는 중...</div>
            </div>
            """, unsafe_allow_html=True)

        # 실시간 집계
        st.markdown("##### 📊 학생 자기평가 실시간 집계")
        responses = flip_get_responses(word["id"])
        counts = {"known": 0, "unsure": 0, "unknown": 0}
        for r in responses:
            counts[r["rating"]] = counts.get(r["rating"], 0) + 1
        total = sum(counts.values())

        m1, m2, m3 = st.columns(3)
        for col, key in zip([m1, m2, m3], ["known", "unsure", "unknown"]):
            info = RATINGS[key]
            pct = round(counts[key] / total * 100) if total else 0
            col.markdown(f"""
            <div style="background:{info['bg']}; border-radius:10px; padding:1rem; text-align:center;">
              <div style="font-size:1.8rem; font-weight:700; color:{info['color']};">{counts[key]}</div>
              <div style="font-size:13px; color:{info['color']};">{info['label']} ({pct}%)</div>
            </div>
            """, unsafe_allow_html=True)

        st.caption(f"총 {total}명 응답 · 🔄 새로고침하면 최신 집계가 반영됩니다.")
        if st.button("🔄 집계 새로고침"):
            st.rerun()
    elif not active:
        st.info("'시작' 버튼을 누르면 학생 화면에 첫 카드가 나타납니다.")

    # ── 수업 후 복습 목록 ──────────────────────────────────────────────
    st.markdown("---")
    with st.expander("📋 '몰랐어' 단어 집계 (개인 복습 목록 재료)"):
        all_resp = flip_get_responses()
        unknown_by_word = {}
        for r in all_resp:
            if r["rating"] == "unknown":
                unknown_by_word.setdefault(r["word_id"], []).append(r["student"])
        if unknown_by_word:
            for word in words:
                if word["id"] in unknown_by_word:
                    students = unknown_by_word[word["id"]]
                    st.markdown(
                        f"**{word['word']}** ({word['meaning']}) — "
                        f"{len(students)}명이 모름: {', '.join(students)}"
                    )
        else:
            st.caption("아직 '몰랐어' 응답이 없습니다.")


# ══════════════════════════════════════════════════════════════════════
# 학생 화면
# ══════════════════════════════════════════════════════════════════════
def flip_student_view(student_name):
    st.markdown("## 👤 Flip & Recall")
    st.caption(f"{student_name} 님 — 카드를 보고 뜻을 떠올린 뒤, 솔직하게 자기평가하세요.")

    active = get_state("flip_state", "active", "false") == "true"
    current_idx = int(get_state("flip_state", "current_idx", "0"))
    flipped = get_state("flip_state", "flipped", "false") == "true"
    words = flip_get_words()

    if not active or current_idx >= len(words):
        st.info("교사가 카드를 시작하면 여기에 나타납니다.")
        if st.button("🔄 새로고침"):
            st.rerun()
        return

    word = words[current_idx]
    st.markdown(f"#### 카드 {current_idx + 1} / {len(words)}")

    if not flipped:
        # 앞면 — 단어만
        st.markdown(f"""
        <div style="background:white; border:2px solid #3C3489; border-radius:14px;
                    padding:2.5rem; text-align:center;">
          <div style="font-size:2.8rem; font-weight:700; color:#3C3489;">{word['word']}</div>
          <div style="color:#aaa; margin-top:12px;">뜻을 머릿속으로 떠올려 보세요</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("교사가 카드를 뒤집으면 정답이 나타납니다.")
        if st.button("🔄 새로고침"):
            st.rerun()
    else:
        # 뒷면 — 뜻 공개 + 자기평가
        st.markdown(f"""
        <div style="background:white; border:2px solid #085041; border-radius:14px;
                    padding:1.5rem; text-align:center;">
          <div style="font-size:2rem; font-weight:700; color:#3C3489;">{word['word']}</div>
          <div style="font-size:1.3rem; color:#085041; margin-top:8px;">{word['meaning']}</div>
          <div style="color:#888; font-style:italic; margin-top:8px;">{word['example']}</div>
        </div>
        """, unsafe_allow_html=True)

        # 이미 응답했는지 확인
        my_resp = [r for r in flip_get_responses(word["id"]) if r["student"] == student_name]
        if my_resp:
            rating = my_resp[0]["rating"]
            info = RATINGS[rating]
            st.success(f"평가 완료: {info['label']} — 교사가 다음 카드로 넘기면 계속됩니다.")
            if st.button("🔄 새로고침"):
                st.rerun()
        else:
            st.markdown("##### 얼마나 알고 있었나요?")
            bc1, bc2, bc3 = st.columns(3)
            for col, key in zip([bc1, bc2, bc3], ["known", "unsure", "unknown"]):
                if col.button(RATINGS[key]["label"], key=f"rate_{key}", use_container_width=True):
                    flip_save_response(student_name, word["id"], key)
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# READING — Text Spotlight
# ══════════════════════════════════════════════════════════════════════════
# 태그 정의
TAGS = {
    "글의 주제":       {"color": "#633806", "bg": "#FAEEDA", "icon": "📍"},
    "날개 문제 근거":  {"color": "#085041", "bg": "#E1F5EE", "icon": "🔍"},
    "문법·구조":       {"color": "#3C3489", "bg": "#EEEDFE", "icon": "✏️"},
    "이해 안 됨":      {"color": "#A32D2D", "bg": "#FCEBEB", "icon": "❓"},
}

SAMPLE_TEXT = """When I first moved to a new school, I felt completely lost. Everyone already had their own friends, and I knew no one. During lunch, I sat alone in the corner of the cafeteria. One day, a girl named Mina came up to me and asked if I wanted to join her table. That simple act of kindness changed everything. I realized that sometimes the smallest gesture can make the biggest difference in someone's life."""

SAMPLE_QUESTIONS = [
    "Why did the writer feel lost at the new school?",
    "What lesson did the writer learn from Mina?",
]


def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


# ══════════════════════════════════════════════════════════════════════
# 교사 화면
# ══════════════════════════════════════════════════════════════════════
def ts_teacher_view():
    st.markdown("## 👩‍🏫 Text Spotlight — 교사 화면")
    st.caption("지문과 날개 문제를 등록하고, 학생 제출 현황을 확인한 뒤 히트맵을 공개하세요.")

    # ── 지문 등록 ──────────────────────────────────────────────────────
    with st.expander("📄 지문 & 날개 문제 등록", expanded=True):
        if st.button("📚 샘플 지문 불러오기"):
            st.session_state["ts_text_input"] = SAMPLE_TEXT
            st.session_state["ts_q_input"] = "\n".join(SAMPLE_QUESTIONS)
            st.rerun()

        text = st.text_area(
            "영어 지문",
            value=st.session_state.get("ts_text_input", ""),
            height=160,
            key="ts_text_input",
        )
        questions = st.text_area(
            "날개 문제 (한 줄에 하나씩)",
            value=st.session_state.get("ts_q_input", ""),
            height=90,
            key="ts_q_input",
            placeholder="Why did the writer feel lost?\nWhat lesson did the writer learn?",
        )

        if st.button("✅ 지문 등록 / 새 수업 시작", type="primary"):
            if text.strip():
                sentences = split_sentences(text)
                ts_set_text(sentences)
                q_list = [q.strip() for q in questions.split("\n") if q.strip()]
                ts_set_questions(q_list)
                set_state("ts_state", "reveal", "false")
                st.success(f"지문 등록 완료 — {len(sentences)}문장 / 날개 문제 {len(q_list)}개")
            else:
                st.warning("지문을 입력해 주세요.")

    sentences = ts_get_sentences()
    if not sentences:
        st.info("지문을 먼저 등록해 주세요.")
        return

    # ── 제출 현황 ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📋 제출 현황")
    participants = ts_get_participants()
    submitted = ts_get_submitted_list()

    c1, c2, c3 = st.columns(3)
    c1.metric("참여 학생", f"{len(participants)}명")
    c2.metric("제출 완료", f"{len(submitted)}명")
    not_submitted = set(participants) - set(submitted)
    c3.metric("작성 중", f"{len(not_submitted)}명")

    if submitted:
        st.caption(f"✅ 제출 완료: {', '.join(submitted)}")
    if not_submitted:
        st.caption(f"✍️ 작성 중: {', '.join(not_submitted)}")

    if st.button("🔄 현황 새로고침"):
        st.rerun()

    # ── 공개 제어 ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🎬 히트맵 공개 제어")
    revealed = get_state("ts_state", "reveal", "false") == "true"

    rc1, rc2 = st.columns(2)
    if rc1.button("🔓 전체 히트맵 공개", type="primary"):
        set_state("ts_state", "reveal", "true")
        st.rerun()
    if rc2.button("🔒 다시 잠금"):
        set_state("ts_state", "reveal", "false")
        st.rerun()

    status = "🔓 공개 중 — 모든 학생 화면에 히트맵 표시" if revealed else "🔒 잠금 중 — 학생은 자기 태그만 봄"
    st.info(f"현재 상태: {status}")

    if st.button("🗑️ 학생 데이터 초기화 (지문 유지)"):
        ts_reset_all()
        set_state("ts_state", "reveal", "false")
        st.rerun()

    # ── 교사용 히트맵 미리보기 (항상 표시) ──────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 히트맵 (교사 미리보기)")
    st.caption("교사는 공개 전에도 미리 볼 수 있습니다.")
    render_heatmap(show_memos=True)


# ══════════════════════════════════════════════════════════════════════
# 학생 화면
# ══════════════════════════════════════════════════════════════════════
def ts_student_view(student_name):
    st.markdown("## 👤 Text Spotlight")
    sentences = ts_get_sentences()
    if not sentences:
        st.info("교사가 지문을 등록하면 여기에 나타납니다.")
        if st.button("🔄 새로고침"):
            st.rerun()
        return

    revealed = get_state("ts_state", "reveal", "false") == "true"

    # 결과가 공개되면 모든 학생이 히트맵을 봄
    if revealed:
        st.caption("전체 결과가 공개됐습니다. 함께 보며 토론해요!")
        st.success("🔓 학급 전체 히트맵")
        render_heatmap(show_memos=True)
        if st.button("🔄 새로고침"):
            st.rerun()
        return

    # 태깅 화면
    st.caption(f"{student_name} 님 — 각 문장을 읽고 해당하는 태그를 선택하세요. (다른 학생 선택은 제출 전까지 숨겨집니다)")

    # 날개 문제 표시
    questions = ts_get_questions()
    if questions:
        with st.expander("📌 날개 문제 (근거 문장을 찾아보세요)", expanded=True):
            for i, q in enumerate(questions, 1):
                st.markdown(f"**Q{i}.** {q['text']}")

    # 태그 범례
    legend = " ".join(
        f"<span style='background:{t['bg']}; color:{t['color']}; padding:3px 10px; "
        f"border-radius:20px; font-size:12px; font-weight:600; margin-right:4px;'>"
        f"{t['icon']} {name}</span>"
        for name, t in TAGS.items()
    )
    st.markdown(legend, unsafe_allow_html=True)
    st.markdown("---")

    already_submitted = ts_is_submitted(student_name)
    if already_submitted:
        st.success("✅ 제출 완료! 교사가 히트맵을 공개하면 전체 결과를 볼 수 있습니다.")
        if st.button("🔄 새로고침"):
            st.rerun()
        return

    # 문장별 태깅
    tag_options = list(TAGS.keys())
    for sent in sentences:
        idx = sent["idx"]
        st.markdown(f"""
        <div style="background:white; border:1px solid #e9ecef; border-radius:10px;
                    padding:12px 16px; margin-bottom:4px;">
          <span style="font-size:12px; color:#888;">문장 {idx + 1}</span><br>
          <span style="font-size:15px; line-height:1.7;">{sent['text']}</span>
        </div>
        """, unsafe_allow_html=True)

        existing = ts_get_student_tags(student_name, idx)
        selected = st.multiselect(
            f"태그 (문장 {idx + 1})",
            tag_options,
            default=existing,
            key=f"tag_sel_{idx}",
            label_visibility="collapsed",
        )

        existing_memo = ts_get_student_memo(student_name, idx)
        memo = st.text_input(
            f"메모 (문장 {idx + 1})",
            value=existing_memo,
            key=f"memo_{idx}",
            placeholder="자유 메모: 공감, 궁금증, 작가 의도 추측 등...",
            label_visibility="collapsed",
        )

        if st.button("💾 이 문장 저장", key=f"save_{idx}"):
            ts_save_tags(student_name, idx, selected)
            ts_save_memo(student_name, idx, memo)
            st.toast(f"문장 {idx + 1} 저장됨")

        st.markdown("")

    st.markdown("---")
    st.warning("모든 문장 태깅이 끝나면 아래 버튼을 눌러 제출하세요. 제출 후에는 수정할 수 없습니다.")
    if st.button("📤 최종 제출", type="primary"):
        ts_mark_submitted(student_name)
        st.rerun()


# ══════════════════════════════════════════════════════════════════════
# 히트맵 렌더링 (공통)
# ══════════════════════════════════════════════════════════════════════
def render_heatmap(show_memos=False):
    sentences = ts_get_sentences()
    all_tags = ts_get_all_tags()
    all_memos = ts_get_all_memos()
    participants = ts_get_participants()
    total_students = max(len(participants), 1)

    if not all_tags and not all_memos:
        st.caption("아직 학생 태그가 없습니다.")
        return

    # 문장별 태그 집계
    from collections import defaultdict
    sent_tag_counts = defaultdict(lambda: defaultdict(int))
    for t in all_tags:
        sent_tag_counts[t["sentence_idx"]][t["tag"]] += 1

    sent_memos = defaultdict(list)
    for m in all_memos:
        sent_memos[m["sentence_idx"]].append(m)

    for sent in sentences:
        idx = sent["idx"]
        tag_counts = sent_tag_counts.get(idx, {})
        total_tags = sum(tag_counts.values())
        heat = total_tags / total_students

        # 열 강도에 따른 좌측 바 색
        if heat >= 1.0:
            bar = "#3C3489"
        elif heat >= 0.5:
            bar = "#9F9CE0"
        elif heat > 0:
            bar = "#D8D6F5"
        else:
            bar = "#eee"

        # 태그 칩
        chips = ""
        for tag_name, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            info = TAGS.get(tag_name, {"bg": "#eee", "color": "#555", "icon": ""})
            chips += (
                f"<span style='background:{info['bg']}; color:{info['color']}; "
                f"padding:2px 9px; border-radius:20px; font-size:12px; font-weight:600; "
                f"margin-right:4px;'>{info['icon']} {tag_name} {count}</span> "
            )

        # 메모
        memo_html = ""
        if show_memos and idx in sent_memos:
            memo_html = "<div style='margin-top:8px;'>"
            for m in sent_memos[idx]:
                memo_html += (
                    f"<div style='font-size:13px; color:#666; margin-top:3px;'>"
                    f"💬 <b>{m['student']}</b>: {m['memo']}</div>"
                )
            memo_html += "</div>"

        st.markdown(f"""
        <div style="background:white; border-left:4px solid {bar};
                    border-radius:0 10px 10px 0; padding:12px 16px; margin-bottom:6px;
                    border-top:1px solid #eee; border-right:1px solid #eee; border-bottom:1px solid #eee;">
          <span style="font-size:12px; color:#888;">문장 {idx + 1} · 태그 {total_tags}개</span><br>
          <span style="font-size:15px; line-height:1.7;">{sent['text']}</span>
          <div style="margin-top:8px;">{chips if chips else "<span style='color:#bbb; font-size:13px;'>태그 없음</span>"}</div>
          {memo_html}
        </div>
        """, unsafe_allow_html=True)

    # 태그 유형별 총계
    st.markdown("##### 태그 유형별 집계")
    type_total = defaultdict(int)
    for t in all_tags:
        type_total[t["tag"]] += 1
    cols = st.columns(len(TAGS))
    for col, (name, info) in zip(cols, TAGS.items()):
        col.markdown(f"""
        <div style="background:{info['bg']}; border-radius:10px; padding:10px; text-align:center;">
          <div style="font-size:1.5rem; font-weight:700; color:{info['color']};">{type_total.get(name, 0)}</div>
          <div style="font-size:12px; color:{info['color']};">{info['icon']} {name}</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# OVERVIEW 페이지
# ══════════════════════════════════════════════════════════════════════════
def render_overview():
    st.markdown("""
    <style>
    .ov-section { margin-bottom: 2.5rem; }

    /* ── 헤더 배너 ── */
    .ov-banner {
        background: linear-gradient(135deg, #1C2340 0%, #2E3A6E 60%, #3D5291 100%);
        border-radius: 18px;
        padding: 2.5rem 3rem;
        display: flex;
        align-items: center;
        gap: 2.5rem;
        margin-bottom: 2rem;
    }
    .ov-banner-text { flex: 1; }
    .ov-eyebrow {
        font-size: 12px; font-weight: 700; letter-spacing: .12em;
        color: #8FA8E8; text-transform: uppercase; margin-bottom: 8px;
    }
    .ov-h1 { font-size: 2rem; font-weight: 800; color: #fff; line-height: 1.3; margin-bottom: 10px; }
    .ov-h1 span { color: #7EB8F7; }
    .ov-lead { font-size: 14px; color: #A8BFEE; line-height: 1.75; }

    /* ── What You'll Learn 카드 ── */
    .learn-grid {
        display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 2rem;
    }
    .learn-card {
        background: white; border-radius: 14px; padding: 1.4rem 1.5rem;
        border: 1px solid #E0E8FF;
    }
    .learn-icon { font-size: 2rem; margin-bottom: 10px; }
    .learn-en { font-size: 15px; font-weight: 700; color: #1C2340; margin-bottom: 4px; }
    .learn-kr { font-size: 12px; color: #8FA8E8; font-weight: 600; margin-bottom: 8px; }
    .learn-desc { font-size: 13px; color: #5A6A8A; line-height: 1.7; }

    /* ── 앱 소개 2칸 ── */
    .app-pair { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 2rem; }
    .app-block {
        background: white; border-radius: 14px; padding: 1.5rem 1.75rem;
        border: 1px solid #E0E8FF;
    }
    .app-block-header {
        display: flex; align-items: center; gap: 12px; margin-bottom: 14px;
        padding-bottom: 12px; border-bottom: 1px solid #E0E8FF;
    }
    .app-block-icon {
        width: 42px; height: 42px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0;
    }
    .app-block-title { font-size: 16px; font-weight: 700; color: #1C2340; margin: 0; }
    .app-block-sub { font-size: 12px; color: #8FA8E8; margin: 2px 0 0; }
    .step-list { list-style: none; padding: 0; margin: 0; }
    .step-list li {
        display: flex; gap: 10px; align-items: flex-start;
        font-size: 13px; color: #5A6A8A; line-height: 1.6; margin-bottom: 8px;
    }
    .step-dot {
        width: 20px; height: 20px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 10px; font-weight: 700; flex-shrink: 0; margin-top: 1px;
    }
    .chip {
        display: inline-block; font-size: 11px; font-weight: 700;
        padding: 2px 9px; border-radius: 20px; margin: 2px 2px 0 0;
    }

    /* ── How It Works 타임라인 ── */
    .timeline {
        background: white; border-radius: 14px; padding: 1.5rem 1.75rem;
        border: 1px solid #E0E8FF; margin-bottom: 2rem;
    }
    .tl-title {
        font-size: 13px; font-weight: 700; color: #8FA8E8;
        text-transform: uppercase; letter-spacing: .08em; margin-bottom: 16px;
    }
    .tl-row {
        display: flex; align-items: flex-start; gap: 14px; margin-bottom: 14px;
    }
    .tl-badge {
        width: 36px; height: 36px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 13px; font-weight: 700; flex-shrink: 0;
    }
    .tl-body { flex: 1; }
    .tl-name { font-size: 14px; font-weight: 700; color: #1C2340; margin-bottom: 2px; }
    .tl-desc { font-size: 13px; color: #5A6A8A; line-height: 1.6; }
    .tl-line {
        width: 2px; height: 14px; background: #E0E8FF;
        margin: 0 17px 0 17px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── 헤더 배너 ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="ov-banner">
      <div class="ov-banner-text">
        <div class="ov-eyebrow">Daea High School · Grade 1 English</div>
        <div class="ov-h1">Learn Words.<br><span>Read Deeper.</span><br>Think Together.</div>
        <div class="ov-lead">
          An interactive English class platform for building vocabulary,<br>
          analyzing texts, and discussing ideas as a class.
        </div>
      </div>
      <!-- SVG 일러스트: 전구 + 책 + 말풍선 -->
      <svg width="220" height="180" viewBox="0 0 220 180" fill="none" xmlns="http://www.w3.org/2000/svg">
        <!-- 배경 원 -->
        <circle cx="110" cy="90" r="80" fill="#2E3A6E" opacity="0.5"/>
        <!-- 책 (펼쳐진) -->
        <rect x="40" y="90" width="62" height="48" rx="5" fill="white" opacity="0.92"/>
        <rect x="40" y="90" width="62" height="48" rx="5" fill="none" stroke="#7EB8F7" stroke-width="1.5"/>
        <line x1="71" y1="92" x2="71" y2="136" stroke="#C8CFEE" stroke-width="1.5"/>
        <line x1="47" y1="102" x2="69" y2="102" stroke="#E0E8FF" stroke-width="1"/>
        <line x1="47" y1="110" x2="69" y2="110" stroke="#E0E8FF" stroke-width="1"/>
        <line x1="47" y1="118" x2="69" y2="118" stroke="#E0E8FF" stroke-width="1"/>
        <line x1="47" y1="126" x2="69" y2="126" stroke="#E0E8FF" stroke-width="1"/>
        <line x1="73" y1="102" x2="95" y2="102" stroke="#E0E8FF" stroke-width="1"/>
        <line x1="73" y1="110" x2="95" y2="110" stroke="#E0E8FF" stroke-width="1"/>
        <line x1="73" y1="118" x2="95" y2="118" stroke="#E0E8FF" stroke-width="1"/>
        <!-- 전구 (단어 아이디어) -->
        <circle cx="155" cy="62" r="22" fill="#FFD166" opacity="0.9"/>
        <rect x="149" y="82" width="12" height="6" rx="2" fill="#E8B84B"/>
        <rect x="151" y="88" width="8" height="4" rx="2" fill="#D4A43A"/>
        <line x1="155" y1="35" x2="155" y2="28" stroke="#FFD166" stroke-width="2.5" stroke-linecap="round"/>
        <line x1="175" y1="42" x2="181" y2="36" stroke="#FFD166" stroke-width="2.5" stroke-linecap="round"/>
        <line x1="135" y1="42" x2="129" y2="36" stroke="#FFD166" stroke-width="2.5" stroke-linecap="round"/>
        <line x1="182" y1="62" x2="189" y2="62" stroke="#FFD166" stroke-width="2.5" stroke-linecap="round"/>
        <line x1="128" y1="62" x2="121" y2="62" stroke="#FFD166" stroke-width="2.5" stroke-linecap="round"/>
        <!-- 전구 안 W 글자 -->
        <text x="148" y="67" font-size="14" font-weight="800" fill="#1C2340">W</text>
        <!-- 말풍선 (토론) -->
        <rect x="110" y="112" width="72" height="34" rx="10" fill="#5BC8AF" opacity="0.9"/>
        <polygon points="118,146 110,158 130,146" fill="#5BC8AF" opacity="0.9"/>
        <line x1="120" y1="124" x2="172" y2="124" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.7"/>
        <line x1="120" y1="133" x2="165" y2="133" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.7"/>
        <!-- 별 장식 -->
        <text x="30" y="70" font-size="14" fill="#FFD166" opacity="0.7">✦</text>
        <text x="188" y="115" font-size="10" fill="#7EB8F7" opacity="0.7">✦</text>
        <text x="50" y="160" font-size="8" fill="#5BC8AF" opacity="0.6">★</text>
      </svg>
    </div>
    """, unsafe_allow_html=True)

    # ── What You'll Learn ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="learn-grid">

      <div class="learn-card">
        <div class="learn-icon">📖</div>
        <div class="learn-en">Vocabulary</div>
        <div class="learn-kr">어휘 학습</div>
        <div class="learn-desc">
          Flashcard-style word cards help you recall meanings actively.
          You rate your own confidence — <em>knew it / unsure / didn't know</em> —
          so revision focuses exactly where you need it.
        </div>
      </div>

      <div class="learn-card">
        <div class="learn-icon">🔍</div>
        <div class="learn-en">Reading Comprehension</div>
        <div class="learn-kr">독해 능력</div>
        <div class="learn-desc">
          Tag each sentence in a textbook passage as you read:
          identify the main idea, find evidence for questions,
          and flag grammar points or anything confusing.
        </div>
      </div>

      <div class="learn-card">
        <div class="learn-icon">💬</div>
        <div class="learn-en">Critical Discussion</div>
        <div class="learn-kr">비판적 사고 & 토론</div>
        <div class="learn-desc">
          After everyone submits, a live heatmap reveals where classmates
          agreed or differed. Use it as the starting point for
          a teacher-led discussion on the text.
        </div>
      </div>

    </div>
    """, unsafe_allow_html=True)

    # ── 앱 소개 두 칸 ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="app-pair">

      <!-- Word -->
      <div class="app-block">
        <div class="app-block-header">
          <div class="app-block-icon" style="background:#EEEDFE;">🗂</div>
          <div>
            <div class="app-block-title">Word — Flip & Recall</div>
            <div class="app-block-sub">Vocabulary · Self-Assessment · Real-time Feedback</div>
          </div>
        </div>
        <ul class="step-list">
          <li>
            <div class="step-dot" style="background:#EEEDFE; color:#3C3489;">1</div>
            <span>The teacher displays a word card on screen.</span>
          </li>
          <li>
            <div class="step-dot" style="background:#EEEDFE; color:#3C3489;">2</div>
            <span>Students silently recall the meaning during a 5-second <em>Think Time</em>.</span>
          </li>
          <li>
            <div class="step-dot" style="background:#EEEDFE; color:#3C3489;">3</div>
            <span>The card flips to reveal the meaning and example sentence.</span>
          </li>
          <li>
            <div class="step-dot" style="background:#EEEDFE; color:#3C3489;">4</div>
            <span>Each student rates privately — ✅ Knew it / 🤔 Unsure / ❌ Didn't know.</span>
          </li>
          <li>
            <div class="step-dot" style="background:#EEEDFE; color:#3C3489;">5</div>
            <span>The teacher sees live results and decides whether to explain more or move on.</span>
          </li>
        </ul>
        <div style="margin-top:12px;">
          <span class="chip" style="background:#EEEDFE; color:#3C3489;">Self-rating</span>
          <span class="chip" style="background:#E1F5EE; color:#085041;">Live tally</span>
          <span class="chip" style="background:#FAEEDA; color:#633806;">Auto review list</span>
        </div>
      </div>

      <!-- Reading -->
      <div class="app-block">
        <div class="app-block-header">
          <div class="app-block-icon" style="background:#E1F5EE;">📖</div>
          <div>
            <div class="app-block-title">Reading — Text Spotlight</div>
            <div class="app-block-sub">Tagging · Heatmap · Class Discussion</div>
          </div>
        </div>
        <ul class="step-list">
          <li>
            <div class="step-dot" style="background:#E1F5EE; color:#085041;">1</div>
            <span>The teacher uploads a textbook passage and side-note questions.</span>
          </li>
          <li>
            <div class="step-dot" style="background:#E1F5EE; color:#085041;">2</div>
            <span>Students read independently and tag each sentence using 4 categories.</span>
          </li>
          <li>
            <div class="step-dot" style="background:#E1F5EE; color:#085041;">3</div>
            <span>Tags are hidden during reading — no one influences anyone else.</span>
          </li>
          <li>
            <div class="step-dot" style="background:#E1F5EE; color:#085041;">4</div>
            <span>After everyone submits, the teacher reveals the heatmap to the whole class.</span>
          </li>
          <li>
            <div class="step-dot" style="background:#E1F5EE; color:#085041;">5</div>
            <span>Discussion flows naturally from the sentences everyone flagged most.</span>
          </li>
        </ul>
        <div style="margin-top:12px;">
          <span class="chip" style="background:#FAEEDA; color:#633806;">📍 Main idea</span>
          <span class="chip" style="background:#E1F5EE; color:#085041;">🔍 Evidence</span>
          <span class="chip" style="background:#EEEDFE; color:#3C3489;">✏️ Grammar</span>
          <span class="chip" style="background:#FCEBEB; color:#A32D2D;">❓ Confusing</span>
        </div>
      </div>

    </div>
    """, unsafe_allow_html=True)

    # ── How It Works 타임라인 ────────────────────────────────────────────────────
    st.markdown("""
    <div class="timeline">
      <div class="tl-title">How a Lesson Works</div>

      <div class="tl-row">
        <div class="tl-badge" style="background:#EEEDFE; color:#3C3489;">1</div>
        <div class="tl-body">
          <div class="tl-name">🗂 Warm-up · Word Cards <span style="font-size:12px; color:#8FA8E8; font-weight:400;">~10 min</span></div>
          <div class="tl-desc">The teacher runs through 10–15 key vocabulary cards before reading. Students self-assess each word.</div>
        </div>
      </div>
      <div class="tl-line"></div>

      <div class="tl-row">
        <div class="tl-badge" style="background:#E1F5EE; color:#085041;">2</div>
        <div class="tl-body">
          <div class="tl-name">📖 Individual Reading & Tagging <span style="font-size:12px; color:#8FA8E8; font-weight:400;">~10 min</span></div>
          <div class="tl-desc">Students read the textbook passage on their device and tag sentences independently. Notes are private until submission.</div>
        </div>
      </div>
      <div class="tl-line"></div>

      <div class="tl-row">
        <div class="tl-badge" style="background:#FAEEDA; color:#633806;">3</div>
        <div class="tl-body">
          <div class="tl-name">📊 Heatmap Reveal</div>
          <div class="tl-desc">The teacher publishes results. Every student's screen shows the same heatmap — which sentences got the most tags and why.</div>
        </div>
      </div>
      <div class="tl-line"></div>

      <div class="tl-row">
        <div class="tl-badge" style="background:#FCEBEB; color:#A32D2D;">4</div>
        <div class="tl-body">
          <div class="tl-name">💬 Class Discussion</div>
          <div class="tl-desc">The teacher leads discussion starting from the most-tagged sentences. Anonymous memos are read aloud to spark conversation.</div>
        </div>
      </div>
      <div class="tl-line"></div>

      <div class="tl-row">
        <div class="tl-badge" style="background:#F0F4FF; color:#3D5291;">↻</div>
        <div class="tl-body">
          <div class="tl-name">🔄 Next Class Connection</div>
          <div class="tl-desc">Words tagged <em>"Confusing"</em> in Reading automatically become the next Word session's focus. Each lesson feeds the next.</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# 메인: 스타일 / 사이드바 / 라우팅
# ══════════════════════════════════════════════════════════════════════════
init_db()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp { background: #F0F4FF; }
section[data-testid="stSidebar"] { background: #1C2340; }
section[data-testid="stSidebar"] * { color: #C8CFEE !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 📚 English Class")
    st.markdown("---")
    page = st.radio("페이지", ["📋 Overview", "🗂 Word", "📖 Reading"],
                    label_visibility="collapsed")
    st.markdown("---")
    role = st.radio("역할", ["👤 학생", "👩‍🏫 교사"])
    student_name = ""
    if role == "👤 학생":
        student_name = st.text_input("이름", placeholder="홍길동").strip()
    st.markdown("---")
    st.caption("Daea High School · 1학년 영어")

is_teacher = (role == "👩‍🏫 교사")

# ── 라우팅 ──────────────────────────────────────────────────────────────────
if page == "📋 Overview":
    render_overview()

elif page == "🗂 Word":
    if is_teacher:
        flip_teacher_view()
    elif student_name:
        flip_student_view(student_name)
    else:
        st.info("👈 사이드바에서 이름을 입력하세요.")

elif page == "📖 Reading":
    if is_teacher:
        ts_teacher_view()
    elif student_name:
        ts_student_view(student_name)
    else:
        st.info("👈 사이드바에서 이름을 입력하세요.")

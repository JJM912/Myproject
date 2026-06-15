"""
flip_recall.py — 앱 1: Flip & Recall
교사가 단어 카드를 제어하고, 학생은 개별 자기평가를 합니다.
"""
import streamlit as st
import db


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
def teacher_view():
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
                db.flip_add_word(w.strip(), m.strip(), e.strip())
                st.rerun()

        col_a, col_b = st.columns(2)
        if col_a.button("📚 샘플 단어 5개 불러오기"):
            for w, m, e in SAMPLE_WORDS:
                db.flip_add_word(w, m, e)
            st.rerun()
        if col_b.button("🗑️ 전체 단어 삭제"):
            db.flip_clear_words()
            db.set_state("flip_state", "active", "false")
            st.rerun()

        words = db.flip_get_words()
        st.markdown(f"**등록된 단어: {len(words)}개**")
        for word in words:
            wc1, wc2, wc3, wc4 = st.columns([2, 2, 3, 1])
            wc1.markdown(f"**{word['word']}**")
            wc2.markdown(word["meaning"])
            wc3.caption(word["example"] or "—")
            if wc4.button("삭제", key=f"del_w_{word['id']}"):
                db.flip_delete_word(word["id"])
                st.rerun()

    if not words:
        st.info("단어를 먼저 등록해 주세요.")
        return

    st.markdown("---")

    # ── 카드 진행 제어 ─────────────────────────────────────────────────
    active = db.get_state("flip_state", "active", "false") == "true"
    current_idx = int(db.get_state("flip_state", "current_idx", "0"))
    flipped = db.get_state("flip_state", "flipped", "false") == "true"

    st.markdown("### 🎬 카드 진행 제어")

    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns(4)
    if ctrl1.button("▶ 시작 / 첫 카드", type="primary"):
        db.set_state("flip_state", "active", "true")
        db.set_state("flip_state", "current_idx", "0")
        db.set_state("flip_state", "flipped", "false")
        db.flip_clear_responses()
        st.rerun()

    if ctrl2.button("🔄 카드 뒤집기", disabled=not active):
        db.set_state("flip_state", "flipped", "true")
        st.rerun()

    if ctrl3.button("⏭ 다음 카드", disabled=not active):
        if current_idx < len(words) - 1:
            db.set_state("flip_state", "current_idx", str(current_idx + 1))
            db.set_state("flip_state", "flipped", "false")
        else:
            db.set_state("flip_state", "active", "false")
        st.rerun()

    if ctrl4.button("⏹ 종료"):
        db.set_state("flip_state", "active", "false")
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
        responses = db.flip_get_responses(word["id"])
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
        all_resp = db.flip_get_responses()
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
def student_view(student_name):
    st.markdown("## 👤 Flip & Recall")
    st.caption(f"{student_name} 님 — 카드를 보고 뜻을 떠올린 뒤, 솔직하게 자기평가하세요.")

    active = db.get_state("flip_state", "active", "false") == "true"
    current_idx = int(db.get_state("flip_state", "current_idx", "0"))
    flipped = db.get_state("flip_state", "flipped", "false") == "true"
    words = db.flip_get_words()

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
        my_resp = [r for r in db.flip_get_responses(word["id"]) if r["student"] == student_name]
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
                    db.flip_save_response(student_name, word["id"], key)
                    st.rerun()

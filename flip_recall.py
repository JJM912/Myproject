"""
flip_recall.py — Word: Flip & Recall
역할 구분 없이 단일 화면. 학생은 위쪽 카드 활동, 교사는 아래쪽 '수업 설정'을 펼쳐서 사용.
"""
import streamlit as st
import db

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


def render(student_name):
    """student_name: 학생 이름. 비어있으면 '익명'으로 처리."""
    st.markdown("## 🗂 Word — Flip & Recall")

    words = db.flip_get_words()
    active = db.get_state("flip_state", "active", "false") == "true"
    current_idx = int(db.get_state("flip_state", "current_idx", "0"))
    flipped = db.get_state("flip_state", "flipped", "false") == "true"

    # ══════════════════════════════════════════════════════════════════
    # 활동 영역 (모두가 보는 곳)
    # ══════════════════════════════════════════════════════════════════
    if not active or not words or current_idx >= len(words):
        st.info("아직 카드가 시작되지 않았습니다. 선생님이 카드를 시작하면 여기에 나타납니다.")
    else:
        word = words[current_idx]
        st.markdown(f"#### 카드 {current_idx + 1} / {len(words)}")

        if not flipped:
            st.markdown(f"""
            <div style="background:white; border:2px solid #3C3489; border-radius:16px;
                        padding:2.5rem; text-align:center;">
              <div style="font-size:2.8rem; font-weight:800; color:#3C3489;">{word['word']}</div>
              <div style="color:#aaa; margin-top:12px;">뜻을 머릿속으로 떠올려 보세요</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:white; border:2px solid #085041; border-radius:16px;
                        padding:1.6rem; text-align:center;">
              <div style="font-size:2.2rem; font-weight:800; color:#3C3489;">{word['word']}</div>
              <div style="font-size:1.4rem; color:#085041; margin-top:8px;">{word['meaning']}</div>
              <div style="color:#888; font-style:italic; margin-top:8px;">{word['example']}</div>
            </div>
            """, unsafe_allow_html=True)

        # 학생 자기평가 (뒤집힌 후, 이름이 있을 때)
        if flipped:
            sname = student_name.strip() if student_name else ""
            if not sname:
                st.warning("👈 사이드바에서 이름을 입력하면 자기평가를 할 수 있어요.")
            else:
                my_resp = [r for r in db.flip_get_responses(word["id"]) if r["student"] == sname]
                if my_resp:
                    info = RATINGS[my_resp[0]["rating"]]
                    st.success(f"평가 완료: {info['label']} — 다음 카드를 기다려 주세요.")
                else:
                    st.markdown("##### 얼마나 알고 있었나요?")
                    bc1, bc2, bc3 = st.columns(3)
                    for col, key in zip([bc1, bc2, bc3], ["known", "unsure", "unknown"]):
                        if col.button(RATINGS[key]["label"], key=f"rate_{key}", use_container_width=True):
                            db.flip_save_response(sname, word["id"], key)
                            st.rerun()

        # 실시간 집계 (모두가 봄)
        st.markdown("##### 📊 우리 반 집계")
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
            <div style="background:{info['bg']}; border-radius:10px; padding:0.9rem; text-align:center;">
              <div style="font-size:1.6rem; font-weight:800; color:{info['color']};">{counts[key]}</div>
              <div style="font-size:12px; color:{info['color']};">{info['label']} ({pct}%)</div>
            </div>
            """, unsafe_allow_html=True)
        st.caption(f"총 {total}명 응답")

    if st.button("🔄 새로고침", key="flip_refresh"):
        st.rerun()

    # ══════════════════════════════════════════════════════════════════
    # 수업 설정 (교사용 — 접혀 있음)
    # ══════════════════════════════════════════════════════════════════
    st.markdown("---")
    with st.expander("⚙️ 수업 설정 (선생님용)", expanded=False):

        st.markdown("**① 단어 등록**")
        with st.form("add_word", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 2, 3])
            w = c1.text_input("영단어", placeholder="ambiguous")
            m = c2.text_input("뜻", placeholder="모호한")
            e = c3.text_input("예문(선택)", placeholder="The instructions were ambiguous.")
            if st.form_submit_button("➕ 추가") and w and m:
                db.flip_add_word(w.strip(), m.strip(), e.strip())
                st.rerun()

        cc1, cc2 = st.columns(2)
        if cc1.button("📚 샘플 5개 불러오기"):
            for w, m, e in SAMPLE_WORDS:
                db.flip_add_word(w, m, e)
            st.rerun()
        if cc2.button("🗑️ 전체 단어 삭제"):
            db.flip_clear_words()
            db.set_state("flip_state", "active", "false")
            st.rerun()

        if words:
            st.caption(f"등록된 단어 {len(words)}개")
            for word in words:
                wc1, wc2, wc3 = st.columns([3, 3, 1])
                wc1.markdown(f"**{word['word']}**")
                wc2.caption(word["meaning"])
                if wc3.button("삭제", key=f"del_w_{word['id']}"):
                    db.flip_delete_word(word["id"])
                    st.rerun()

        st.markdown("---")
        st.markdown("**② 카드 진행**")
        b1, b2, b3, b4 = st.columns(4)
        if b1.button("▶ 시작", use_container_width=True):
            db.set_state("flip_state", "active", "true")
            db.set_state("flip_state", "current_idx", "0")
            db.set_state("flip_state", "flipped", "false")
            db.flip_clear_responses()
            st.rerun()
        if b2.button("🔄 뒤집기", use_container_width=True, disabled=not active):
            db.set_state("flip_state", "flipped", "true")
            st.rerun()
        if b3.button("⏭ 다음", use_container_width=True, disabled=not active):
            if current_idx < len(words) - 1:
                db.set_state("flip_state", "current_idx", str(current_idx + 1))
                db.set_state("flip_state", "flipped", "false")
            else:
                db.set_state("flip_state", "active", "false")
            st.rerun()
        if b4.button("⏹ 종료", use_container_width=True):
            db.set_state("flip_state", "active", "false")
            st.rerun()

        # '몰랐어' 집계
        st.markdown("---")
        st.markdown("**③ '몰랐어' 단어 (복습 재료)**")
        all_resp = db.flip_get_responses()
        unknown_by_word = {}
        for r in all_resp:
            if r["rating"] == "unknown":
                unknown_by_word.setdefault(r["word_id"], []).append(r["student"])
        if unknown_by_word:
            for word in words:
                if word["id"] in unknown_by_word:
                    st.caption(f"**{word['word']}** ({word['meaning']}) — {len(unknown_by_word[word['id']])}명")
        else:
            st.caption("아직 '몰랐어' 응답이 없습니다.")

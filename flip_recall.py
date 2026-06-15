"""
flip_recall.py — Word: Flip & Recall

학생 화면
1. Class Practice
   - 교사가 제시한 단어 카드 확인
   - I Know It / Save to My Words 선택

2. My Words
   - 학번별 개인 단어장
   - 저장한 단어 복습
   - 외운 단어 Remove

교사 화면
- 단어 등록
- 카드 시작 / 뒤집기 / 다음 / 종료
- 응답 집계 확인
"""

import streamlit as st
import db

SAMPLE_WORDS = [
    ("pollution", "오염", "The river suffered from serious pollution."),
    ("waste", "폐기물", "Factories dumped waste into the river."),
    ("industrial", "산업의", "Industrial growth changed the city."),
    ("movement", "운동", "The photo helped start an environmental movement."),
]


def render(student_id="", role="Student"):
    st.markdown("## 🗂 Word — Flip & Recall")

    tab1, tab2 = st.tabs(["Class Practice", "My Words"])

    with tab1:
        render_class_practice(student_id, role)

    with tab2:
        render_my_words(student_id, role)

    if role == "Teacher":
        st.markdown("---")
        render_teacher_controls()


def render_class_practice(student_id, role):
    words = db.flip_get_words()
    active = db.get_state("flip_state", "active", "false") == "true"
    current_idx = int(db.get_state("flip_state", "current_idx", "0"))
    flipped = db.get_state("flip_state", "flipped", "false") == "true"

    if not words:
        st.info("아직 단어 세트가 없습니다. 선생님이 단어를 등록하면 여기에 나타납니다.")
        return

    if not active or current_idx >= len(words):
        st.info("아직 카드가 시작되지 않았습니다. 선생님이 카드를 시작하면 여기에 나타납니다.")
        return

    word = words[current_idx]

    st.caption(f"Card {current_idx + 1} / {len(words)}")

    if not flipped:
        st.markdown(
            f"""
            <div style="background:white; border:2px solid #3C3489; border-radius:18px;
                        padding:3rem; text-align:center;">
              <div style="font-size:3rem; font-weight:900; color:#3C3489;">{word['word']}</div>
              <div style="color:#777; margin-top:12px;">Think about the meaning.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        st.markdown(
            f"""
            <div style="background:white; border:2px solid #085041; border-radius:18px;
                        padding:2rem; text-align:center;">
              <div style="font-size:2.4rem; font-weight:900; color:#3C3489;">{word['word']}</div>
              <div style="font-size:1.5rem; color:#085041; margin-top:10px;">{word['meaning']}</div>
              <div style="color:#777; font-style:italic; margin-top:10px;">{word['example']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if role == "Student":
            student_id = student_id.strip()

            if not student_id:
                st.warning("왼쪽 사이드바에 학번을 입력하면 응답할 수 있어요.")
            else:
                existing = [
                    r for r in db.flip_get_responses(word["id"])
                    if r["student"] == student_id
                ]

                if existing:
                    response = existing[0]["response"]

                    if response == "know":
                        st.success("응답 완료: I Know It")
                    else:
                        st.success("응답 완료: Save to My Words")
                else:
                    col1, col2 = st.columns(2)

                    if col1.button("✅ I Know It", use_container_width=True):
                        db.flip_save_response(student_id, word["id"], "know")
                        st.rerun()

                    if col2.button("⭐ Save to My Words", use_container_width=True):
                        db.flip_save_response(student_id, word["id"], "save")
                        db.my_words_add(
                            student_id,
                            word["id"],
                            word["word"],
                            word["meaning"],
                            word["example"],
                        )
                        st.rerun()

    st.markdown("### Class Summary")
    render_word_summary(word["id"])

    if st.button("🔄 Refresh", key="flip_refresh"):
        st.rerun()


def render_word_summary(word_id):
    responses = db.flip_get_responses(word_id)

    know = sum(1 for r in responses if r["response"] == "know")
    save = sum(1 for r in responses if r["response"] == "save")
    total = know + save

    col1, col2, col3 = st.columns(3)

    col1.metric("I Know It", know)
    col2.metric("Saved to My Words", save)
    col3.metric("Total Responses", total)


def render_my_words(student_id, role):
    if role != "Student":
        st.info("My Words는 학생 개인 복습 공간입니다.")
        return

    student_id = student_id.strip()

    if not student_id:
        st.warning("왼쪽 사이드바에 학번을 입력하면 My Words를 볼 수 있어요.")
        return

    my_words = db.my_words_get(student_id)

    if not my_words:
        st.info("아직 저장한 단어가 없습니다.")
        return

    st.caption("수업 중 저장한 단어를 복습하세요. 외웠다면 Remove를 누르세요.")

    for item in my_words:
        with st.container(border=True):
            st.markdown(f"### {item['word']}")
            st.markdown(f"**Meaning:** {item['meaning']}")

            if item["example"]:
                st.markdown(f"> {item['example']}")

            if st.button("Remove", key=f"remove_my_word_{item['id']}"):
                db.my_words_delete(item["id"], student_id)
                st.rerun()


def render_teacher_controls():
    st.markdown("## ⚙️ Word Teacher Controls")

    words = db.flip_get_words()
    active = db.get_state("flip_state", "active", "false") == "true"
    current_idx = int(db.get_state("flip_state", "current_idx", "0"))

    with st.expander("① Add Words", expanded=True):
        st.markdown("한 줄에 하나씩 입력하세요.")

        st.code("pollution, 오염, The river suffered from serious pollution.")

        raw_words = st.text_area(
            "Word list",
            height=160,
            placeholder=(
                "pollution, 오염, The river suffered from serious pollution.\n"
                "waste, 폐기물, Factories dumped waste into the river."
            ),
        )

        col1, col2 = st.columns(2)

        if col1.button("Add Words", use_container_width=True):
            added = 0

            for line in raw_words.splitlines():
                parts = [p.strip() for p in line.split(",", 2)]

                if len(parts) >= 2:
                    word = parts[0]
                    meaning = parts[1]
                    example = parts[2] if len(parts) == 3 else ""

                    if word and meaning:
                        db.flip_add_word(word, meaning, example)
                        added += 1

            st.success(f"{added}개 단어를 추가했습니다.")
            st.rerun()

        if col2.button("Load Sample Words", use_container_width=True):
            for word, meaning, example in SAMPLE_WORDS:
                db.flip_add_word(word, meaning, example)
            st.rerun()

        if words:
            st.markdown("#### Current Words")

            for word in words:
                c1, c2, c3 = st.columns([2, 3, 1])

                c1.markdown(f"**{word['word']}**")
                c2.caption(word["meaning"])

                if c3.button("Delete", key=f"delete_word_{word['id']}"):
                    db.flip_delete_word(word["id"])
                    st.rerun()

        if st.button("Delete All Words"):
            db.flip_clear_words()
            db.set_state("flip_state", "active", "false")
            db.set_state("flip_state", "current_idx", "0")
            db.set_state("flip_state", "flipped", "false")
            st.rerun()

    with st.expander("② Control Cards", expanded=True):
        c1, c2, c3, c4 = st.columns(4)

        if c1.button("▶ Start", use_container_width=True, disabled=not words):
            db.set_state("flip_state", "active", "true")
            db.set_state("flip_state", "current_idx", "0")
            db.set_state("flip_state", "flipped", "false")
            db.flip_clear_responses()
            st.rerun()

        if c2.button("🔄 Flip", use_container_width=True, disabled=not active):
            db.set_state("flip_state", "flipped", "true")
            st.rerun()

        if c3.button("⏭ Next", use_container_width=True, disabled=not active):
            if current_idx < len(words) - 1:
                db.set_state("flip_state", "current_idx", str(current_idx + 1))
                db.set_state("flip_state", "flipped", "false")
            else:
                db.set_state("flip_state", "active", "false")

            st.rerun()

        if c4.button("⏹ Stop", use_container_width=True):
            db.set_state("flip_state", "active", "false")
            st.rerun()

    with st.expander("③ Results", expanded=True):
        if not words:
            st.info("단어가 없습니다.")
        else:
            rows = []

            for word in words:
                responses = db.flip_get_responses(word["id"])

                know = sum(1 for r in responses if r["response"] == "know")
                save = sum(1 for r in responses if r["response"] == "save")

                rows.append({
                    "word": word["word"],
                    "meaning": word["meaning"],
                    "I Know It": know,
                    "Saved to My Words": save,
                })

            st.table(rows)

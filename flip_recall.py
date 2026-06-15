"""
flip_recall.py — Word

- 단어 목록은 코드에서 관리
- 학생 화면은 자동 새로고침으로 교사 카드 이동을 반영
- Teacher Settings에서 현재 단어를 큰 화면으로 미리보기
"""

import json
import hashlib
import html

import streamlit as st
import db

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None


CODE_WORDS = [
    {"word": "capture", "meaning": "정확히 포착하다, 담아내다", "definition": "v. to record or take a picture with a camera"},
    {"word": "grab hold of", "meaning": "~을 (움켜)잡다", "definition": "to get or catch someone’s attention or interest"},
    {"word": "convey", "meaning": "(생각·감정 등을) 전달하다", "definition": "v. to communicate or express a thought, feeling, or idea, with or without using words"},
    {"word": "complex", "meaning": "복잡한", "definition": "a. hard to understand or explain"},
    {"word": "spark", "meaning": "촉발하다, 유발하다", "definition": "v. to cause something to happen or start, especially suddenly"},
    {"word": "industry", "meaning": "산업", "definition": "n. the production of things by using machines and factories"},
    {"word": "steel mill", "meaning": "제철소", "definition": "a factory that makes steel"},
    {"word": "regard", "meaning": "~을 ···으로 여기다[평가하다]", "definition": "v. to consider or think of someone or something in a certain way"},
    {"word": "economic", "meaning": "경제의", "definition": "a. relating to the production, trade, and usage of goods and services"},
    {"word": "likely", "meaning": "가능성 있는, 그럴듯한", "definition": "a. having a high chance of happening or being true"},
    {"word": "flare", "meaning": "(순간적으로) 확 타오르는 불길, 불꽃", "definition": "n. a bright fire or light that does not last long"},
    {"word": "oil-soaked", "meaning": "기름에 흠뻑 젖은", "definition": "made completely wet by oil"},
    {"word": "beneath", "meaning": "아래에", "definition": "prep. in a lower position or under someone or something"},
    {"word": "article", "meaning": "(신문·잡지의) 글, 기사", "definition": "n. a piece of writing on a certain topic in a printed or online newspaper or magazine"},
    {"word": "feature", "meaning": "특별히 포함하다, 특징으로 삼다", "definition": "v. to have something as an important part by giving attention to it"},
    {"word": "flame", "meaning": "불길, 불꽃", "definition": "n. the hot, bright gas of a fire"},
    {"word": "put out", "meaning": "(불을) 끄다", "definition": "to make something stop burning"},
    {"word": "impact", "meaning": "영향", "definition": "n. a strong effect that someone or something has on another"},
    {"word": "awareness", "meaning": "의식, 관심", "definition": "n. knowledge or understanding of a certain fact, subject, or situation"},
    {"word": "standard", "meaning": "수준, 기준", "definition": "n. a level of quality that is required or considered acceptable"},
    {"word": "establish", "meaning": "설립[설정]하다; 수립하다", "definition": "v. to start or create something that is meant to last for a long time"},
    {"word": "passage", "meaning": "통로; (법안의) 처리, 통과", "definition": "n. the official approval of something, such as a law"},
    {"word": "expose", "meaning": "드러내다; 폭로하다", "definition": "v. to make known or reveal something that is usually bad"},
    {"word": "harsh", "meaning": "가혹한, 냉혹한", "definition": "a. cruel, severe, or unkind"},
    {"word": "revolution", "meaning": "혁명", "definition": "n. a sudden, great change in the way people live or think"},
    {"word": "employ", "meaning": "고용하다", "definition": "v. to pay someone for work or to do a job"},
    {"word": "go on strike", "meaning": "파업하다", "definition": "to stop working so that one’s employer accepts one’s demands"},
    {"word": "reveal", "meaning": "드러내다, 밝히다", "definition": "v. to make known secret or hidden information to others"},
    {"word": "committee", "meaning": "위원회", "definition": "n. a group of people that were chosen to make decisions or act on something"},
    {"word": "investigative", "meaning": "조사[수사]의", "definition": "a. involving the examination of something to discover the truth"},
    {"word": "pretend", "meaning": "~인 척하다, ~라고 가장하다", "definition": "v. to act like something is true when you know that it is not"},
    {"word": "insurance", "meaning": "보험; 보험업", "definition": "n. an agreement in which one gives money to a company so that the company can pay for some kind of future loss"},
    {"word": "inspector", "meaning": "조사관, 감독관", "definition": "n. someone whose job is to ensure that official standards are met through critical examination"},
    {"word": "take advantage of", "meaning": "~을 이용하다", "definition": "to unfairly use someone or something for one’s own benefit"},
    {"word": "helpless", "meaning": "무력한", "definition": "a. unable to protect oneself or to act without support from others"},
    {"word": "weave", "meaning": "짜다[엮다], 짜서[엮어서] 만들다", "definition": "v. to twist and cross long pieces of material to make cloth, a carpet, a basket, etc."},
    {"word": "equipment", "meaning": "장비, 용품", "definition": "n. the tools, machines, etc. that are needed for a certain activity or purpose"},
    {"word": "tragic", "meaning": "비극적인, 비극의", "definition": "a. causing great sadness, often relating to death or suffering"},
    {"word": "can't help but", "meaning": "~하지 않을 수 없다", "definition": "to not be able to do anything else but"},
    {"word": "exhibition", "meaning": "전시회, 전시", "definition": "n. an event where objects such as paintings or photographs are shown to the public"},
    {"word": "ban", "meaning": "금하다, 금지하다", "definition": "v. to legally or officially say that something is not allowed"},
    {"word": "congress", "meaning": "의회, 국회", "definition": "n. the group of people chosen to create laws for a nation, especially the US"},
    {"word": "illegal", "meaning": "불법적인", "definition": "a. not allowed by law"},
]


def safe(text):
    return html.escape(str(text))


def word_auto_refresh(key, interval=2000):
    """
    교사가 카드를 넘기면 학생 화면에 자동 반영되도록 2초마다 새로고침.
    streamlit-autorefresh가 설치되지 않아도 앱이 멈추지 않도록 처리.
    """
    if st_autorefresh is not None:
        st_autorefresh(interval=interval, key=key)


def get_code_words_hash():
    text = json.dumps(CODE_WORDS, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sync_code_words_if_needed():
    current_hash = get_code_words_hash()
    saved_hash = db.get_state("flip_state", "code_words_hash", "")
    current_words = db.flip_get_words()

    if saved_hash == current_hash and current_words:
        return

    db.flip_clear_words()

    for item in CODE_WORDS:
        word = item["word"].strip()
        meaning = item["meaning"].strip()
        definition = item.get("definition", "").strip()

        if word and meaning:
            db.flip_add_word(word, meaning, definition)

    db.set_state("flip_state", "code_words_hash", current_hash)
    db.set_state("flip_state", "active", "false")
    db.set_state("flip_state", "current_idx", "0")
    db.set_state("flip_state", "flipped", "false")


def get_current_word_state():
    words = db.flip_get_words()
    active = db.get_state("flip_state", "active", "false") == "true"
    current_idx = int(db.get_state("flip_state", "current_idx", "0"))
    flipped = db.get_state("flip_state", "flipped", "false") == "true"

    if not words:
        return words, active, current_idx, flipped, None

    if current_idx >= len(words):
        current_idx = len(words) - 1
        db.set_state("flip_state", "current_idx", str(current_idx))

    current_word = words[current_idx]
    return words, active, current_idx, flipped, current_word


def render_word_card(word, current_idx, total, flipped, teacher_preview=False):
    word_text = safe(word["word"])
    meaning_text = safe(word["meaning"])
    definition_text = safe(word.get("example", ""))

    label = "Teacher Preview" if teacher_preview else "Card"

    if not flipped:
        st.markdown(
            f"""
            <div style="background:white; border:3px solid #38BDF8; border-radius:22px;
                        padding:3.5rem 2rem; text-align:center;
                        box-shadow:0 10px 25px rgba(56,189,248,.18); margin-bottom:1rem;">
              <div style="font-size:1rem; font-weight:900; color:#0284C7; margin-bottom:1rem;">
                {label} {current_idx + 1} / {total}
              </div>
              <div style="font-size:4rem; font-weight:900; color:#0284C7;">
                {word_text}
              </div>
              <div style="color:#64748B; margin-top:16px; font-size:1.1rem;">
                Think about the meaning.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="background:white; border:3px solid #38BDF8; border-radius:22px;
                        padding:3rem 2rem; text-align:center;
                        box-shadow:0 10px 25px rgba(56,189,248,.18); margin-bottom:1rem;">
              <div style="font-size:1rem; font-weight:900; color:#0284C7; margin-bottom:1rem;">
                {label} {current_idx + 1} / {total}
              </div>
              <div style="font-size:3.4rem; font-weight:900; color:#0284C7;">
                {word_text}
              </div>
              <div style="font-size:1.8rem; color:#0F172A; font-weight:900; margin-top:14px;">
                {meaning_text}
              </div>
              <div style="color:#475569; font-style:italic; margin-top:16px; font-size:1.1rem;">
                {definition_text}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render(student_id=""):
    sync_code_words_if_needed()

    st.markdown("## ✏️ Word")

    tab1, tab2 = st.tabs(["Class Practice", "My Words"])

    with tab1:
        render_class_practice(student_id)

    with tab2:
        render_my_words(student_id)


def render_class_practice(student_id):
    word_auto_refresh("student_word_refresh", interval=2000)

    words, active, current_idx, flipped, word = get_current_word_state()

    if not words:
        st.info("아직 단어가 등록되지 않았습니다.")
        return

    if not active or word is None:
        st.info("아직 카드가 시작되지 않았습니다. 선생님이 시작하면 여기에 나타납니다.")
        return

    render_word_card(word, current_idx, len(words), flipped, teacher_preview=False)

    student_id = student_id.strip()

    if not student_id:
        st.warning("왼쪽 사이드바에 학번을 입력하면 응답할 수 있어요.")
        return

    existing = [
        r for r in db.flip_get_responses(word["id"])
        if r["student"] == student_id
    ]

    current_response = existing[0]["response"] if existing else ""

    if current_response == "know":
        st.success("현재 응답: I Know It")
    elif current_response == "save":
        st.success("현재 응답: Save to My Words")

    c1, c2 = st.columns(2)

    if c1.button("✅ I Know It", width="stretch", key=f"know_{word['id']}"):
        db.flip_save_response(student_id, word["id"], "know")
        st.rerun()

    if c2.button("⭐ Save to My Words", width="stretch", key=f"save_{word['id']}"):
        db.flip_save_response(student_id, word["id"], "save")
        db.my_words_add(
            student_id,
            word["id"],
            word["word"],
            word["meaning"],
            word.get("example", ""),
        )
        st.rerun()

    st.markdown("### Class Summary")
    render_word_summary(word["id"])

    if st.button("🔄 Refresh", key="flip_refresh"):
        st.rerun()


def render_word_summary(word_id):
    responses = db.flip_get_responses(word_id)

    know = sum(1 for r in responses if r["response"] == "know")
    save_count = sum(1 for r in responses if r["response"] == "save")
    total = know + save_count

    c1, c2, c3 = st.columns(3)
    c1.metric("I Know It", know)
    c2.metric("Save to My Words", save_count)
    c3.metric("Total Responses", total)


def render_my_words(student_id):
    student_id = student_id.strip()

    if not student_id:
        st.warning("왼쪽 사이드바에 학번을 입력하면 My Words를 볼 수 있어요.")
        return

    my_words = db.my_words_get(student_id)

    if not my_words:
        st.info("아직 저장한 단어가 없습니다.")
        return

    st.caption("저장한 단어를 복습하고, 외웠다면 Remove를 누르세요.")

    for item in my_words:
        with st.container(border=True):
            st.markdown(f"### {safe(item['word'])}")
            st.markdown(f"**Meaning:** {safe(item['meaning'])}")

            if item.get("example"):
                st.markdown(f"> {safe(item['example'])}")

            if st.button("Remove", key=f"remove_{item['id']}"):
                db.my_words_delete(item["id"], student_id)
                st.rerun()


def render_teacher_controls():
    sync_code_words_if_needed()
    word_auto_refresh("teacher_word_refresh", interval=2500)

    st.markdown("### Word Settings")

    words, active, current_idx, flipped, current_word = get_current_word_state()

    st.info(
        f"현재 단어 목록은 코드의 CODE_WORDS에서 자동으로 불러옵니다. "
        f"등록된 단어 수: {len(words)}개"
    )

    with st.expander("① Control Cards", expanded=True):
        c1, c2, c3, c4 = st.columns(4)

        if c1.button("▶ Start", width="stretch", disabled=not words):
            db.set_state("flip_state", "active", "true")
            db.set_state("flip_state", "current_idx", "0")
            db.set_state("flip_state", "flipped", "false")
            db.flip_clear_responses()
            st.rerun()

        if c2.button("🔄 Flip", width="stretch", disabled=not active):
            db.set_state("flip_state", "flipped", "true")
            st.rerun()

        if c3.button("⏭ Next", width="stretch", disabled=not active):
            if current_idx < len(words) - 1:
                db.set_state("flip_state", "current_idx", str(current_idx + 1))
                db.set_state("flip_state", "flipped", "false")
            else:
                db.set_state("flip_state", "active", "false")

            st.rerun()

        if c4.button("⏹ Stop", width="stretch"):
            db.set_state("flip_state", "active", "false")
            st.rerun()

        if words and active:
            st.caption(f"Current card: {current_idx + 1} / {len(words)}")
            st.progress((current_idx + 1) / len(words))

    with st.expander("② Current Student Screen", expanded=True):
        if not words:
            st.info("단어가 없습니다.")
        elif not active or current_word is None:
            st.info("아직 카드가 시작되지 않았습니다. Start를 누르면 학생 화면에 단어가 나타납니다.")
        else:
            render_word_card(
                current_word,
                current_idx,
                len(words),
                flipped,
                teacher_preview=True,
            )

            st.caption(
                "이 카드가 현재 학생 Word 페이지에 보이는 카드입니다. "
                "학생 화면은 약 2초마다 자동 갱신됩니다."
            )

    with st.expander("③ Results", expanded=True):
        if not words:
            st.info("단어가 없습니다.")
        else:
            rows = []

            for word in words:
                responses = db.flip_get_responses(word["id"])

                know = sum(1 for r in responses if r["response"] == "know")
                save_count = sum(1 for r in responses if r["response"] == "save")
                total = know + save_count

                rows.append(
                    {
                        "word": word["word"],
                        "meaning": word["meaning"],
                        "I Know It": know,
                        "Save to My Words": save_count,
                        "Total": total,
                    }
                )

            st.table(rows)

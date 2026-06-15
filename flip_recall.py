"""
flip_recall.py — Word
단어 카드 + My Words + 교사용 어휘 일괄 입력
쪽수 없이 어휘 / 뜻 / 영영 뜻풀이만 사용
"""

import re
import html
import streamlit as st
import db


LESSON4_WORDS = [
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


def render(student_id=""):
    st.markdown("## ✏️ Word")

    tab1, tab2 = st.tabs(["Class Practice", "My Words"])

    with tab1:
        render_class_practice(student_id)

    with tab2:
        render_my_words(student_id)


def safe(text):
    return html.escape(str(text))


def make_example(definition):
    definition = str(definition).strip()
    return definition


def render_class_practice(student_id):
    words = db.flip_get_words()
    active = db.get_state("flip_state", "active", "false") == "true"
    current_idx = int(db.get_state("flip_state", "current_idx", "0"))
    flipped = db.get_state("flip_state", "flipped", "false") == "true"

    if not words:
        st.info("아직 단어가 등록되지 않았습니다. 왼쪽 Teacher Settings에서 단어를 등록하세요.")
        return

    if not active or current_idx >= len(words):
        st.info("아직 카드가 시작되지 않았습니다. 선생님이 시작하면 여기에 나타납니다.")
        return

    word = words[current_idx]
    st.caption(f"Card {current_idx + 1} / {len(words)}")

    word_text = safe(word["word"])
    meaning_text = safe(word["meaning"])
    example_text = safe(word.get("example", ""))

    if not flipped:
        st.markdown(
            f"""
            <div style="background:white; border:2px solid #38BDF8; border-radius:18px;
                        padding:3rem; text-align:center; box-shadow:0 8px 20px rgba(56,189,248,.15);">
              <div style="font-size:3rem; font-weight:900; color:#0284C7;">{word_text}</div>
              <div style="color:#64748B; margin-top:12px;">Think about the meaning.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="background:white; border:2px solid #38BDF8; border-radius:18px;
                        padding:2rem; text-align:center; box-shadow:0 8px 20px rgba(56,189,248,.15);">
              <div style="font-size:2.5rem; font-weight:900; color:#0284C7;">{word_text}</div>
              <div style="font-size:1.55rem; color:#0F172A; font-weight:800; margin-top:10px;">{meaning_text}</div>
              <div style="color:#475569; font-style:italic; margin-top:12px;">{example_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
                c1, c2 = st.columns(2)

                if c1.button("✅ I Know It", width="stretch"):
                    db.flip_save_response(student_id, word["id"], "know")
                    st.rerun()

                if c2.button("⭐ Save to My Words", width="stretch"):
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
    c2.metric("Saved to My Words", save_count)
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


def parse_bulk_words(raw_text):
    """
    입력 가능 형식 1:
    capture | 정확히 포착하다, 담아내다 | v. to record ...

    입력 가능 형식 2:
    capture    정확히 포착하다, 담아내다    v. to record ...

    입력 가능 형식 3:
    83 | capture | 정확히 포착하다, 담아내다 | v. to record ...
    → 이 경우 쪽수 83은 자동으로 무시됨.
    """

    records = []

    raw_text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

    skip_words = {
        "쪽",
        "어휘",
        "뜻",
        "영영 뜻풀이",
        "page",
        "word",
        "meaning",
        "definition",
    }

    lines = [line for line in lines if line.lower() not in skip_words]

    for line in lines:
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
        elif "\t" in line:
            parts = [p.strip() for p in line.split("\t")]
        else:
            parts = re.split(r"\s{2,}", line.strip())

        parts = [p for p in parts if p]

        word = ""
        meaning = ""
        definition = ""

        if len(parts) >= 4 and parts[0].isdigit():
            # 쪽수 포함 형식이면 첫 번째 값은 무시
            word = parts[1]
            meaning = parts[2]
            definition = " ".join(parts[3:])
        elif len(parts) >= 3:
            word = parts[0]
            meaning = parts[1]
            definition = " ".join(parts[2:])
        elif len(parts) == 2:
            word = parts[0]
            meaning = parts[1]

        if word and meaning:
            records.append(
                {
                    "word": word,
                    "meaning": meaning,
                    "definition": definition,
                }
            )

    return records


def add_word_records(records, replace=False):
    if replace:
        db.flip_clear_words()
        db.set_state("flip_state", "active", "false")
        db.set_state("flip_state", "current_idx", "0")
        db.set_state("flip_state", "flipped", "false")

    existing_words = {
        item["word"].strip().lower()
        for item in db.flip_get_words()
    }

    added = 0
    skipped = 0

    for record in records:
        word = record.get("word", "").strip()
        meaning = record.get("meaning", "").strip()
        definition = record.get("definition", "").strip()

        if not word or not meaning:
            skipped += 1
            continue

        key = word.lower()

        if key in existing_words:
            skipped += 1
            continue

        example = make_example(definition)

        db.flip_add_word(word, meaning, example)

        existing_words.add(key)
        added += 1

    return added, skipped


def render_teacher_controls():
    st.markdown("### Word Settings")

    words = db.flip_get_words()
    active = db.get_state("flip_state", "active", "false") == "true"
    current_idx = int(db.get_state("flip_state", "current_idx", "0"))

    with st.expander("① Load Lesson 4 Vocabulary", expanded=True):
        st.markdown(
            """
            Lesson 4 어휘 리스트를 바로 불러올 수 있습니다.  
            단어 카드에는 **어휘 → 뜻 → 영영 뜻풀이** 순서로 표시됩니다.
            """
        )

        st.caption(f"Lesson 4 vocabulary: {len(LESSON4_WORDS)} words")

        preview_rows = [
            {
                "word": item["word"],
                "meaning": item["meaning"],
                "definition": item["definition"],
            }
            for item in LESSON4_WORDS[:8]
        ]

        st.table(preview_rows)

        c1, c2 = st.columns(2)

        if c1.button("Add Lesson 4 Words", width="stretch"):
            added, skipped = add_word_records(LESSON4_WORDS, replace=False)
            st.success(f"{added}개 추가, {skipped}개 건너뜀")
            st.rerun()

        if c2.button("Replace with Lesson 4 Words", width="stretch"):
            added, skipped = add_word_records(LESSON4_WORDS, replace=True)
            st.success(f"기존 단어를 지우고 {added}개 단어를 불러왔습니다.")
            st.rerun()

    with st.expander("② Paste Your Own Vocabulary Table", expanded=False):
        st.markdown(
            """
            다른 단어 자료를 넣을 때는 아래 형식으로 붙여넣으면 됩니다.

            **추천 형식**
            """
        )

        st.code(
            """capture | 정확히 포착하다, 담아내다 | v. to record or take a picture with a camera
convey | 전달하다 | v. to communicate or express a thought, feeling, or idea
impact | 영향 | n. a strong effect that someone or something has on another"""
        )

        raw_words = st.text_area(
            "Vocabulary table",
            height=180,
            placeholder="어휘 | 뜻 | 영영 뜻풀이",
        )

        parsed = parse_bulk_words(raw_words) if raw_words.strip() else []

        if parsed:
            st.markdown("#### Preview")
            st.table(parsed[:10])
            st.caption(f"총 {len(parsed)}개 단어가 인식되었습니다.")

        c1, c2 = st.columns(2)

        if c1.button("Add Pasted Words", width="stretch"):
            if not parsed:
                st.warning("인식된 단어가 없습니다. 입력 형식을 확인하세요.")
            else:
                added, skipped = add_word_records(parsed, replace=False)
                st.success(f"{added}개 추가, {skipped}개 건너뜀")
                st.rerun()

        if c2.button("Replace with Pasted Words", width="stretch"):
            if not parsed:
                st.warning("인식된 단어가 없습니다. 입력 형식을 확인하세요.")
            else:
                added, skipped = add_word_records(parsed, replace=True)
                st.success(f"기존 단어를 지우고 {added}개 단어를 불러왔습니다.")
                st.rerun()

    with st.expander("③ Current Words", expanded=False):
        words = db.flip_get_words()

        if not words:
            st.info("현재 등록된 단어가 없습니다.")
        else:
            st.caption(f"현재 {len(words)}개 단어가 등록되어 있습니다.")

            for word in words:
                w1, w2, w3 = st.columns([2, 4, 1])
                w1.markdown(f"**{safe(word['word'])}**")
                w2.caption(f"{word['meaning']} / {word.get('example', '')}")

                if w3.button("Delete", key=f"delete_word_{word['id']}"):
                    db.flip_delete_word(word["id"])
                    st.rerun()

            if st.button("Delete All Words"):
                db.flip_clear_words()
                db.set_state("flip_state", "active", "false")
                db.set_state("flip_state", "current_idx", "0")
                db.set_state("flip_state", "flipped", "false")
                st.rerun()

    with st.expander("④ Control Cards", expanded=True):
        words = db.flip_get_words()

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

    with st.expander("⑤ Results", expanded=False):
        words = db.flip_get_words()

        if not words:
            st.info("단어가 없습니다.")
        else:
            rows = []

            for word in words:
                responses = db.flip_get_responses(word["id"])
                know = sum(1 for r in responses if r["response"] == "know")
                save_count = sum(1 for r in responses if r["response"] == "save")

                rows.append(
                    {
                        "word": word["word"],
                        "meaning": word["meaning"],
                        "I Know It": know,
                        "Saved to My Words": save_count,
                    }
                )

            st.table(rows)

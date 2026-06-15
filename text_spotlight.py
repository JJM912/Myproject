"""
text_spotlight.py — Reading
"""

import re
import html
from collections import defaultdict

import streamlit as st
import db

TAGS = {
    "글의 주제": {
        "color": "#8A4B00",
        "bg": "#FFF1D6",
        "border": "#F4A62A",
        "icon": "📍",
    },
    "날개 문제 근거": {
        "color": "#075F4A",
        "bg": "#DFF7EE",
        "border": "#2AA876",
        "icon": "🔍",
    },
    "문법·구조": {
        "color": "#4636A8",
        "bg": "#EEECFF",
        "border": "#6C5CE7",
        "icon": "✏️",
    },
    "이해 안 됨": {
        "color": "#A32D2D",
        "bg": "#FCE5E5",
        "border": "#E05252",
        "icon": "❓",
    },
}

NO_TAG = "선택 안 함"

SAMPLE_TEXT = """In the 1880s, industry began to grow rapidly along the Cuyahoga River in the city of Cleveland. This industrial growth provided steady jobs to people in the area. Meanwhile, steel mills and factories started dumping large amounts of waste into the river. Although the river became polluted, most people simply regarded this as a sign of the area’s economic success."""

SAMPLE_QUESTIONS = [
    "Why did the Cuyahoga River become polluted?",
    "What did most people think the polluted river showed?",
]


def split_sentences(text):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


def render(student_id=""):
    st.markdown("## 📚 Reading")

    sentences = db.ts_get_sentences()
    revealed = db.get_state("ts_state", "reveal", "false") == "true"

    render_student_reading(student_id, sentences, revealed)


def render_student_reading(student_id, sentences, revealed):
    student_id = student_id.strip()

    if not student_id:
        st.warning("왼쪽 사이드바에 학번을 입력하면 Reading 활동에 참여할 수 있어요.")
        return

    if not sentences:
        st.info("아직 등록된 지문이 없습니다.")
        return

    questions = db.ts_get_questions()

    if questions:
        with st.expander("📌 Wing Questions", expanded=True):
            for i, question in enumerate(questions, 1):
                st.markdown(f"**Q{i}.** {question['text']}")

    render_tag_legend()

    if revealed:
        st.success("🔓 Class tags are now open. Discuss the results together.")
        render_class_shared_view()
        return

    if db.ts_is_submitted(student_id):
        st.success("제출 완료! 선생님이 태그를 공개하면 반 전체 결과를 볼 수 있어요.")
        render_own_readonly_view(student_id, sentences)
        return

    st.info("문장을 읽고 카테고리를 선택하면 해당 색상으로 하이라이트됩니다. 의견은 문장 옆 박스에 적으세요.")

    for sent in sentences:
        idx = sent["idx"]
        sentence_text = sent["text"]

        existing_tags = db.ts_get_student_tags(student_id, idx)
        existing_tag = existing_tags[0] if existing_tags else NO_TAG
        existing_memo = db.ts_get_student_memo(student_id, idx)

        widget_key = f"student_tag_{idx}"
        memo_key = f"student_memo_{idx}"

        current_tag = st.session_state.get(widget_key, existing_tag)
        if current_tag not in TAGS:
            current_tag = NO_TAG

        tag_info = TAGS.get(
            current_tag,
            {
                "color": "#1F2937",
                "bg": "#FFFFFF",
                "border": "#E0E8FF",
                "icon": "",
            },
        )

        left, right = st.columns([2.4, 1])

        with left:
            render_sentence_card(
                sentence_number=idx + 1,
                sentence=sentence_text,
                tag_info=tag_info,
                selected_tag=current_tag,
            )

        with right:
            st.markdown(
                f"""
                <div style="background:white; border:1px solid #E0E8FF; border-radius:14px;
                            padding:12px; margin-bottom:6px;">
                <b>Your tag & opinion</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

            options = [NO_TAG] + list(TAGS.keys())
            default_index = options.index(current_tag) if current_tag in options else 0

            st.selectbox(
                "Category",
                options,
                index=default_index,
                key=widget_key,
                label_visibility="collapsed",
            )

            st.text_area(
                "Opinion",
                value=existing_memo,
                key=memo_key,
                placeholder="Write your reason, question, or opinion.",
                height=105,
                label_visibility="collapsed",
            )

        st.markdown("")

    c1, c2 = st.columns(2)

    if c1.button("Save Draft", use_container_width=True):
        save_current_tags(student_id, sentences)
        st.success("저장되었습니다. 제출 전이라 수정할 수 있어요.")
        st.rerun()

    if c2.button("Submit Reading Tags", type="primary", use_container_width=True):
        save_current_tags(student_id, sentences)
        db.ts_mark_submitted(student_id)
        st.rerun()


def render_sentence_card(sentence_number, sentence, tag_info, selected_tag):
    safe_sentence = html.escape(sentence)

    if selected_tag == NO_TAG:
        chip = "<span style='color:#9CA3AF; font-size:12px;'>No highlight yet</span>"
    else:
        chip = (
            f"<span style='background:{tag_info['bg']}; color:{tag_info['color']}; "
            f"border:1px solid {tag_info['border']}; padding:4px 10px; "
            f"border-radius:20px; font-size:12px; font-weight:800;'>"
            f"{tag_info['icon']} {selected_tag}</span>"
        )

    st.markdown(
        f"""
        <div style="background:{tag_info['bg']}; border:2px solid {tag_info['border']};
                    border-radius:16px; padding:18px 20px; min-height:150px;">
          <div style="font-size:12px; font-weight:900; color:{tag_info['color']};
                      margin-bottom:8px;">
            Sentence {sentence_number}
          </div>
          <div style="font-size:20px; line-height:1.75; font-weight:900; color:#111827;">
            {safe_sentence}
          </div>
          <div style="margin-top:12px;">
            {chip}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def save_current_tags(student_id, sentences):
    for sent in sentences:
        idx = sent["idx"]
        selected_tag = st.session_state.get(f"student_tag_{idx}", NO_TAG)
        memo = st.session_state.get(f"student_memo_{idx}", "")

        if selected_tag == NO_TAG:
            db.ts_save_tags(student_id, idx, [])
        else:
            db.ts_save_tags(student_id, idx, [selected_tag])

        db.ts_save_memo(student_id, idx, memo)


def render_own_readonly_view(student_id, sentences):
    st.markdown("### Your submitted tags")

    for sent in sentences:
        idx = sent["idx"]
        tags = db.ts_get_student_tags(student_id, idx)
        memo = db.ts_get_student_memo(student_id, idx)

        tag = tags[0] if tags else NO_TAG
        tag_info = TAGS.get(
            tag,
            {
                "color": "#1F2937",
                "bg": "#FFFFFF",
                "border": "#E0E8FF",
                "icon": "",
            },
        )

        left, right = st.columns([2.4, 1])

        with left:
            render_sentence_card(idx + 1, sent["text"], tag_info, tag)

        with right:
            render_comment_box(student_id, tag, memo)


def render_class_shared_view():
    sentences = db.ts_get_sentences()
    all_tags = db.ts_get_all_tags()
    all_memos = db.ts_get_all_memos()

    tag_by_sentence = defaultdict(list)
    memo_by_sentence = defaultdict(list)

    for tag in all_tags:
        tag_by_sentence[tag["sentence_idx"]].append(tag)

    for memo in all_memos:
        memo_by_sentence[memo["sentence_idx"]].append(memo)

    for sent in sentences:
        idx = sent["idx"]

        dominant_tag = get_dominant_tag(tag_by_sentence[idx])
        tag_info = TAGS.get(
            dominant_tag,
            {
                "color": "#1F2937",
                "bg": "#FFFFFF",
                "border": "#E0E8FF",
                "icon": "",
            },
        )

        left, right = st.columns([2.2, 1.2])

        with left:
            render_sentence_card(
                sentence_number=idx + 1,
                sentence=sent["text"],
                tag_info=tag_info,
                selected_tag=dominant_tag,
            )

            render_sentence_tag_summary(tag_by_sentence[idx])

        with right:
            st.markdown("**Class opinions**")

            comments = memo_by_sentence[idx]

            if not comments:
                st.caption("No opinions yet.")
            else:
                for memo in comments:
                    student = memo["student"]
                    memo_text = memo["memo"]
                    student_tags = [
                        t["tag"]
                        for t in tag_by_sentence[idx]
                        if t["student"] == student
                    ]
                    tag = student_tags[0] if student_tags else NO_TAG
                    render_comment_box(student, tag, memo_text)

        st.markdown("")


def get_dominant_tag(tags):
    if not tags:
        return NO_TAG

    counts = defaultdict(int)

    for tag in tags:
        counts[tag["tag"]] += 1

    return max(counts.items(), key=lambda x: x[1])[0]


def render_sentence_tag_summary(tags):
    counts = defaultdict(int)

    for tag in tags:
        counts[tag["tag"]] += 1

    if not counts:
        st.caption("No class tags yet.")
        return

    chips = ""

    for tag_name, count in sorted(counts.items(), key=lambda x: -x[1]):
        info = TAGS[tag_name]
        chips += (
            f"<span style='background:{info['bg']}; color:{info['color']}; "
            f"border:1px solid {info['border']}; padding:4px 10px; "
            f"border-radius:20px; font-size:12px; font-weight:800; margin-right:5px;'>"
            f"{info['icon']} {tag_name} {count}</span>"
        )

    st.markdown(
        f"""
        <div style="margin-top:8px;">{chips}</div>
        """,
        unsafe_allow_html=True,
    )


def render_comment_box(student, tag, memo):
    safe_student = html.escape(student)
    safe_memo = html.escape(memo)

    if not safe_memo:
        safe_memo = "<span style='color:#999;'>No opinion</span>"

    info = TAGS.get(
        tag,
        {
            "color": "#1F2937",
            "bg": "#FFFFFF",
            "border": "#E0E8FF",
            "icon": "",
        },
    )

    tag_label = tag if tag != NO_TAG else "No tag"

    st.markdown(
        f"""
        <div style="background:{info['bg']}; border:1.5px solid {info['border']};
                    border-radius:14px; padding:10px 12px; margin-bottom:8px;">
          <div style="font-size:12px; font-weight:900; color:{info['color']}; margin-bottom:5px;">
            {info['icon']} {html.escape(tag_label)}
          </div>
          <div style="font-size:13px; font-weight:800; color:#111827;">
            {safe_student}
          </div>
          <div style="font-size:13px; line-height:1.5; color:#374151; margin-top:4px;">
            {safe_memo}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tag_legend():
    legend = ""

    for name, info in TAGS.items():
        legend += (
            f"<span style='background:{info['bg']}; color:{info['color']}; "
            f"border:1px solid {info['border']}; padding:5px 12px; "
            f"border-radius:20px; font-size:13px; font-weight:900; margin-right:6px;'>"
            f"{info['icon']} {name}</span>"
        )

    st.markdown(
        f"""
        <div style="margin:10px 0 16px 0;">{legend}</div>
        """,
        unsafe_allow_html=True,
    )


def render_teacher_controls(revealed):
    st.markdown("### ① Add Reading Text")

    if st.button("Load Sample Text"):
        st.session_state["ts_text_input"] = SAMPLE_TEXT
        st.session_state["ts_q_input"] = "\n".join(SAMPLE_QUESTIONS)
        st.rerun()

    text = st.text_area(
        "Reading text",
        value=st.session_state.get("ts_text_input", ""),
        height=180,
        key="ts_text_input",
    )

    questions = st.text_area(
        "Wing questions",
        value=st.session_state.get("ts_q_input", ""),
        height=90,
        key="ts_q_input",
        help="한 줄에 하나씩 입력하세요.",
    )

    if st.button("Start New Reading Activity", type="primary"):
        if not text.strip():
            st.warning("지문을 입력하세요.")
        else:
            sentence_list = split_sentences(text)
            question_list = [q.strip() for q in questions.splitlines() if q.strip()]

            db.ts_set_text(sentence_list)
            db.ts_set_questions(question_list)
            db.set_state("ts_state", "reveal", "false")

            st.success("새 Reading 활동을 시작했습니다.")
            st.rerun()

    st.markdown("---")
    st.markdown("### ② Share Control")

    participants = db.ts_get_participants()
    submitted = db.ts_get_submitted_list()

    c1, c2, c3 = st.columns(3)
    c1.metric("Participants", len(participants))
    c2.metric("Submitted", len(submitted))
    c3.metric("Writing", len(set(participants) - set(submitted)))

    if submitted:
        st.caption("Submitted: " + ", ".join(submitted))

    b1, b2 = st.columns(2)

    if b1.button("🔓 Show Class Tags", type="primary", use_container_width=True):
        db.set_state("ts_state", "reveal", "true")
        st.rerun()

    if b2.button("🔒 Hide Class Tags", use_container_width=True):
        db.set_state("ts_state", "reveal", "false")
        st.rerun()

    st.caption("Current status: " + ("Open" if revealed else "Hidden"))

    st.markdown("---")

    if st.button("Reset Student Tags Only"):
        db.ts_reset_all()
        db.set_state("ts_state", "reveal", "false")
        st.rerun()


def render_class_results():
    all_tags = db.ts_get_all_tags()
    all_memos = db.ts_get_all_memos()

    if not all_tags and not all_memos:
        st.info("아직 학생 태그가 없습니다.")
        return

    st.markdown("### Heatmap Preview")
    render_class_shared_view()

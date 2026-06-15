"""
text_spotlight.py — Reading: Text Spotlight

학생
- 문장별 태그
- 메모 작성
- 제출
- 교사가 공개하면 전체 결과 보기

교사
- 하단 Teacher Settings에서 비밀번호 입력 후 접근
"""

import re
from collections import defaultdict

import streamlit as st
import db

TEACHER_PASSWORD = "daea1234"

TAGS = {
    "글의 주제": {"color": "#633806", "bg": "#FAEEDA", "icon": "📍"},
    "날개 문제 근거": {"color": "#085041", "bg": "#E1F5EE", "icon": "🔍"},
    "문법·구조": {"color": "#3C3489", "bg": "#EEEDFE", "icon": "✏️"},
    "이해 안 됨": {"color": "#A32D2D", "bg": "#FCEBEB", "icon": "❓"},
}

SAMPLE_TEXT = """In the 1880s, industry began to grow rapidly along the Cuyahoga River in the city of Cleveland. This industrial growth provided steady jobs to people in the area. Meanwhile, steel mills and factories started dumping large amounts of waste into the river. Although the river became polluted, most people simply regarded this as a sign of the area’s economic success."""

SAMPLE_QUESTIONS = [
    "Why did the Cuyahoga River become polluted?",
    "What did most people think the polluted river showed?",
]


def split_sentences(text):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


def render(student_id=""):
    st.markdown("## 📚 Reading — Text Spotlight")

    sentences = db.ts_get_sentences()
    revealed = db.get_state("ts_state", "reveal", "false") == "true"

    render_student_reading(student_id, sentences, revealed)

    st.markdown("---")
    render_hidden_teacher_settings(sentences, revealed)


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
        render_heatmap(show_memos=True)
        return

    if db.ts_is_submitted(student_id):
        st.success("제출 완료! 선생님이 태그를 공개하면 반 전체 결과를 볼 수 있어요.")
        return

    st.info("각 문장을 읽고 해당되는 태그를 자유롭게 선택하세요. 메모는 선택입니다.")

    for sent in sentences:
        idx = sent["idx"]

        st.markdown(
            f"""
            <div style="background:white; border:1px solid #E0E8FF; border-radius:12px;
                        padding:14px 16px; margin-bottom:6px;">
              <span style="font-size:12px; color:#8FA8E8;">Sentence {idx + 1}</span><br>
              <span style="font-size:15px; line-height:1.7;">{sent['text']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        existing_tags = db.ts_get_student_tags(student_id, idx)
        existing_memo = db.ts_get_student_memo(student_id, idx)

        st.multiselect(
            "Choose tags",
            list(TAGS.keys()),
            default=existing_tags,
            key=f"student_tag_{idx}",
            label_visibility="collapsed",
        )

        st.text_input(
            "Memo",
            value=existing_memo,
            key=f"student_memo_{idx}",
            placeholder="Optional memo",
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


def save_current_tags(student_id, sentences):
    for sent in sentences:
        idx = sent["idx"]
        selected_tags = st.session_state.get(f"student_tag_{idx}", [])
        memo = st.session_state.get(f"student_memo_{idx}", "")
        db.ts_save_tags(student_id, idx, selected_tags)
        db.ts_save_memo(student_id, idx, memo)


def render_hidden_teacher_settings(sentences, revealed):
    with st.expander("🔐 Teacher Settings", expanded=False):
        pw = st.text_input(
            "Teacher password",
            type="password",
            key="reading_teacher_pw",
            placeholder="Enter password",
        )

        if not pw:
            st.caption("교사용 설정은 비밀번호 입력 후 사용할 수 있습니다.")
            return

        if pw != TEACHER_PASSWORD:
            st.error("비밀번호가 올바르지 않습니다.")
            return

        st.success("Teacher mode unlocked.")

        tab1, tab2, tab3 = st.tabs(["Preview", "Teacher Controls", "Class Results"])

        with tab1:
            if not sentences:
                st.info("아직 등록된 지문이 없습니다.")
            elif revealed:
                st.success("현재 학생들에게 히트맵이 공개되어 있습니다.")
                render_heatmap(show_memos=True)
            else:
                st.info("현재 학생들은 개별 태깅 중입니다. 히트맵은 숨겨져 있습니다.")
                render_text_preview()

        with tab2:
            render_teacher_controls(revealed)

        with tab3:
            render_class_results()


def render_text_preview():
    sentences = db.ts_get_sentences()
    questions = db.ts_get_questions()

    if questions:
        st.markdown("### Wing Questions")
        for i, question in enumerate(questions, 1):
            st.markdown(f"**Q{i}.** {question['text']}")

    st.markdown("### Text")
    for sent in sentences:
        st.markdown(f"**{sent['idx'] + 1}.** {sent['text']}")


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
    render_heatmap(show_memos=True)


def render_tag_legend():
    legend = " ".join(
        f"""
        <span style='background:{info["bg"]}; color:{info["color"]};
                     padding:4px 10px; border-radius:20px;
                     font-size:12px; font-weight:700; margin-right:5px;'>
            {info["icon"]} {name}
        </span>
        """
        for name, info in TAGS.items()
    )
    st.markdown(legend, unsafe_allow_html=True)
    st.markdown("")


def render_heatmap(show_memos=False):
    sentences = db.ts_get_sentences()
    all_tags = db.ts_get_all_tags()
    all_memos = db.ts_get_all_memos()
    participants = db.ts_get_participants()

    total_students = max(len(participants), 1)

    sent_tag_counts = defaultdict(lambda: defaultdict(int))
    sent_memos = defaultdict(list)

    for tag in all_tags:
        sent_tag_counts[tag["sentence_idx"]][tag["tag"]] += 1

    for memo in all_memos:
        sent_memos[memo["sentence_idx"]].append(memo)

    for sent in sentences:
        idx = sent["idx"]
        tag_counts = sent_tag_counts.get(idx, {})
        total_tags = sum(tag_counts.values())
        heat = total_tags / total_students

        if heat >= 1:
            bar = "#3C3489"
        elif heat >= 0.5:
            bar = "#9F9CE0"
        elif heat > 0:
            bar = "#D8D6F5"
        else:
            bar = "#EEEEEE"

        chips = ""
        for tag_name, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            info = TAGS.get(tag_name, {"bg": "#eee", "color": "#555", "icon": ""})
            chips += (
                f"<span style='background:{info['bg']}; color:{info['color']}; "
                f"padding:3px 9px; border-radius:20px; font-size:12px; "
                f"font-weight:700; margin-right:4px;'>"
                f"{info['icon']} {tag_name} {count}</span>"
            )

        memo_html = ""
        if show_memos and idx in sent_memos:
            memo_html = "<div style='margin-top:8px;'>"
            for memo in sent_memos[idx]:
                memo_html += (
                    f"<div style='font-size:13px; color:#666; margin-top:4px;'>"
                    f"💬 <b>{memo['student']}</b>: {memo['memo']}</div>"
                )
            memo_html += "</div>"

        st.markdown(
            f"""
            <div style="background:white; border-left:5px solid {bar};
                        border-radius:0 12px 12px 0; padding:14px 16px;
                        margin-bottom:8px; border-top:1px solid #eee;
                        border-right:1px solid #eee; border-bottom:1px solid #eee;">
              <span style="font-size:12px; color:#8FA8E8;">
                Sentence {idx + 1} · Tags {total_tags}
              </span><br>
              <span style="font-size:15px; line-height:1.7;">{sent['text']}</span>
              <div style="margin-top:8px;">
                {chips if chips else "<span style='color:#bbb; font-size:13px;'>No tags</span>"}
              </div>
              {memo_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Tag Type Summary")

    type_total = defaultdict(int)
    for tag in all_tags:
        type_total[tag["tag"]] += 1

    cols = st.columns(len(TAGS))
    for col, (name, info) in zip(cols, TAGS.items()):
        col.markdown(
            f"""
            <div style="background:{info['bg']}; border-radius:12px;
                        padding:12px; text-align:center;">
              <div style="font-size:1.5rem; font-weight:900; color:{info['color']};">
                {type_total.get(name, 0)}
              </div>
              <div style="font-size:12px; color:{info['color']};">
                {info['icon']} {name}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

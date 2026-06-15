"""
text_spotlight.py — Reading

- Reading text와 Questions는 코드에서 직접 관리
- 학생은 문장별 태그와 의견을 저장
- 전체 공유 전에는 본인 태그와 하이라이트만 확인
- 교사는 Teacher Settings에서 전체 공유/숨기기 조절
- 교사는 전체 학급 버전을 크게 확인 가능
"""

import re
import json
import hashlib
import html
from collections import defaultdict

import streamlit as st
import db


# =================================================
# Reading 본문과 질문
# 본문이나 질문을 바꾸고 싶으면 이 부분만 수정하면 됩니다.
# =================================================

CODE_READING_SECTIONS = [
    {
        "heading": "Pictures Worth a Thousand Words",
        "text": """
As quickly as a camera captures a scene, an image can grab hold of our emotions.
Through speech or written text, it can be difficult to convey a complex message quickly.
Yet photographs can change people’s hearts and minds in an instant.
And when the magic of photography sparks an emotional reaction in a great number of people, it can change history.
"""
    },
    {
        "heading": "The Burning River That Started a Movement",
        "text": """
In the 1880s, industry began to grow rapidly along the Cuyahoga River in the city of Cleveland.
This industrial growth provided steady jobs to people in the area.
Meanwhile, steel mills and factories started dumping large amounts of waste into the river.
Although the river became polluted, most people simply regarded this as a sign of the area’s economic success.
"""
    },
    {
        "heading": "",
        "text": """
In June 1969, the polluted river caught fire.
The likely cause was a burning flare falling from a train, which set fire to oil-soaked waste beneath a bridge.
At that time, few people in Cleveland cared.
This was because fires had been recorded on the Cuyahoga more than ten times before, and some of them had been much worse.
However, it wasn’t long before the 1969 fire became famous.
This was thanks to an article published in Time magazine that year.
The article featured a shocking photograph of flames and smoke rising from the river.
But this was not a photograph of the 1969 fire, which was put out so quickly that nobody took a picture of it.
In fact, it was a picture of a much worse fire that had occurred on the river several years earlier.
Still, the image had a great impact on people.
"""
    },
    {
        "heading": "",
        "text": """
Around that time, the attitudes of Americans toward environmental problems were starting to change.
More and more people were becoming aware of the need to protect the environment, and the shocking image of the burning river sparked public anger about water pollution.
As a result, the Cuyahoga River fire of 1969 became a symbol of pollution.
A national environmental awareness event was held on April 22, 1970, which later became known as the first Earth Day.
And in 1972, national water quality standards were established with the passage of the Clean Water Act.
"""
    },
]

CODE_QUESTIONS = [
    "Q1. How are photographs different from speech or written text according to the passage?",
    "Q2. Why did few people in Cleveland care when the Cuyahoga River caught fire in 1969?",
    "Q3. Over to You: How does the image of the burning Cuyahoga River make you feel?",
    "Q4. Why did 19th-century factory owners in the United States turn to child labor?",
]


# =================================================
# 태그 카테고리
# =================================================

TAGS = {
    "글의 주제": {
        "color": "#8A4B00",
        "bg": "#FFF1D6",
        "border": "#F4A62A",
        "icon": "📍",
    },
    "문제 근거": {
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


# =================================================
# 기본 유틸 함수
# =================================================

def safe(text):
    return html.escape(str(text))


def split_sentences(text):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


def build_reading_data():
    sentences = []
    heading_map = {}
    idx = 0

    for section in CODE_READING_SECTIONS:
        heading = section.get("heading", "").strip()
        section_sentences = split_sentences(section.get("text", ""))

        if heading and section_sentences:
            heading_map[idx] = heading

        for sentence in section_sentences:
            sentences.append(sentence)
            idx += 1

    return sentences, heading_map


def get_code_reading_hash():
    data = {
        "sections": CODE_READING_SECTIONS,
        "questions": CODE_QUESTIONS,
    }

    text = json.dumps(data, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sync_code_reading_if_needed():
    current_hash = get_code_reading_hash()
    saved_hash = db.get_state("ts_state", "code_reading_hash", "")

    current_sentences = db.ts_get_sentences()

    if saved_hash == current_hash and current_sentences:
        return

    sentences, _ = build_reading_data()

    db.ts_set_text(sentences)
    db.ts_set_questions(CODE_QUESTIONS)
    db.set_state("ts_state", "code_reading_hash", current_hash)
    db.set_state("ts_state", "reveal", "false")


def get_tag_info(tag):
    return TAGS.get(
        tag,
        {
            "color": "#1F2937",
            "bg": "#FFFFFF",
            "border": "#E0E8FF",
            "icon": "",
        },
    )


def normalize_tag(value):
    if isinstance(value, list):
        if len(value) == 0:
            return NO_TAG
        value = value[0]

    if value in TAGS:
        return value

    return NO_TAG


# =================================================
# 학생 Reading 화면
# =================================================

def render(student_id=""):
    sync_code_reading_if_needed()

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

    render_questions(expanded=True)
    render_tag_legend()

    if revealed:
        st.success("🔓 Class highlights are now shared.")
        render_class_shared_view(for_teacher=False, show_questions=False)
        return

    st.info("전체 공유 전에는 본인이 저장한 태그와 하이라이트만 볼 수 있습니다.")

    render_student_private_view(student_id, sentences)


def render_questions(expanded=True):
    questions = db.ts_get_questions()

    if not questions:
        return

    with st.expander("📌 Questions", expanded=expanded):
        for question in questions:
            st.markdown(f"**{question['text']}**")


def render_student_private_view(student_id, sentences):
    _, heading_map = build_reading_data()
    activity_id = get_code_reading_hash()[:8]

    for sent in sentences:
        idx = sent["idx"]

        if idx in heading_map:
            st.markdown(
                f"""
                <div style="margin-top:22px; margin-bottom:10px;">
                    <h2 style="color:#0284C7; font-weight:900;">
                        {safe(heading_map[idx])}
                    </h2>
                </div>
                """,
                unsafe_allow_html=True,
            )

        saved_tags = db.ts_get_student_tags(student_id, idx)
        saved_tag = normalize_tag(saved_tags[0]) if saved_tags else NO_TAG
        saved_memo = db.ts_get_student_memo(student_id, idx)

        tag_key = f"ts_tag_{activity_id}_{student_id}_{idx}"
        memo_key = f"ts_memo_{activity_id}_{student_id}_{idx}"

        if tag_key not in st.session_state:
            st.session_state[tag_key] = saved_tag

        st.session_state[tag_key] = normalize_tag(st.session_state[tag_key])

        if memo_key not in st.session_state:
            st.session_state[memo_key] = saved_memo

        left, right = st.columns([2.4, 1])

        with right:
            st.markdown(
                """
                <div style="background:white; border:1px solid #BAE6FD; border-radius:14px;
                            padding:12px; margin-bottom:6px;">
                <b>Your tag & opinion</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

            selected_tag = st.selectbox(
                "Category",
                [NO_TAG] + list(TAGS.keys()),
                key=tag_key,
                label_visibility="collapsed",
            )

            st.text_area(
                "Opinion",
                key=memo_key,
                placeholder="Write your reason, question, or opinion.",
                height=105,
                label_visibility="collapsed",
            )

        with left:
            tag_info = get_tag_info(selected_tag)

            render_sentence_card(
                sentence_number=idx + 1,
                sentence=sent["text"],
                tag_info=tag_info,
                selected_tag=selected_tag,
                large=False,
            )

        st.markdown("")

    if st.button("💾 Save My Tags", type="primary", width="stretch"):
        save_current_tags(student_id, sentences, activity_id)
        st.success("저장되었습니다. 전체 공유 전에는 본인에게만 보입니다.")
        st.rerun()


def save_current_tags(student_id, sentences, activity_id):
    for sent in sentences:
        idx = sent["idx"]

        tag_key = f"ts_tag_{activity_id}_{student_id}_{idx}"
        memo_key = f"ts_memo_{activity_id}_{student_id}_{idx}"

        selected_tag = normalize_tag(st.session_state.get(tag_key, NO_TAG))
        memo = st.session_state.get(memo_key, "")

        if selected_tag == NO_TAG:
            db.ts_save_tags(student_id, idx, [])
        else:
            db.ts_save_tags(student_id, idx, [selected_tag])

        db.ts_save_memo(student_id, idx, memo)


# =================================================
# 문장 카드 / 태그 / 코멘트 렌더링
# =================================================

def render_sentence_card(sentence_number, sentence, tag_info, selected_tag, large=False):
    safe_sentence = safe(sentence)

    font_size = "22px" if large else "20px"
    padding = "22px 24px" if large else "18px 20px"

    if selected_tag == NO_TAG:
        chip = "<span style='color:#9CA3AF; font-size:12px;'>No highlight yet</span>"
    else:
        chip = (
            f"<span style='background:{tag_info['bg']}; color:{tag_info['color']}; "
            f"border:1px solid {tag_info['border']}; padding:4px 10px; "
            f"border-radius:20px; font-size:12px; font-weight:800;'>"
            f"{tag_info['icon']} {safe(selected_tag)}</span>"
        )

    st.markdown(
        f"""
        <div style="background:{tag_info['bg']}; border:2px solid {tag_info['border']};
                    border-radius:16px; padding:{padding}; min-height:145px;">
          <div style="font-size:12px; font-weight:900; color:{tag_info['color']};
                      margin-bottom:8px;">
            Sentence {sentence_number}
          </div>
          <div style="font-size:{font_size}; line-height:1.75; font-weight:900; color:#111827;">
            {safe_sentence}
          </div>
          <div style="margin-top:12px;">
            {chip}
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
            f"{info['icon']} {safe(name)}</span>"
        )

    st.markdown(
        f"""
        <div style="margin:10px 0 16px 0;">{legend}</div>
        """,
        unsafe_allow_html=True,
    )


def render_comment_box(student, tag, memo):
    safe_student = safe(student)
    safe_memo = safe(memo)

    if not safe_memo:
        safe_memo = "<span style='color:#999;'>No opinion</span>"

    info = get_tag_info(tag)
    tag_label = tag if tag != NO_TAG else "No tag"

    st.markdown(
        f"""
        <div style="background:{info['bg']}; border:1.5px solid {info['border']};
                    border-radius:14px; padding:10px 12px; margin-bottom:8px;">
          <div style="font-size:12px; font-weight:900; color:{info['color']}; margin-bottom:5px;">
            {info['icon']} {safe(tag_label)}
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


# =================================================
# 전체 공유 화면
# =================================================

def render_class_shared_view(for_teacher=False, show_questions=True):
    sync_code_reading_if_needed()

    sentences = db.ts_get_sentences()
    all_tags = db.ts_get_all_tags()
    all_memos = db.ts_get_all_memos()
    _, heading_map = build_reading_data()

    tag_by_sentence = defaultdict(list)
    memo_by_sentence = defaultdict(list)

    for tag in all_tags:
        tag_by_sentence[tag["sentence_idx"]].append(tag)

    for memo in all_memos:
        memo_by_sentence[memo["sentence_idx"]].append(memo)

    if for_teacher:
        st.markdown("## 🖥️ Full Class Shared View")
        st.caption("교사용 전체 보기입니다. 학생 공유 여부와 관계없이 교사는 여기서 전체 결과를 확인할 수 있습니다.")

    if show_questions:
        render_questions(expanded=False)

    for sent in sentences:
        idx = sent["idx"]

        if idx in heading_map:
            st.markdown(
                f"""
                <div style="margin-top:26px; margin-bottom:10px;">
                    <h2 style="color:#0284C7; font-weight:900;">
                        {safe(heading_map[idx])}
                    </h2>
                </div>
                """,
                unsafe_allow_html=True,
            )

        dominant_tag = get_dominant_tag(tag_by_sentence[idx])
        tag_info = get_tag_info(dominant_tag)

        left, right = st.columns([2.2, 1.2])

        with left:
            render_sentence_card(
                sentence_number=idx + 1,
                sentence=sent["text"],
                tag_info=tag_info,
                selected_tag=dominant_tag,
                large=for_teacher,
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

                    tag = normalize_tag(student_tags[0]) if student_tags else NO_TAG
                    render_comment_box(student, tag, memo_text)

        st.markdown("")


def get_dominant_tag(tags):
    if not tags:
        return NO_TAG

    counts = defaultdict(int)

    for tag in tags:
        normalized = normalize_tag(tag["tag"])
        if normalized != NO_TAG:
            counts[normalized] += 1

    if not counts:
        return NO_TAG

    return max(counts.items(), key=lambda x: x[1])[0]


def render_sentence_tag_summary(tags):
    counts = defaultdict(int)

    for tag in tags:
        normalized = normalize_tag(tag["tag"])
        if normalized != NO_TAG:
            counts[normalized] += 1

    if not counts:
        st.caption("No class tags yet.")
        return

    chips = ""

    for tag_name, count in sorted(counts.items(), key=lambda x: -x[1]):
        info = get_tag_info(tag_name)

        chips += (
            f"<span style='background:{info['bg']}; color:{info['color']}; "
            f"border:1px solid {info['border']}; padding:4px 10px; "
            f"border-radius:20px; font-size:12px; font-weight:800; margin-right:5px;'>"
            f"{info['icon']} {safe(tag_name)} {count}</span>"
        )

    st.markdown(
        f"""
        <div style="margin-top:8px;">{chips}</div>
        """,
        unsafe_allow_html=True,
    )


# =================================================
# 교사 화면
# =================================================

def render_teacher_controls(revealed):
    sync_code_reading_if_needed()

    st.markdown("### Reading Settings")

    sentences = db.ts_get_sentences()
    participants = db.ts_get_participants()

    c1, c2, c3 = st.columns(3)
    c1.metric("Sentences", len(sentences))
    c2.metric("Participants", len(participants))
    c3.metric("Sharing", "Open" if revealed else "Hidden")

    st.markdown("---")

    st.markdown("### Share Control")

    b1, b2 = st.columns(2)

    if b1.button("🔓 Share Class Highlights", type="primary", width="stretch"):
        db.set_state("ts_state", "reveal", "true")
        st.rerun()

    if b2.button("🔒 Hide Class Highlights", width="stretch"):
        db.set_state("ts_state", "reveal", "false")
        st.rerun()

    st.caption(
        "공유 전에는 학생들이 본인의 태그와 하이라이트만 볼 수 있습니다. "
        "Share를 누르면 전체 학생의 태그와 의견이 함께 공개됩니다."
    )

    st.markdown("---")
    st.markdown("### Reset")

    if st.button("🗑️ Reset Student Tags Only", width="stretch"):
        db.ts_reset_all()
        db.set_state("ts_state", "reveal", "false")
        st.success("학생들의 태그, 하이라이트, 의견이 모두 삭제되었습니다.")
        st.rerun()


def render_class_results():
    sync_code_reading_if_needed()

    revealed = db.get_state("ts_state", "reveal", "false") == "true"

    if revealed:
        st.success("현재 학생들에게 전체 공유 화면이 공개되어 있습니다.")
    else:
        st.info("현재 학생들은 본인의 태그와 하이라이트만 볼 수 있습니다.")

    render_class_shared_view(for_teacher=True, show_questions=True)

"""
app.py — English Reading Lab

- 학생용 기본 화면
- Home / Word / Reading 메뉴를 버튼형으로 구성
- 교사용 설정은 왼쪽 아래 Teacher Settings에서 비밀번호로 접근
"""

import os
import streamlit as st
import db
import flip_recall
import text_spotlight

st.set_page_config(
    page_title="English Reading Lab",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()


def apply_style():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

        html, body, [class*="css"] {
            font-family: 'Nunito', sans-serif;
        }

        .stApp {
            background: #F0F4FF;
        }

        section[data-testid="stSidebar"] {
            background: #1C2340;
        }

        section[data-testid="stSidebar"] * {
            color: #D6DCF8 !important;
        }

        .home-top-label {
            text-align:center;
            font-size: 14px;
            font-weight: 800;
            letter-spacing: .14em;
            text-transform: uppercase;
            color: #3D5291;
            margin-top: 8px;
            margin-bottom: 18px;
        }

        .home-main-title {
            text-align:center;
            font-size: 3.3rem;
            font-weight: 900;
            color: #1C2340;
            margin-bottom: 20px;
            line-height: 1.1;
        }

        .home-main-title span {
            color: #4256A6;
        }

        div[data-testid="stButton"] > button {
            border-radius: 12px;
            font-weight: 700;
            text-align: left;
        }

        .sidebar-footer {
            font-size: 12px;
            color: #AEB8DD !important;
            margin-top: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_style()

if "student_id" not in st.session_state:
    st.session_state["student_id"] = ""

if "page" not in st.session_state:
    st.session_state["page"] = "Home"


def go_page(page_name):
    st.session_state["page"] = page_name
    st.rerun()


with st.sidebar:
    st.markdown("## 📚 English Reading Lab")

    student_id = st.text_input(
        "학번",
        value=st.session_state.get("student_id", ""),
        placeholder="예: 10101",
    )
    st.session_state["student_id"] = student_id.strip()

    st.markdown("---")

    if st.button("🏠 Home", use_container_width=True):
        go_page("Home")

    if st.button("✏️ Word", use_container_width=True):
        go_page("Word")

    if st.button("📚 Reading", use_container_width=True):
        go_page("Reading")

    st.markdown("---")

    if st.button("🔐 Teacher Settings", use_container_width=True):
        go_page("Teacher Settings")

    st.markdown(
        '<div class="sidebar-footer">Daea High School · Grade 1 English</div>',
        unsafe_allow_html=True,
    )


def find_home_image():
    possible_paths = [
        "home_student.png",
        "home_student.jpg",
        "home_student.jpeg",
        "assets/home_student.png",
        "assets/home_student.jpg",
        "assets/home_student.jpeg",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def show_home():
    _, center, _ = st.columns([1, 3, 1])

    with center:
        st.markdown(
            '<div class="home-top-label">Daea High School Grade 1 English Class</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="home-main-title">English <span>Reading Lab</span></div>',
            unsafe_allow_html=True,
        )

        image_path = find_home_image()

        if image_path:
            c1, c2, c3 = st.columns([1.6, 1.8, 1.6])
            with c2:
                st.image(image_path, use_container_width=True)
        else:
            st.warning(
                "그림 파일이 없습니다. GitHub 저장소에 home_student.png 파일을 업로드해 주세요."
            )


def show_teacher_settings():
    st.markdown("## 🔐 Teacher Settings")

    pw = st.text_input(
        "Teacher password",
        type="password",
        placeholder="Enter password",
    )

    if not pw:
        st.info("비밀번호를 입력하면 교사용 설정이 열립니다.")
        return

    if pw != "daea1234":
        st.error("비밀번호가 올바르지 않습니다.")
        return

    st.success("Teacher mode unlocked.")

    tab1, tab2 = st.tabs(["Word Settings", "Reading Settings"])

    with tab1:
        st.markdown("### Word Settings")
        flip_recall.render_teacher_controls()

    with tab2:
        st.markdown("### Reading Settings")
        revealed = db.get_state("ts_state", "reveal", "false") == "true"
        text_spotlight.render_teacher_controls(revealed)

        st.markdown("---")
        st.markdown("### Class Results")
        text_spotlight.render_class_results()


if st.session_state["page"] == "Home":
    show_home()

elif st.session_state["page"] == "Word":
    flip_recall.render(st.session_state.get("student_id", ""))

elif st.session_state["page"] == "Reading":
    text_spotlight.render(st.session_state.get("student_id", ""))

elif st.session_state["page"] == "Teacher Settings":
    show_teacher_settings()

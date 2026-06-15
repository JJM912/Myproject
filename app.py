"""
app.py — English Reading Lab

학생용 기본 화면
- Home / Word / Reading
- 교사 설정은 각 페이지 하단 Teacher Settings에서 접근
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
            margin-bottom: 12px;
            line-height: 1.1;
        }

        .home-main-title span {
            color: #4256A6;
        }

        .sidebar-note {
            font-size: 12px;
            color: #AEB8DD !important;
        }

        div[data-testid="stButton"] > button {
            border-radius: 12px;
            font-weight: 700;
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

NAV_OPTIONS = {
    "🏠 Home": "Home",
    "✏️ Word": "Word",
    "📚 Reading": "Reading",
}

# 현재 page에 맞는 radio 기본값 찾기
reverse_nav = {v: k for k, v in NAV_OPTIONS.items()}
default_label = reverse_nav.get(st.session_state["page"], "🏠 Home")

with st.sidebar:
    st.markdown("## 📚 English Reading Lab")

    student_id = st.text_input(
        "학번",
        value=st.session_state.get("student_id", ""),
        placeholder="예: 10101",
    )
    st.session_state["student_id"] = student_id.strip()

    st.markdown("---")

    selected_label = st.radio(
        "",
        list(NAV_OPTIONS.keys()),
        index=list(NAV_OPTIONS.keys()).index(default_label),
        label_visibility="collapsed",
    )

    st.session_state["page"] = NAV_OPTIONS[selected_label]

    st.markdown("---")
    st.markdown(
        '<div class="sidebar-note">Daea High School · Grade 1 English</div>',
        unsafe_allow_html=True,
    )


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

        image_path = "assets/home_student.png"

        if os.path.exists(image_path):
            c1, c2, c3 = st.columns([1.5, 2, 1.5])
            with c2:
                st.image(image_path, use_container_width=True)
        else:
            st.warning(
                "홈 그림 파일이 없습니다. 저장소에 assets/home_student.png 파일을 업로드해 주세요."
            )


if st.session_state["page"] == "Home":
    show_home()

elif st.session_state["page"] == "Word":
    flip_recall.render(st.session_state.get("student_id", ""))

elif st.session_state["page"] == "Reading":
    text_spotlight.render(st.session_state.get("student_id", ""))

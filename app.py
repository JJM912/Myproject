"""
app.py — English Reading Class

홈 화면:
- Daea High School
- English Reading Class
- home_student.png 그림 표시

왼쪽 메뉴:
- Home
- Word
- Reading
- Teacher Settings

교사 설정:
- 왼쪽 Teacher Settings에서 한 번에 관리
"""

import os
import streamlit as st

import db
import flip_recall
import text_spotlight


# -------------------------------------------------
# 기본 설정
# -------------------------------------------------
st.set_page_config(
    page_title="English Reading Class",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()

TEACHER_PASSWORD = "daea1234"


# -------------------------------------------------
# CSS 스타일
# -------------------------------------------------
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

        /* 왼쪽 사이드바 배경 */
        section[data-testid="stSidebar"] {
            background: #1C2340;
        }

        section[data-testid="stSidebar"] * {
            color: #D6DCF8 !important;
        }

        /* 왼쪽 메뉴 버튼 */
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
            background: #FFFFFF !important;
            color: #14213D !important;
            border: 1px solid #DDE5FF !important;
            border-radius: 12px;
            font-weight: 900;
            text-align: left;
            margin-bottom: 6px;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button p {
            color: #14213D !important;
            font-weight: 900 !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
            background: #EAF0FF !important;
            border: 1px solid #8FA8E8 !important;
        }

        /* 홈 화면 학교명 */
        .home-school {
            text-align: center;
            font-size: 1.25rem;
            font-weight: 900;
            letter-spacing: .18em;
            color: #2563EB;
            text-transform: uppercase;
            margin-top: 18px;
            margin-bottom: 8px;
        }

        /* 홈 화면 제목 */
        .home-title {
            text-align: center;
            font-size: 3.6rem;
            font-weight: 900;
            color: #0F172A;
            margin-bottom: 18px;
            line-height: 1.1;
        }

        .home-title .blue {
            color: #2563EB;
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


# -------------------------------------------------
# 세션 상태
# -------------------------------------------------
if "student_id" not in st.session_state:
    st.session_state["student_id"] = ""

if "page" not in st.session_state:
    st.session_state["page"] = "Home"


def go_page(page_name):
    st.session_state["page"] = page_name
    st.rerun()


# -------------------------------------------------
# 사이드바
# -------------------------------------------------
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


# -------------------------------------------------
# 홈 화면 그림
# -------------------------------------------------
def show_home_illustration():
    image_path = "home_student.png"

    if os.path.exists(image_path):
        c1, c2, c3 = st.columns([1.4, 1.7, 1.4])

        with c2:
            st.image(image_path, use_container_width=True)
    else:
        st.warning(
            "home_student.png 파일이 없습니다. "
            "GitHub 저장소에서 app.py와 같은 위치에 home_student.png를 업로드해 주세요."
        )


# -------------------------------------------------
# 홈 화면
# -------------------------------------------------
def show_home():
    _, center, _ = st.columns([1, 3, 1])

    with center:
        st.markdown(
            '<div class="home-school">Daea High School</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="home-title">English <span class="blue">Reading Class</span></div>',
            unsafe_allow_html=True,
        )

        show_home_illustration()


# -------------------------------------------------
# 교사 설정 화면
# -------------------------------------------------
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

    if pw != TEACHER_PASSWORD:
        st.error("비밀번호가 올바르지 않습니다.")
        return

    st.success("Teacher mode unlocked.")

    tab1, tab2 = st.tabs(["Word Settings", "Reading Settings"])

    with tab1:
        flip_recall.render_teacher_controls()

    with tab2:
        st.markdown("### Reading Settings")

        revealed = db.get_state("ts_state", "reveal", "false") == "true"

        text_spotlight.render_teacher_controls(revealed)

        st.markdown("---")
        st.markdown("### Class Results")
        text_spotlight.render_class_results()


# -------------------------------------------------
# 페이지 라우팅
# -------------------------------------------------
if st.session_state["page"] == "Home":
    show_home()

elif st.session_state["page"] == "Word":
    flip_recall.render(st.session_state.get("student_id", ""))

elif st.session_state["page"] == "Reading":
    text_spotlight.render(st.session_state.get("student_id", ""))

elif st.session_state["page"] == "Teacher Settings":
    show_teacher_settings()

"""
app.py — English Reading Lab

하나의 Streamlit 페이지에서
Overview / Word / Reading / Teacher Dashboard 이동
"""

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
            color: #C8CFEE !important;
        }

        .main-card {
            background: white;
            border: 1px solid #E0E8FF;
            border-radius: 18px;
            padding: 1.4rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(28,35,64,0.04);
        }

        .home-school {
            font-size: 14px;
            font-weight: 800;
            letter-spacing: .16em;
            color: #3D5291;
            text-transform: uppercase;
            margin-bottom: 18px;
            text-align: center;
        }

        .home-title-en {
            font-size: 3.1rem;
            font-weight: 900;
            color: #1C2340;
            line-height: 1.15;
            text-align: center;
            margin-bottom: 6px;
        }

        .home-title-en span {
            color: #3D5291;
        }

        .home-title-kr {
            font-size: 1.1rem;
            font-weight: 700;
            color: #5A6A8A;
            text-align: center;
            margin-bottom: 28px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_style()

if "student_id" not in st.session_state:
    st.session_state["student_id"] = ""

if "menu" not in st.session_state:
    st.session_state["menu"] = "Overview"

if "role" not in st.session_state:
    st.session_state["role"] = "Student"


with st.sidebar:
    st.markdown("## 📚 English Reading Lab")

    role = st.radio(
        "Mode",
        ["Student", "Teacher"],
        key="role",
        horizontal=True,
    )

    if role == "Student":
        student_id = st.text_input(
            "학번",
            value=st.session_state.get("student_id", ""),
            placeholder="예: 10101",
        )
        st.session_state["student_id"] = student_id.strip()
    else:
        st.info("Teacher mode")

    st.markdown("---")

    menu_options = ["Overview", "Word", "Reading"]

    if role == "Teacher":
        menu_options.append("Teacher Dashboard")

    if st.session_state.get("menu") not in menu_options:
        st.session_state["menu"] = "Overview"

    menu = st.radio(
        "Menu",
        menu_options,
        key="menu",
    )

    st.markdown("---")
    st.caption("Daea High School · Grade 1 English")


def show_overview():
    _, center, _ = st.columns([1, 3, 1])

    with center:
        st.markdown(
            '<div class="home-school">Daea High School</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="home-title-en">English <span>Reading Lab</span></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="home-title-kr">단어 예습 · 독해 태깅 · 토론 중심 영어 수업</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="main-card">
            <h3>What you will learn</h3>
            <p>
            In this app, you will preview key vocabulary, save difficult words,
            read a text closely, mark important sentences, and discuss your ideas
            with classmates.
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)

        with c1:
            st.markdown(
                """
                <div class="main-card">
                <h3>🗂 Word Practice</h3>
                <p>
                Check key words before reading. If a word is difficult,
                save it to My Words and review it later.
                </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("Go to Word", use_container_width=True):
                st.session_state["menu"] = "Word"
                st.rerun()

        with c2:
            st.markdown(
                """
                <div class="main-card">
                <h3>📖 Reading Activity</h3>
                <p>
                Tag sentences for main idea, evidence, grammar structure,
                or unclear parts. After sharing, discuss the class results.
                </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("Go to Reading", use_container_width=True):
                st.session_state["menu"] = "Reading"
                st.rerun()


def show_teacher_dashboard():
    st.markdown("## Teacher Dashboard")

    st.info(
        "Word와 Reading의 세부 설정은 각각 Word / Reading 메뉴 안에서 조작할 수 있습니다. "
        "아래 버튼으로 바로 이동하세요."
    )

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Open Word Controls", use_container_width=True):
            st.session_state["menu"] = "Word"
            st.rerun()

    with c2:
        if st.button("Open Reading Controls", use_container_width=True):
            st.session_state["menu"] = "Reading"
            st.rerun()

    st.markdown("---")

    st.markdown("### Recommended Class Flow")

    st.markdown(
        """
        1. **Word**에서 핵심 단어를 제시합니다.  
        2. 학생은 **I Know It / Save to My Words** 중 하나를 선택합니다.  
        3. **Reading**에서 학생은 네 가지 태그를 자유롭게 답니다.  
        4. 교사가 **Show Class Tags**를 누릅니다.  
        5. 학생들이 서로의 태그를 보며 토론합니다.
        """
    )


if menu == "Overview":
    show_overview()

elif menu == "Word":
    flip_recall.render(
        st.session_state.get("student_id", ""),
        role=role,
    )

elif menu == "Reading":
    text_spotlight.render(
        st.session_state.get("student_id", ""),
        role=role,
    )

elif menu == "Teacher Dashboard":
    show_teacher_dashboard()

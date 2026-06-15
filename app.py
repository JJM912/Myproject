"""
app.py — English Reading Class
"""

import streamlit as st
import db
import flip_recall
import text_spotlight

st.set_page_config(
    page_title="English Reading Class",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()

TEACHER_PASSWORD = "daea1234"


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

        div[data-testid="stButton"] > button {
            border-radius: 12px;
            font-weight: 800;
            text-align: left;
        }

        .home-school {
            text-align: center;
            font-size: 1.25rem;
            font-weight: 900;
            letter-spacing: .18em;
            color: #FF6B35;
            text-transform: uppercase;
            margin-top: 18px;
            margin-bottom: 8px;
        }

        .home-title {
            text-align: center;
            font-size: 3.6rem;
            font-weight: 900;
            color: #0F172A;
            margin-bottom: 18px;
            line-height: 1.1;
        }

        .home-title span {
            color: #E63946;
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


def show_home_illustration():
    st.markdown(
        """
        <div style="display:flex; justify-content:center; margin-top: 8px;">
        <svg width="430" height="360" viewBox="0 0 430 360" fill="none" xmlns="http://www.w3.org/2000/svg">
          <ellipse cx="215" cy="330" rx="150" ry="10" fill="#C7CDE8" opacity="0.55"/>

          <path d="M112 218 Q72 245 69 292 Q69 313 88 318 Q105 322 116 306 Q128 285 147 265 Z"
                fill="#F04E3E"/>
          <path d="M318 218 Q358 245 361 292 Q361 313 342 318 Q325 322 314 306 Q302 285 283 265 Z"
                fill="#F04E3E"/>

          <path d="M120 205 Q215 165 310 205 L298 315 L132 315 Z" fill="#F04E3E"/>
          <path d="M146 205 Q215 245 284 205 L270 315 L160 315 Z" fill="#F36A55"/>

          <rect x="193" y="164" width="44" height="42" rx="18" fill="#FFD2A8"/>
          <circle cx="215" cy="125" r="78" fill="#FFD2A8"/>
          <circle cx="133" cy="134" r="17" fill="#FFD2A8"/>
          <circle cx="297" cy="134" r="17" fill="#FFD2A8"/>

          <path d="M137 124
                   Q130 61 178 37
                   Q225 12 272 42
                   Q310 67 303 129
                   Q292 86 257 70
                   Q240 108 214 83
                   Q198 115 169 82
                   Q149 101 137 124Z"
                fill="#5A3824"/>

          <path d="M210 42 Q218 20 235 14" stroke="#5A3824" stroke-width="5" stroke-linecap="round"/>
          <path d="M229 67 Q239 91 259 101" stroke="#3D2418" stroke-width="5" stroke-linecap="round"/>
          <path d="M196 67 Q207 95 225 105" stroke="#3D2418" stroke-width="5" stroke-linecap="round"/>

          <circle cx="184" cy="130" r="7" fill="#191919"/>
          <circle cx="246" cy="130" r="7" fill="#191919"/>
          <path d="M215 139 Q209 150 216 154" stroke="#C7896E" stroke-width="2" stroke-linecap="round"/>
          <path d="M190 166 Q215 184 240 166" stroke="#8B4D3B" stroke-width="3" stroke-linecap="round" fill="none"/>

          <circle cx="170" cy="154" r="10" fill="#FFB4A3" opacity="0.45"/>
          <circle cx="260" cy="154" r="10" fill="#FFB4A3" opacity="0.45"/>

          <circle cx="111" cy="260" r="19" fill="#FFD2A8"/>
          <circle cx="319" cy="260" r="19" fill="#FFD2A8"/>

          <path d="M92 207 L212 246 L212 329 L92 287 Z"
                fill="#F5C23B" stroke="#3A2A1C" stroke-width="3"/>
          <path d="M338 207 L212 246 L212 329 L338 287 Z"
                fill="#F7C845" stroke="#3A2A1C" stroke-width="3"/>

          <path d="M212 246 L212 329" stroke="#9B711D" stroke-width="5"/>
          <path d="M202 247 L202 327" stroke="#E2A92D" stroke-width="2"/>
          <path d="M222 247 L222 327" stroke="#E2A92D" stroke-width="2"/>

          <path d="M100 207 L212 242" stroke="white" stroke-width="5"/>
          <path d="M330 207 L212 242" stroke="white" stroke-width="5"/>
          <path d="M110 220 L196 247" stroke="#D99F28" stroke-width="2"/>
          <path d="M320 220 L232 247" stroke="#D99F28" stroke-width="2"/>

          <path d="M98 251 Q116 257 127 272" stroke="#C7896E" stroke-width="3" stroke-linecap="round"/>
          <path d="M332 251 Q314 257 303 272" stroke="#C7896E" stroke-width="3" stroke-linecap="round"/>

          <line x1="50" y1="326" x2="380" y2="326" stroke="#444" stroke-width="2" opacity="0.5"/>
        </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_home():
    _, center, _ = st.columns([1, 3, 1])

    with center:
        st.markdown(
            '<div class="home-school">Daea High School</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="home-title">English <span>Reading Class</span></div>',
            unsafe_allow_html=True,
        )

        show_home_illustration()


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


if st.session_state["page"] == "Home":
    show_home()

elif st.session_state["page"] == "Word":
    flip_recall.render(st.session_state.get("student_id", ""))

elif st.session_state["page"] == "Reading":
    text_spotlight.render(st.session_state.get("student_id", ""))

elif st.session_state["page"] == "Teacher Settings":
    show_teacher_settings()

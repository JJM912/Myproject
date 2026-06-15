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
        <div style="display:flex; justify-content:center; margin-top: 10px;">
        <svg width="470" height="430" viewBox="0 0 470 430" fill="none" xmlns="http://www.w3.org/2000/svg">

          <!-- soft background -->
          <circle cx="235" cy="215" r="185" fill="#FFFFFF" opacity="0.42"/>
          <ellipse cx="235" cy="388" rx="150" ry="13" fill="#C9D2F2" opacity="0.45"/>

          <!-- hair -->
          <path d="M123 142
                   Q116 78 169 47
                   Q226 14 291 42
                   Q340 63 346 126
                   Q320 92 284 90
                   Q272 126 235 93
                   Q220 124 187 88
                   Q151 96 123 142Z"
                fill="#CFC7B9" stroke="#3D3D3D" stroke-width="4" stroke-linecap="round"/>

          <!-- hair curls -->
          <path d="M158 78
                   C198 42, 228 50, 202 83
                   C177 115, 224 114, 247 82
                   C274 45, 303 62, 278 98
                   C259 126, 302 126, 324 96"
                stroke="#3D3D3D" stroke-width="7" stroke-linecap="round" fill="none"/>

          <!-- ears -->
          <path d="M119 151
                   C92 144, 89 188, 117 188"
                fill="#FFFFFF" stroke="#3D3D3D" stroke-width="4" stroke-linecap="round"/>
          <path d="M349 151
                   C376 144, 379 188, 351 188"
                fill="#FFFFFF" stroke="#3D3D3D" stroke-width="4" stroke-linecap="round"/>

          <!-- face -->
          <path d="M118 131
                   C120 77, 165 48, 235 48
                   C305 48, 350 78, 352 134
                   C356 237, 291 283, 235 283
                   C179 283, 114 236, 118 131Z"
                fill="#FFFFFF" stroke="#3D3D3D" stroke-width="4" stroke-linecap="round"/>

          <!-- cheeks -->
          <circle cx="158" cy="190" r="19" fill="#FFB6B6" opacity="0.72"/>
          <circle cx="313" cy="190" r="19" fill="#FFB6B6" opacity="0.72"/>

          <!-- eyes -->
          <circle cx="196" cy="164" r="7" fill="#333333"/>
          <circle cx="278" cy="164" r="7" fill="#333333"/>

          <!-- nose -->
          <path d="M236 178
                   Q230 194 237 201"
                stroke="#3D3D3D" stroke-width="3" stroke-linecap="round" fill="none"/>

          <!-- smile -->
          <path d="M168 211
                   Q235 265 305 211"
                stroke="#3D3D3D" stroke-width="5" stroke-linecap="round" fill="none"/>

          <!-- shirt collar -->
          <path d="M171 281
                   L235 319
                   L299 281
                   L276 356
                   L194 356Z"
                fill="#FFD500" stroke="#3D3D3D" stroke-width="4"/>

          <path d="M184 283 L222 314 L205 335"
                stroke="#3D3D3D" stroke-width="4" stroke-linecap="round" fill="none"/>
          <path d="M286 283 L248 314 L265 335"
                stroke="#3D3D3D" stroke-width="4" stroke-linecap="round" fill="none"/>

          <!-- buttons -->
          <circle cx="235" cy="320" r="4" fill="#3D3D3D"/>
          <circle cx="235" cy="343" r="4" fill="#3D3D3D"/>

          <!-- arms -->
          <path d="M126 293
                   Q81 318 82 367
                   Q82 389 104 394
                   Q128 399 143 377
                   L161 332Z"
                fill="#FFFFFF" stroke="#3D3D3D" stroke-width="4"/>

          <path d="M344 293
                   Q389 318 388 367
                   Q388 389 366 394
                   Q342 399 327 377
                   L309 332Z"
                fill="#FFFFFF" stroke="#3D3D3D" stroke-width="4"/>

          <!-- book left -->
          <path d="M78 266
                   Q155 262 235 318
                   L235 408
                   Q151 342 82 358Z"
                fill="#FFD500" stroke="#3D3D3D" stroke-width="4" stroke-linejoin="round"/>

          <!-- book right -->
          <path d="M392 266
                   Q315 262 235 318
                   L235 408
                   Q319 342 388 358Z"
                fill="#FFD500" stroke="#3D3D3D" stroke-width="4" stroke-linejoin="round"/>

          <!-- book pages -->
          <path d="M86 254 Q160 249 235 306"
                stroke="#3D3D3D" stroke-width="4" stroke-linecap="round" fill="none"/>
          <path d="M384 254 Q310 249 235 306"
                stroke="#3D3D3D" stroke-width="4" stroke-linecap="round" fill="none"/>
          <path d="M96 241 Q166 239 235 292"
                stroke="#3D3D3D" stroke-width="3" stroke-linecap="round" fill="none"/>
          <path d="M374 241 Q304 239 235 292"
                stroke="#3D3D3D" stroke-width="3" stroke-linecap="round" fill="none"/>

          <!-- book center fold -->
          <path d="M235 318 L235 408"
                stroke="#3D3D3D" stroke-width="4" stroke-linecap="round"/>

          <!-- hands -->
          <path d="M102 310
                   Q128 303 138 328
                   Q144 350 127 367
                   Q113 379 97 365"
                fill="#FFFFFF" stroke="#3D3D3D" stroke-width="4" stroke-linecap="round"/>
          <path d="M368 310
                   Q342 303 332 328
                   Q326 350 343 367
                   Q357 379 373 365"
                fill="#FFFFFF" stroke="#3D3D3D" stroke-width="4" stroke-linecap="round"/>

          <!-- simple finger lines -->
          <path d="M113 325 Q127 326 135 340" stroke="#3D3D3D" stroke-width="3" stroke-linecap="round"/>
          <path d="M357 325 Q343 326 335 340" stroke="#3D3D3D" stroke-width="3" stroke-linecap="round"/>

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
            '<div class="home-title">English <span class="blue">Reading Class</span></div>',
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

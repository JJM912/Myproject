"""
app.py — English Reading Lab

- Home / Word / Reading
- 학생용 기본 화면
- 교사용은 각 페이지 하단의 숨겨진 Teacher Settings에서 접근
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
            margin-bottom: 6px;
            line-height: 1.1;
        }

        .home-main-title span {
            color: #4256A6;
        }

        .home-subtitle {
            text-align:center;
            font-size: 1.05rem;
            font-weight: 700;
            color: #60708D;
            margin-bottom: 20px;
        }

        .home-note {
            text-align:center;
            font-size: 0.95rem;
            color: #6D7A94;
            margin-top: 6px;
            margin-bottom: 14px;
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

if "menu" not in st.session_state:
    st.session_state["menu"] = "Home"


with st.sidebar:
    st.markdown("## 📚 English Reading Lab")

    student_id = st.text_input(
        "학번",
        value=st.session_state.get("student_id", ""),
        placeholder="예: 10101",
    )
    st.session_state["student_id"] = student_id.strip()

    st.markdown("---")

    menu_options = ["Home", "Word", "Reading"]

    if st.session_state.get("menu") not in menu_options:
        st.session_state["menu"] = "Home"

    st.radio(
        "Navigation",
        menu_options,
        key="menu",
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption("Daea High School · Grade 1 English")


def show_home():
    _, center, _ = st.columns([1, 3.4, 1])

    with center:
        st.markdown(
            '<div class="home-top-label">Daea High School Grade 1 English Class</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="home-main-title">English <span>Reading Lab</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="home-subtitle">Preview vocabulary, tag important parts, and discuss ideas together.</div>',
            unsafe_allow_html=True,
        )

        # 귀여운 남학생들 교복 입고 책 읽는 SVG
        st.markdown(
            """
            <div style="display:flex; justify-content:center; margin: 8px 0 12px 0;">
            <svg width="700" height="360" viewBox="0 0 700 360" fill="none" xmlns="http://www.w3.org/2000/svg">

              <!-- background blobs -->
              <circle cx="350" cy="170" r="135" fill="#E4EAFE"/>
              <circle cx="140" cy="250" r="55" fill="#DDEFF2"/>
              <circle cx="560" cy="120" r="60" fill="#FBE8E5"/>
              <circle cx="540" cy="275" r="38" fill="#FFF1CC"/>

              <!-- left boy -->
              <ellipse cx="180" cy="305" rx="75" ry="18" fill="#D6DEF5"/>
              <!-- legs -->
              <rect x="145" y="235" width="18" height="60" rx="9" fill="#5E6786"/>
              <rect x="170" y="235" width="18" height="60" rx="9" fill="#5E6786"/>
              <ellipse cx="154" cy="300" rx="14" ry="7" fill="#1C2340"/>
              <ellipse cx="179" cy="300" rx="14" ry="7" fill="#1C2340"/>
              <!-- body -->
              <rect x="128" y="160" width="78" height="85" rx="24" fill="#CFD8F6"/>
              <!-- blazer -->
              <path d="M128 178 Q167 145 206 178 L198 244 L136 244 Z" fill="#25335E"/>
              <!-- shirt -->
              <rect x="152" y="174" width="30" height="56" rx="8" fill="white"/>
              <!-- tie -->
              <path d="M167 180 L175 180 L171 205 Z" fill="#4256A6"/>
              <path d="M171 205 L177 225 L165 225 Z" fill="#4256A6"/>
              <!-- book -->
              <rect x="118" y="196" width="94" height="48" rx="8" fill="white"/>
              <rect x="118" y="196" width="94" height="48" rx="8" stroke="#9EB2F3" stroke-width="2"/>
              <line x1="165" y1="199" x2="165" y2="241" stroke="#D7DDF7" stroke-width="2"/>
              <!-- hands -->
              <circle cx="121" cy="216" r="8" fill="#FFD8B5"/>
              <circle cx="209" cy="216" r="8" fill="#FFD8B5"/>
              <!-- head -->
              <circle cx="167" cy="118" r="36" fill="#FFD8B5"/>
              <!-- hair -->
              <path d="M131 118 Q131 81 167 80 Q203 81 203 118 Q203 96 194 91 Q186 80 167 80 Q145 80 138 94 Q131 101 131 118 Z" fill="#2B1C12"/>
              <!-- ears -->
              <circle cx="132" cy="121" r="6" fill="#FFD8B5"/>
              <circle cx="202" cy="121" r="6" fill="#FFD8B5"/>
              <!-- face -->
              <circle cx="153" cy="121" r="4.5" fill="#2B1C12"/>
              <circle cx="180" cy="121" r="4.5" fill="#2B1C12"/>
              <circle cx="154.5" cy="119.5" r="1.5" fill="white"/>
              <circle cx="181.5" cy="119.5" r="1.5" fill="white"/>
              <path d="M156 138 Q167 146 178 138" stroke="#D27A65" stroke-width="2.3" stroke-linecap="round" fill="none"/>
              <circle cx="147" cy="132" r="5.5" fill="#F8A5A5" opacity="0.5"/>
              <circle cx="187" cy="132" r="5.5" fill="#F8A5A5" opacity="0.5"/>

              <!-- middle boy -->
              <ellipse cx="350" cy="305" rx="85" ry="18" fill="#D6DEF5"/>
              <rect x="323" y="235" width="18" height="60" rx="9" fill="#5E6786"/>
              <rect x="350" y="235" width="18" height="60" rx="9" fill="#5E6786"/>
              <ellipse cx="332" cy="300" rx="14" ry="7" fill="#1C2340"/>
              <ellipse cx="359" cy="300" rx="14" ry="7" fill="#1C2340"/>

              <rect x="301" y="162" width="90" height="84" rx="26" fill="#D9E2FF"/>
              <path d="M301 179 Q346 143 391 179 L382 246 L310 246 Z" fill="#2B3A67"/>
              <rect x="333" y="176" width="28" height="53" rx="8" fill="white"/>
              <path d="M346 181 L353 181 L349 205 Z" fill="#C94A4A"/>
              <path d="M349 205 L355 225 L343 225 Z" fill="#C94A4A"/>

              <rect x="303" y="194" width="87" height="50" rx="8" fill="#FFFDF8"/>
              <rect x="303" y="194" width="87" height="50" rx="8" stroke="#E7C98B" stroke-width="2"/>
              <line x1="346.5" y1="197" x2="346.5" y2="241" stroke="#EEDCB0" stroke-width="2"/>

              <circle cx="306" cy="216" r="8" fill="#FFD8B5"/>
              <circle cx="388" cy="216" r="8" fill="#FFD8B5"/>

              <circle cx="346" cy="118" r="38" fill="#FFD8B5"/>
              <path d="M308 119 Q308 82 346 80 Q384 82 384 119 Q384 102 377 95 Q372 82 346 80 Q320 82 315 96 Q308 101 308 119 Z" fill="#1F1712"/>
              <circle cx="330" cy="121" r="4.8" fill="#1F1712"/>
              <circle cx="360" cy="121" r="4.8" fill="#1F1712"/>
              <circle cx="331.5" cy="119.5" r="1.6" fill="white"/>
              <circle cx="361.5" cy="119.5" r="1.6" fill="white"/>
              <path d="M334 139 Q346 150 358 139" stroke="#D27A65" stroke-width="2.4" stroke-linecap="round" fill="none"/>
              <circle cx="323" cy="132" r="5.8" fill="#F8A5A5" opacity="0.5"/>
              <circle cx="369" cy="132" r="5.8" fill="#F8A5A5" opacity="0.5"/>

              <!-- right boy -->
              <ellipse cx="525" cy="305" rx="75" ry="18" fill="#D6DEF5"/>
              <rect x="492" y="235" width="18" height="60" rx="9" fill="#5E6786"/>
              <rect x="517" y="235" width="18" height="60" rx="9" fill="#5E6786"/>
              <ellipse cx="501" cy="300" rx="14" ry="7" fill="#1C2340"/>
              <ellipse cx="526" cy="300" rx="14" ry="7" fill="#1C2340"/>

              <rect x="474" y="160" width="78" height="85" rx="24" fill="#CFD8F6"/>
              <path d="M474 178 Q513 145 552 178 L544 244 L482 244 Z" fill="#24335D"/>
              <rect x="498" y="174" width="30" height="56" rx="8" fill="white"/>
              <path d="M513 180 L520 180 L517 204 Z" fill="#4256A6"/>
              <path d="M517 204 L523 225 L511 225 Z" fill="#4256A6"/>

              <rect x="468" y="192" width="92" height="50" rx="8" fill="#FFFFFF"/>
              <rect x="468" y="192" width="92" height="50" rx="8" stroke="#9EB2F3" stroke-width="2"/>
              <line x1="514" y1="195" x2="514" y2="239" stroke="#D7DDF7" stroke-width="2"/>

              <circle cx="471" cy="214" r="8" fill="#FFD8B5"/>
              <circle cx="557" cy="214" r="8" fill="#FFD8B5"/>

              <circle cx="513" cy="118" r="36" fill="#FFD8B5"/>
              <path d="M477 118 Q477 84 513 82 Q549 84 549 118 Q549 103 543 97 Q540 84 513 82 Q490 84 484 96 Q477 102 477 118 Z" fill="#35261B"/>
              <path d="M494 121 Q498 116 502 121" stroke="#2B1C12" stroke-width="2.4" stroke-linecap="round"/>
              <path d="M520 121 Q524 116 528 121" stroke="#2B1C12" stroke-width="2.4" stroke-linecap="round"/>
              <path d="M503 139 Q513 146 523 139" stroke="#D27A65" stroke-width="2.3" stroke-linecap="round" fill="none"/>
              <circle cx="494" cy="132" r="5.5" fill="#F8A5A5" opacity="0.5"/>
              <circle cx="532" cy="132" r="5.5" fill="#F8A5A5" opacity="0.5"/>

              <!-- decorations -->
              <text x="88" y="118" font-size="18" fill="#8EB4FF">✦</text>
              <text x="590" y="95" font-size="18" fill="#F2B6A7">✦</text>
              <text x="600" y="235" font-size="14" fill="#F0CF6A">★</text>
              <text x="105" y="220" font-size="14" fill="#7EB8F7">★</text>
            </svg>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="home-note">Choose a learning activity below.</div>',
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)

        with c1:
            if st.button("Go to Word", use_container_width=True):
                st.session_state["menu"] = "Word"
                st.rerun()

        with c2:
            if st.button("Go to Reading", use_container_width=True):
                st.session_state["menu"] = "Reading"
                st.rerun()


if st.session_state["menu"] == "Home":
    show_home()

elif st.session_state["menu"] == "Word":
    flip_recall.render(st.session_state.get("student_id", ""))

elif st.session_state["menu"] == "Reading":
    text_spotlight.render(st.session_state.get("student_id", ""))

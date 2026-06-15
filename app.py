"""
app.py — 진입 홈 화면
사이드바: pages/ 폴더에서 Overview / Word / Reading 자동 생성
"""
import streamlit as st
import db

st.set_page_config(
    page_title="Daea High School · 1학년 영어",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)
db.init_db()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp { background: #F0F4FF; }
section[data-testid="stSidebar"] { background: #1C2340; }
section[data-testid="stSidebar"] * { color: #C8CFEE !important; }
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {
    border-radius: 8px; margin: 2px 0; padding: 8px 14px; font-size: 15px; font-weight: 600;
}
section[data-testid="stSidebar"] a[aria-current="page"] {
    background: #2E3A6E !important; color: #fff !important;
}

.home-wrap {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    min-height: 80vh; text-align: center; padding: 2rem;
}
.home-school {
    font-size: 13px; font-weight: 700; letter-spacing: .14em;
    color: #8FA8E8; text-transform: uppercase; margin-bottom: 14px;
}
.home-title {
    font-size: 3rem; font-weight: 800; color: #1C2340;
    line-height: 1.25; margin-bottom: 6px;
}
.home-title span { color: #3D5291; }
.home-sub {
    font-size: 16px; color: #5A6A8A; margin-bottom: 32px; line-height: 1.7;
}
.home-nav {
    display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; margin-top: 8px;
}
.home-nav-card {
    background: white; border: 1px solid #E0E8FF; border-radius: 14px;
    padding: 1.25rem 2rem; font-size: 15px; font-weight: 700; color: #1C2340;
    cursor: default; transition: box-shadow .15s;
}
.home-nav-card:hover { box-shadow: 0 4px 18px rgba(44,62,150,.12); }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    role = st.session_state.get("role", "👤 학생")
    role = st.radio("역할", ["👤 학생", "👩‍🏫 교사"],
                    index=0 if role == "👤 학생" else 1,
                    label_visibility="collapsed")
    st.session_state["role"] = role
    if role == "👤 학생":
        saved = st.session_state.get("student_name", "")
        name = st.text_input("이름", value=saved if saved != "__teacher__" else "",
                             placeholder="홍길동")
        if name:
            st.session_state["student_name"] = name.strip()
    else:
        st.session_state["student_name"] = "__teacher__"
    st.markdown("---")
    st.caption("Daea High School · 1학년 영어")

# ── 홈 본문 ────────────────────────────────────────────────────────────────
col = st.columns([1, 4, 1])[1]   # 가운데 정렬

with col:
    st.markdown('<div class="home-school">Daea High School · Grade 1</div>', unsafe_allow_html=True)
    st.markdown('<div class="home-title">1학년 <span>영어 수업</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="home-sub">단어를 익히고, 지문을 읽고, 생각을 나눕니다.<br>Learn words. Read deeper. Think together.</div>', unsafe_allow_html=True)

    # 일러스트 중앙
    st.markdown("""
    <div style="display:flex; justify-content:center; margin:1.5rem 0 2rem;">
    <svg width="480" height="260" viewBox="0 0 480 260" fill="none" xmlns="http://www.w3.org/2000/svg">
      <!-- 배경 원형 장식 -->
      <circle cx="240" cy="130" r="110" fill="#E0E8FF" opacity="0.5"/>
      <circle cx="120" cy="190" r="48" fill="#EEEDFE" opacity="0.4"/>
      <circle cx="370" cy="80" r="55" fill="#E1F5EE" opacity="0.4"/>

      <!-- ─── 왼쪽 아이: 앉아서 책 읽기 ─── -->
      <!-- 의자 등받이 -->
      <rect x="52" y="108" width="10" height="60" rx="4" fill="#B0BAD8"/>
      <!-- 의자 시트 -->
      <rect x="38" y="160" width="70" height="10" rx="4" fill="#B0BAD8"/>
      <!-- 다리 -->
      <rect x="42" y="170" width="8" height="28" rx="3" fill="#9AA5C4"/>
      <rect x="96" y="170" width="8" height="28" rx="3" fill="#9AA5C4"/>
      <!-- 몸통 -->
      <rect x="60" y="115" width="38" height="48" rx="11" fill="#F97B6B"/>
      <!-- 팔 양쪽 -->
      <rect x="42" y="122" width="20" height="11" rx="5" fill="#F97B6B"/>
      <rect x="96" y="122" width="20" height="11" rx="5" fill="#F97B6B"/>
      <!-- 책 -->
      <rect x="40" y="131" width="76" height="42" rx="7" fill="white" opacity="0.96"/>
      <rect x="40" y="131" width="76" height="42" rx="7" fill="none" stroke="#7EB8F7" stroke-width="1.5"/>
      <line x1="78" y1="133" x2="78" y2="171" stroke="#C8CFEE" stroke-width="1.5"/>
      <line x1="47" y1="142" x2="76" y2="142" stroke="#E0E8FF" stroke-width="1"/>
      <line x1="47" y1="150" x2="76" y2="150" stroke="#E0E8FF" stroke-width="1"/>
      <line x1="47" y1="158" x2="76" y2="158" stroke="#E0E8FF" stroke-width="1"/>
      <line x1="80" y1="142" x2="109" y2="142" stroke="#E0E8FF" stroke-width="1"/>
      <line x1="80" y1="150" x2="109" y2="150" stroke="#E0E8FF" stroke-width="1"/>
      <line x1="80" y1="158" x2="109" y2="158" stroke="#E0E8FF" stroke-width="1"/>
      <!-- 머리 -->
      <circle cx="79" cy="96" r="22" fill="#FDDBB4"/>
      <!-- 머리카락 -->
      <path d="M57 90 Q59 70 79 68 Q99 70 101 90 Q95 74 79 72 Q63 74 57 90Z" fill="#3D2B1F"/>
      <!-- 눈 (웃는) -->
      <path d="M70 95 Q73 92 76 95" stroke="#3D2B1F" stroke-width="1.5" stroke-linecap="round" fill="none"/>
      <path d="M82 95 Q85 92 88 95" stroke="#3D2B1F" stroke-width="1.5" stroke-linecap="round" fill="none"/>
      <!-- 미소 -->
      <path d="M73 102 Q79 107 85 102" stroke="#C87941" stroke-width="1.5" stroke-linecap="round" fill="none"/>

      <!-- ─── 가운데 아이: 서서 손들기 ─── -->
      <!-- 몸통 -->
      <rect x="210" y="118" width="40" height="56" rx="11" fill="#FFD166"/>
      <!-- 다리 -->
      <rect x="212" y="170" width="15" height="28" rx="5" fill="#E8B84B"/>
      <rect x="233" y="170" width="15" height="28" rx="5" fill="#E8B84B"/>
      <!-- 신발 -->
      <ellipse cx="219" cy="199" rx="10" ry="5" fill="#1C2340"/>
      <ellipse cx="241" cy="199" rx="10" ry="5" fill="#1C2340"/>
      <!-- 팔 왼(위로) -->
      <path d="M210 128 Q188 110 182 88" stroke="#FFD166" stroke-width="13" stroke-linecap="round" fill="none"/>
      <!-- 팔 오른(옆으로) -->
      <path d="M250 132 Q272 128 278 118" stroke="#FFD166" stroke-width="13" stroke-linecap="round" fill="none"/>
      <!-- 손 왼 -->
      <circle cx="180" cy="84" r="9" fill="#FDDBB4"/>
      <!-- 손 오른 -->
      <circle cx="280" cy="116" r="9" fill="#FDDBB4"/>
      <!-- 머리 -->
      <circle cx="230" cy="100" r="24" fill="#FDDBB4"/>
      <!-- 머리카락 -->
      <path d="M206 95 Q208 72 230 70 Q252 72 254 95 Q248 76 230 74 Q212 76 206 95Z" fill="#1A0F0A"/>
      <!-- 눈 (크게) -->
      <circle cx="222" cy="98" r="3.5" fill="#3D2B1F"/>
      <circle cx="238" cy="98" r="3.5" fill="#3D2B1F"/>
      <circle cx="223.5" cy="96.5" r="1.2" fill="white"/>
      <circle cx="239.5" cy="96.5" r="1.2" fill="white"/>
      <!-- 신나는 미소 -->
      <path d="M221 107 Q230 115 239 107" stroke="#C87941" stroke-width="2" stroke-linecap="round" fill="none"/>
      <!-- 전구 (아이디어) -->
      <circle cx="230" cy="56" r="18" fill="#FFE066" opacity="0.95"/>
      <rect x="225" y="72" width="10" height="5" rx="2" fill="#E8B84B"/>
      <text x="222" y="62" font-size="13" font-weight="800" fill="#1C2340">!</text>
      <line x1="230" y1="33" x2="230" y2="27" stroke="#FFD166" stroke-width="2" stroke-linecap="round"/>
      <line x1="247" y1="40" x2="252" y2="35" stroke="#FFD166" stroke-width="2" stroke-linecap="round"/>
      <line x1="213" y1="40" x2="208" y2="35" stroke="#FFD166" stroke-width="2" stroke-linecap="round"/>

      <!-- ─── 오른쪽 아이: 태블릿 들고 태깅 ─── -->
      <!-- 몸통 -->
      <rect x="336" y="110" width="40" height="54" rx="11" fill="#5BC8AF"/>
      <!-- 다리 -->
      <rect x="338" y="160" width="15" height="30" rx="5" fill="#3DA08A"/>
      <rect x="359" y="160" width="15" height="30" rx="5" fill="#3DA08A"/>
      <!-- 신발 -->
      <ellipse cx="345" cy="191" rx="10" ry="5" fill="#1C2340"/>
      <ellipse cx="367" cy="191" rx="10" ry="5" fill="#1C2340"/>
      <!-- 팔 양쪽 (태블릿 들기) -->
      <path d="M336 124 Q318 132 312 148" stroke="#5BC8AF" stroke-width="13" stroke-linecap="round" fill="none"/>
      <path d="M376 124 Q390 130 396 146" stroke="#5BC8AF" stroke-width="13" stroke-linecap="round" fill="none"/>
      <!-- 태블릿 -->
      <rect x="306" y="144" width="96" height="62" rx="8" fill="white" opacity="0.97"/>
      <rect x="306" y="144" width="96" height="62" rx="8" fill="none" stroke="#7EB8F7" stroke-width="1.5"/>
      <!-- 태블릿 화면: 히트맵 느낌 -->
      <rect x="314" y="152" width="76" height="8" rx="3" fill="#FAEEDA"/>
      <rect x="314" y="163" width="76" height="8" rx="3" fill="#E1F5EE"/>
      <rect x="314" y="174" width="76" height="8" rx="3" fill="#FCEBEB"/>
      <rect x="314" y="185" width="50" height="8" rx="3" fill="#EEEDFE"/>
      <!-- 태그 chip들 -->
      <rect x="314" y="152" width="28" height="8" rx="3" fill="#FAEEDA" opacity="0"/>
      <text x="316" y="159" font-size="7" fill="#633806" font-weight="700">📍 Main idea</text>
      <text x="316" y="170" font-size="7" fill="#085041" font-weight="700">🔍 Evidence</text>
      <text x="316" y="181" font-size="7" fill="#A32D2D" font-weight="700">❓ Confusing</text>
      <text x="316" y="192" font-size="7" fill="#3C3489" font-weight="700">✏️ Grammar</text>
      <!-- 손 -->
      <circle cx="310" cy="148" r="8" fill="#FDDBB4"/>
      <circle cx="402" cy="148" r="8" fill="#FDDBB4"/>
      <!-- 머리 -->
      <circle cx="356" cy="92" r="22" fill="#FDDBB4"/>
      <!-- 머리카락 -->
      <path d="M334 87 Q336 67 356 65 Q376 67 378 87 Q372 70 356 68 Q340 70 334 87Z" fill="#5C3317"/>
      <!-- 눈 -->
      <path d="M347 91 Q350 88 353 91" stroke="#3D2B1F" stroke-width="1.5" stroke-linecap="round" fill="none"/>
      <path d="M359 91 Q362 88 365 91" stroke="#3D2B1F" stroke-width="1.5" stroke-linecap="round" fill="none"/>
      <!-- 집중하는 표정 -->
      <path d="M350 99 Q356 103 362 99" stroke="#C87941" stroke-width="1.5" stroke-linecap="round" fill="none"/>

      <!-- ── 바닥 라인 ── -->
      <rect x="30" y="200" width="420" height="6" rx="3" fill="#B0BAD8" opacity="0.5"/>

      <!-- ── 별 장식 ── -->
      <text x="28" y="80" font-size="18" fill="#FFD166" opacity="0.75">✦</text>
      <text x="440" y="100" font-size="14" fill="#7EB8F7" opacity="0.7">✦</text>
      <text x="155" y="50" font-size="10" fill="#5BC8AF" opacity="0.7">★</text>
      <text x="400" y="210" font-size="10" fill="#FFD166" opacity="0.6">★</text>
    </svg>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="home-nav">
      <div class="home-nav-card">📋 Overview →</div>
      <div class="home-nav-card">🗂 Word →</div>
      <div class="home-nav-card">📖 Reading →</div>
    </div>
    <div style="font-size:13px; color:#8FA8E8; margin-top:16px;">
      👈 사이드바에서 페이지를 선택하세요
    </div>
    """, unsafe_allow_html=True)

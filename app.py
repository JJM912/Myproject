"""
app.py — Home 화면
사이드바: pages/ 폴더에서 Overview / Word / Reading 자동 생성
"""
import streamlit as st
import db

st.set_page_config(
    page_title="Daea High School · English",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)
db.init_db()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp { background: #F0F4FF; }
section[data-testid="stSidebar"] { background: #1C2340; }
section[data-testid="stSidebar"] * { color: #C8CFEE !important; }
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {
    border-radius: 8px; margin: 2px 0; padding: 8px 14px; font-size: 15px; font-weight: 700;
}
section[data-testid="stSidebar"] a[aria-current="page"] {
    background: #2E3A6E !important; color: #fff !important;
}

.home-school {
    font-size: 14px; font-weight: 800; letter-spacing: .16em;
    color: #3D5291; text-transform: uppercase; margin-bottom: 18px; text-align:center;
}
.home-title-en {
    font-size: 3.2rem; font-weight: 900; color: #1C2340;
    line-height: 1.15; text-align:center; margin-bottom: 6px;
}
.home-title-en span { color: #3D5291; }
.home-title-kr {
    font-size: 1.1rem; font-weight: 700; color: #5A6A8A;
    text-align:center; margin-bottom: 28px;
}
.home-nav {
    display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; margin-top: 10px;
}
.home-nav-card {
    background: white; border: 1px solid #E0E8FF; border-radius: 14px;
    padding: 1.1rem 2rem; font-size: 15px; font-weight: 800; color: #1C2340;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    name = st.text_input("이름", value=st.session_state.get("student_name", ""),
                         placeholder="홍길동")
    if name:
        st.session_state["student_name"] = name.strip()
    st.markdown("---")
    st.caption("Daea High School · Grade 1 English")

# ── 홈 본문 (가운데 정렬) ───────────────────────────────────────────────────
_, center, _ = st.columns([1, 3, 1])
with center:
    st.markdown('<div class="home-school">Daea High School</div>', unsafe_allow_html=True)
    st.markdown('<div class="home-title-en">Grade 1 <span>English Class</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="home-title-kr">대아고등학교 1학년 영어 수업</div>', unsafe_allow_html=True)

    # ── 귀여운 아이들 일러스트 (둥글둥글한 비율) ──
    st.markdown("""
    <div style="display:flex; justify-content:center; margin:1rem 0 2rem;">
    <svg width="460" height="280" viewBox="0 0 460 280" fill="none" xmlns="http://www.w3.org/2000/svg">
      <!-- 배경 장식 -->
      <circle cx="230" cy="140" r="115" fill="#E3E9FF" opacity="0.6"/>
      <circle cx="105" cy="200" r="46" fill="#FCE8E0" opacity="0.55"/>
      <circle cx="360" cy="95" r="52" fill="#DDF3EC" opacity="0.6"/>
      <circle cx="380" cy="200" r="30" fill="#FFF1CC" opacity="0.6"/>

      <!-- ════ 왼쪽 아이: 앉아서 책 읽기 (분홍 후드) ════ -->
      <!-- 다리 -->
      <ellipse cx="108" cy="232" rx="13" ry="9" fill="#F4A896"/>
      <ellipse cx="134" cy="232" rx="13" ry="9" fill="#F4A896"/>
      <!-- 몸통 (통통하게) -->
      <ellipse cx="121" cy="190" rx="34" ry="32" fill="#F98E8E"/>
      <!-- 책 (큰 사이즈) -->
      <rect x="86" y="180" width="70" height="44" rx="8" fill="white"/>
      <rect x="86" y="180" width="70" height="44" rx="8" fill="none" stroke="#7EB8F7" stroke-width="2"/>
      <line x1="121" y1="182" x2="121" y2="222" stroke="#C8CFEE" stroke-width="2"/>
      <line x1="94" y1="192" x2="117" y2="192" stroke="#E0E8FF" stroke-width="1.5"/>
      <line x1="94" y1="200" x2="117" y2="200" stroke="#E0E8FF" stroke-width="1.5"/>
      <line x1="94" y1="208" x2="117" y2="208" stroke="#E0E8FF" stroke-width="1.5"/>
      <line x1="125" y1="192" x2="148" y2="192" stroke="#E0E8FF" stroke-width="1.5"/>
      <line x1="125" y1="200" x2="148" y2="200" stroke="#E0E8FF" stroke-width="1.5"/>
      <line x1="125" y1="208" x2="148" y2="208" stroke="#E0E8FF" stroke-width="1.5"/>
      <!-- 손 (책 잡은) -->
      <circle cx="88" cy="200" r="8" fill="#FFD9B8"/>
      <circle cx="154" cy="200" r="8" fill="#FFD9B8"/>
      <!-- 머리 (큰 동그라미) -->
      <circle cx="121" cy="120" r="34" fill="#FFD9B8"/>
      <!-- 머리카락 (둥근 단발) -->
      <path d="M87 120 Q87 84 121 82 Q155 84 155 120 Q155 104 148 100
               Q150 88 121 86 Q92 88 94 100 Q87 104 87 120Z" fill="#5C3A24"/>
      <path d="M87 118 Q84 130 90 138 L94 120 Z" fill="#5C3A24"/>
      <path d="M155 118 Q158 130 152 138 L148 120 Z" fill="#5C3A24"/>
      <!-- 볼터치 -->
      <circle cx="104" cy="128" r="6" fill="#FF9E9E" opacity="0.5"/>
      <circle cx="138" cy="128" r="6" fill="#FF9E9E" opacity="0.5"/>
      <!-- 눈 (큰 반짝 눈) -->
      <circle cx="110" cy="118" r="5" fill="#3D2B1F"/>
      <circle cx="132" cy="118" r="5" fill="#3D2B1F"/>
      <circle cx="111.5" cy="116" r="1.7" fill="white"/>
      <circle cx="133.5" cy="116" r="1.7" fill="white"/>
      <!-- 활짝 웃는 입 -->
      <path d="M112 130 Q121 138 130 130" stroke="#D9755B" stroke-width="2.2" stroke-linecap="round" fill="none"/>

      <!-- ════ 가운데 아이: 손들고 신남 (노란 티) ════ -->
      <!-- 다리 -->
      <rect x="212" y="218" width="16" height="30" rx="8" fill="#5BB89E"/>
      <rect x="232" y="218" width="16" height="30" rx="8" fill="#5BB89E"/>
      <ellipse cx="220" cy="250" rx="11" ry="6" fill="#2E3A6E"/>
      <ellipse cx="240" cy="250" rx="11" ry="6" fill="#2E3A6E"/>
      <!-- 몸통 (통통) -->
      <ellipse cx="230" cy="190" rx="33" ry="33" fill="#FFD166"/>
      <!-- 팔 왼(위로 번쩍) -->
      <path d="M205 178 Q183 158 178 134" stroke="#FFD166" stroke-width="15" stroke-linecap="round" fill="none"/>
      <circle cx="177" cy="129" r="9" fill="#FFD9B8"/>
      <!-- 팔 오른(아래) -->
      <path d="M255 182 Q272 184 276 198" stroke="#FFD166" stroke-width="15" stroke-linecap="round" fill="none"/>
      <circle cx="277" cy="201" r="9" fill="#FFD9B8"/>
      <!-- 머리 -->
      <circle cx="230" cy="120" r="36" fill="#FFD9B8"/>
      <!-- 머리카락 (짧은 곱슬) -->
      <path d="M194 120 Q194 82 230 80 Q266 82 266 120 Q266 100 258 96
               Q260 84 230 82 Q200 84 202 96 Q194 100 194 120Z" fill="#2A1A10"/>
      <circle cx="200" cy="104" r="7" fill="#2A1A10"/>
      <circle cx="216" cy="92" r="8" fill="#2A1A10"/>
      <circle cx="244" cy="92" r="8" fill="#2A1A10"/>
      <circle cx="260" cy="104" r="7" fill="#2A1A10"/>
      <!-- 볼터치 -->
      <circle cx="211" cy="128" r="6.5" fill="#FF9E9E" opacity="0.5"/>
      <circle cx="249" cy="128" r="6.5" fill="#FF9E9E" opacity="0.5"/>
      <!-- 눈 (크게 반짝) -->
      <circle cx="217" cy="118" r="5.5" fill="#3D2B1F"/>
      <circle cx="243" cy="118" r="5.5" fill="#3D2B1F"/>
      <circle cx="218.5" cy="115.5" r="2" fill="white"/>
      <circle cx="244.5" cy="115.5" r="2" fill="white"/>
      <!-- 신난 입 (벌린 미소) -->
      <path d="M218 130 Q230 142 242 130 Q230 137 218 130Z" fill="#D9755B"/>
      <!-- 전구 (아이디어!) -->
      <circle cx="177" cy="105" r="15" fill="#FFE680"/>
      <rect x="172" y="118" width="10" height="5" rx="2" fill="#E8B84B"/>
      <text x="173" y="111" font-size="13" font-weight="900" fill="#1C2340">!</text>
      <line x1="177" y1="86" x2="177" y2="80" stroke="#FFD166" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="191" y1="92" x2="196" y2="87" stroke="#FFD166" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="163" y1="92" x2="158" y2="87" stroke="#FFD166" stroke-width="2.5" stroke-linecap="round"/>

      <!-- ════ 오른쪽 아이: 책 안고 방긋 (민트 티) ════ -->
      <!-- 다리 -->
      <rect x="332" y="222" width="15" height="28" rx="7" fill="#4A8FD4"/>
      <rect x="351" y="222" width="15" height="28" rx="7" fill="#4A8FD4"/>
      <ellipse cx="339" cy="252" rx="10" ry="6" fill="#2E3A6E"/>
      <ellipse cx="358" cy="252" rx="10" ry="6" fill="#2E3A6E"/>
      <!-- 몸통 -->
      <ellipse cx="349" cy="195" rx="32" ry="31" fill="#5BC8D8"/>
      <!-- 책 (가슴에 안음) -->
      <rect x="324" y="186" width="50" height="36" rx="6" fill="white"/>
      <rect x="324" y="186" width="50" height="36" rx="6" fill="none" stroke="#7EB8F7" stroke-width="2"/>
      <line x1="349" y1="188" x2="349" y2="220" stroke="#C8CFEE" stroke-width="1.5"/>
      <!-- 팔 (책 감싼) -->
      <path d="M322 188 Q314 200 320 214" stroke="#5BC8D8" stroke-width="13" stroke-linecap="round" fill="none"/>
      <path d="M376 188 Q384 200 378 214" stroke="#5BC8D8" stroke-width="13" stroke-linecap="round" fill="none"/>
      <!-- 머리 -->
      <circle cx="349" cy="125" r="33" fill="#FFD9B8"/>
      <!-- 머리카락 (옆가르마 단정) -->
      <path d="M316 125 Q316 90 349 88 Q382 90 382 125 Q382 106 374 102
               Q376 92 349 90 Q330 91 326 100 Q318 104 316 125Z" fill="#4A2F1A"/>
      <!-- 볼터치 -->
      <circle cx="333" cy="132" r="6" fill="#FF9E9E" opacity="0.5"/>
      <circle cx="365" cy="132" r="6" fill="#FF9E9E" opacity="0.5"/>
      <!-- 눈 (방긋 호선) -->
      <path d="M337 122 Q341 117 345 122" stroke="#3D2B1F" stroke-width="2.5" stroke-linecap="round" fill="none"/>
      <path d="M353 122 Q357 117 361 122" stroke="#3D2B1F" stroke-width="2.5" stroke-linecap="round" fill="none"/>
      <!-- 미소 -->
      <path d="M341 134 Q349 141 357 134" stroke="#D9755B" stroke-width="2.2" stroke-linecap="round" fill="none"/>

      <!-- ── 바닥 ── -->
      <rect x="60" y="246" width="340" height="7" rx="3.5" fill="#C4CDEC" opacity="0.55"/>

      <!-- ── 별 장식 ── -->
      <text x="50" y="90" font-size="20" fill="#FFD166" opacity="0.8">✦</text>
      <text x="408" y="120" font-size="16" fill="#7EB8F7" opacity="0.75">✦</text>
      <text x="70" y="160" font-size="11" fill="#5BC8D8" opacity="0.7">★</text>
      <text x="400" y="240" font-size="12" fill="#FFD166" opacity="0.65">★</text>
      <text x="300" y="60" font-size="13" fill="#F98E8E" opacity="0.6">♥</text>
    </svg>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="home-nav">
      <div class="home-nav-card">📋 Overview</div>
      <div class="home-nav-card">🗂 Word</div>
      <div class="home-nav-card">📖 Reading</div>
    </div>
    <div style="font-size:13px; color:#8FA8E8; margin-top:18px; text-align:center;">
      👈 왼쪽 메뉴에서 페이지를 선택하세요
    </div>
    """, unsafe_allow_html=True)

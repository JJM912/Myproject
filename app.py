"""
app.py — English Class Tools (단일 파일 진입점)

실행:
    pip install streamlit
    streamlit run app.py

학생 접속: 교사 컴퓨터와 같은 와이파이에서
    http://<교사컴퓨터IP>:8501
"""
import streamlit as st
import db
import flip_recall
import text_spotlight

st.set_page_config(
    page_title="English Class Tools",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()

# ── 전역 스타일 ────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .stApp { background: #f4f5f7; }
  section[data-testid="stSidebar"] { background: #1e1f2e; }
  section[data-testid="stSidebar"] * { color: #e0e0f0 !important; }
  section[data-testid="stSidebar"] .stRadio label { font-size: 15px; }
  div[data-testid="stExpander"] { background: white; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── 사이드바 ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 English Class")
    st.markdown("---")

    page = st.radio(
        "메뉴",
        ["🏠 Home", "🗂 Word", "📖 Reading"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    role = st.radio("역할", ["👤 학생", "👩‍🏫 교사"])

    student_name = ""
    if role == "👤 학생":
        student_name = st.text_input("이름", placeholder="홍길동")

    st.markdown("---")
    st.caption("고1 영어 수업 · 교사 주도")

is_teacher = (role == "👩‍🏫 교사")

# ══════════════════════════════════════════════════════════════════════════
# 🏠  HOME
# ══════════════════════════════════════════════════════════════════════════
if page == "🏠 Home":
    # 제목 + 설명을 메인 영역과 우측 컬럼으로 분리
    main_col, side_col = st.columns([3, 2], gap="large")

    with main_col:
        st.markdown("# 📚 English Class Tools")
        st.markdown("#### 고등학교 1학년 영어 수업 보조 앱")
        st.markdown("---")

        st.markdown("""
        이 앱은 수업 시간에 교사와 학생이 **같은 화면을 함께 보며** 활동할 수 있도록
        설계된 영어 학습 도구입니다.

        사이드바에서 **Word** 또는 **Reading** 을 선택해 활동을 시작하세요.
        """)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div style="background:white; border-radius:12px; padding:1.25rem 1.5rem;
                        border-left:4px solid #3C3489;">
              <div style="font-size:18px; font-weight:600; color:#3C3489; margin-bottom:6px;">
                🗂 Word — Flip & Recall
              </div>
              <div style="font-size:13px; color:#555; line-height:1.7;">
                교사가 단어 카드를 제어하고<br>
                학생은 개별 자기평가를 합니다.<br>
                <br>
                ✅ 알았어 / 🤔 헷갈렸어 / ❌ 몰랐어<br>
                교사 화면에 실시간 집계 표시
              </div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div style="background:white; border-radius:12px; padding:1.25rem 1.5rem;
                        border-left:4px solid #085041;">
              <div style="font-size:18px; font-weight:600; color:#085041; margin-bottom:6px;">
                📖 Reading — Text Spotlight
              </div>
              <div style="font-size:13px; color:#555; line-height:1.7;">
                지문을 읽으며 태그를 달고<br>
                전체 제출 후 히트맵 공개.<br>
                <br>
                📍 글의 주제 / 🔍 날개 문제 근거<br>
                ✏️ 문법·구조 / ❓ 이해 안 됨
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**수업 흐름**")
        flow_cols = st.columns(4)
        steps = [
            ("1", "#3C3489", "Word 활동", "어휘 카드로\n수업 워밍업 (10분)"),
            ("2", "#085041", "Reading 활동", "지문 읽고\n개별 태깅 (10분)"),
            ("3", "#633806", "히트맵 공개", "전체 결과\n함께 확인"),
            ("4", "#A32D2D", "토론", "히트맵 기반\n교사 주도 토론"),
        ]
        for col, (num, color, title, desc) in zip(flow_cols, steps):
            col.markdown(f"""
            <div style="background:white; border-radius:10px; padding:1rem; text-align:center;">
              <div style="font-size:1.5rem; font-weight:700; color:{color};">{num}</div>
              <div style="font-size:13px; font-weight:600; color:{color}; margin:4px 0;">{title}</div>
              <div style="font-size:12px; color:#888; white-space:pre-line;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── 우측 날개: Overview ────────────────────────────────────────────
    with side_col:
        st.markdown("""
        <div style="background:white; border-radius:14px; padding:1.5rem;
                    border:1px solid #e0e0e0; position:sticky; top:1rem;">
          <div style="font-size:16px; font-weight:600; color:#1e1f2e; margin-bottom:12px;">
            📋 Overview — 학습 체계
          </div>

          <div style="font-size:13px; color:#444; line-height:1.75;">

            <b style="color:#3C3489;">🗂 Word (어휘)</b><br>
            교사가 수업 전 핵심 단어 10~15개를 등록합니다.
            카드 앞면(단어)을 보며 학생이 먼저 뜻을 떠올리고,
            교사가 뒤집으면 정답(뜻+예문)이 공개됩니다.
            학생은 <b>알았어 / 헷갈렸어 / 몰랐어</b>로 자기평가하고,
            교사는 실시간 집계를 보며 설명 깊이를 조율합니다.
            수업 후 <b>"몰랐어"</b> 단어가 자동으로 집계되어
            개인 복습 재료로 활용됩니다.

            <div style="margin:12px 0; border-top:1px solid #eee;"></div>

            <b style="color:#085041;">📖 Reading (독해)</b><br>
            교사가 교과서 본문과 날개 문제를 등록합니다.
            학생은 각 문장을 읽으며 4가지 태그를 달고
            자유 메모를 남깁니다.<br><br>

            <span style="background:#FAEEDA; color:#633806; padding:2px 8px;
              border-radius:20px; font-size:12px; font-weight:600;">📍 글의 주제</span>
            지문 전체를 대표하는 문장<br><br>

            <span style="background:#E1F5EE; color:#085041; padding:2px 8px;
              border-radius:20px; font-size:12px; font-weight:600;">🔍 날개 문제 근거</span>
            날개 문제 답의 근거 문장<br><br>

            <span style="background:#EEEDFE; color:#3C3489; padding:2px 8px;
              border-radius:20px; font-size:12px; font-weight:600;">✏️ 문법·구조</span>
            특이한 문법 포인트가 있는 문장<br><br>

            <span style="background:#FCEBEB; color:#A32D2D; padding:2px 8px;
              border-radius:20px; font-size:12px; font-weight:600;">❓ 이해 안 됨</span>
            뜻이나 내용이 이해되지 않는 문장<br><br>

            태깅 중에는 다른 학생의 선택이 숨겨져
            <b>쏠림 없이 독립적으로 판단</b>합니다.
            교사가 공개 버튼을 누르면 <b>히트맵이 모든 화면에
            동시에 표시</b>되어 함께 보며 토론합니다.

            <div style="margin:12px 0; border-top:1px solid #eee;"></div>

            <b style="color:#555;">두 앱의 연결</b><br>
            Reading에서 <b>"이해 안 됨"</b>으로 태그된 단어가
            다음 차시 Word 활동의 단어 재료가 됩니다.
            수업이 쌓일수록 학생 맞춤 어휘 학습이 완성됩니다.

          </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# 🗂 WORD
# ══════════════════════════════════════════════════════════════════════════
elif page == "🗂 Word":
    if is_teacher:
        flip_recall.teacher_view()
    else:
        if student_name.strip():
            flip_recall.student_view(student_name.strip())
        else:
            st.info("👈 사이드바에서 이름을 입력하세요.")

# ══════════════════════════════════════════════════════════════════════════
# 📖 READING
# ══════════════════════════════════════════════════════════════════════════
elif page == "📖 Reading":
    if is_teacher:
        text_spotlight.teacher_view()
    else:
        if student_name.strip():
            text_spotlight.student_view(student_name.strip())
        else:
            st.info("👈 사이드바에서 이름을 입력하세요.")

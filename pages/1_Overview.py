"""
pages/1_Overview.py
이 앱으로 무엇을 배울 수 있는지 영어+그림으로 소개하는 Overview 페이지
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Overview", page_icon="📋", layout="wide")

SIDEBAR_STYLE = """
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
</style>
"""
st.markdown(SIDEBAR_STYLE, unsafe_allow_html=True)

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

# ══════════════════════════════════════════════════════════════════════
# OVERVIEW 본문
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
.ov-section { margin-bottom: 2.5rem; }

/* ── 헤더 배너 ── */
.ov-banner {
    background: linear-gradient(135deg, #1C2340 0%, #2E3A6E 60%, #3D5291 100%);
    border-radius: 18px;
    padding: 2.5rem 3rem;
    display: flex;
    align-items: center;
    gap: 2.5rem;
    margin-bottom: 2rem;
}
.ov-banner-text { flex: 1; }
.ov-eyebrow {
    font-size: 12px; font-weight: 700; letter-spacing: .12em;
    color: #8FA8E8; text-transform: uppercase; margin-bottom: 8px;
}
.ov-h1 { font-size: 2rem; font-weight: 800; color: #fff; line-height: 1.3; margin-bottom: 10px; }
.ov-h1 span { color: #7EB8F7; }
.ov-lead { font-size: 14px; color: #A8BFEE; line-height: 1.75; }

/* ── What You'll Learn 카드 ── */
.learn-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 2rem;
}
.learn-card {
    background: white; border-radius: 14px; padding: 1.4rem 1.5rem;
    border: 1px solid #E0E8FF;
}
.learn-icon { font-size: 2rem; margin-bottom: 10px; }
.learn-en { font-size: 15px; font-weight: 700; color: #1C2340; margin-bottom: 4px; }
.learn-kr { font-size: 12px; color: #8FA8E8; font-weight: 600; margin-bottom: 8px; }
.learn-desc { font-size: 13px; color: #5A6A8A; line-height: 1.7; }

/* ── 앱 소개 2칸 ── */
.app-pair { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 2rem; }
.app-block {
    background: white; border-radius: 14px; padding: 1.5rem 1.75rem;
    border: 1px solid #E0E8FF;
}
.app-block-header {
    display: flex; align-items: center; gap: 12px; margin-bottom: 14px;
    padding-bottom: 12px; border-bottom: 1px solid #E0E8FF;
}
.app-block-icon {
    width: 42px; height: 42px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0;
}
.app-block-title { font-size: 16px; font-weight: 700; color: #1C2340; margin: 0; }
.app-block-sub { font-size: 12px; color: #8FA8E8; margin: 2px 0 0; }
.step-list { list-style: none; padding: 0; margin: 0; }
.step-list li {
    display: flex; gap: 10px; align-items: flex-start;
    font-size: 13px; color: #5A6A8A; line-height: 1.6; margin-bottom: 8px;
}
.step-dot {
    width: 20px; height: 20px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; font-weight: 700; flex-shrink: 0; margin-top: 1px;
}
.chip {
    display: inline-block; font-size: 11px; font-weight: 700;
    padding: 2px 9px; border-radius: 20px; margin: 2px 2px 0 0;
}

/* ── How It Works 타임라인 ── */
.timeline {
    background: white; border-radius: 14px; padding: 1.5rem 1.75rem;
    border: 1px solid #E0E8FF; margin-bottom: 2rem;
}
.tl-title {
    font-size: 13px; font-weight: 700; color: #8FA8E8;
    text-transform: uppercase; letter-spacing: .08em; margin-bottom: 16px;
}
.tl-row {
    display: flex; align-items: flex-start; gap: 14px; margin-bottom: 14px;
}
.tl-badge {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700; flex-shrink: 0;
}
.tl-body { flex: 1; }
.tl-name { font-size: 14px; font-weight: 700; color: #1C2340; margin-bottom: 2px; }
.tl-desc { font-size: 13px; color: #5A6A8A; line-height: 1.6; }
.tl-line {
    width: 2px; height: 14px; background: #E0E8FF;
    margin: 0 17px 0 17px;
}
</style>
""", unsafe_allow_html=True)

# ── 헤더 배너 ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="ov-banner">
  <div class="ov-banner-text">
    <div class="ov-eyebrow">Daea High School · Grade 1 English</div>
    <div class="ov-h1">Learn Words.<br><span>Read Deeper.</span><br>Think Together.</div>
    <div class="ov-lead">
      An interactive English class platform for building vocabulary,<br>
      analyzing texts, and discussing ideas as a class.
    </div>
  </div>
  <!-- SVG 일러스트: 전구 + 책 + 말풍선 -->
  <svg width="220" height="180" viewBox="0 0 220 180" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- 배경 원 -->
    <circle cx="110" cy="90" r="80" fill="#2E3A6E" opacity="0.5"/>
    <!-- 책 (펼쳐진) -->
    <rect x="40" y="90" width="62" height="48" rx="5" fill="white" opacity="0.92"/>
    <rect x="40" y="90" width="62" height="48" rx="5" fill="none" stroke="#7EB8F7" stroke-width="1.5"/>
    <line x1="71" y1="92" x2="71" y2="136" stroke="#C8CFEE" stroke-width="1.5"/>
    <line x1="47" y1="102" x2="69" y2="102" stroke="#E0E8FF" stroke-width="1"/>
    <line x1="47" y1="110" x2="69" y2="110" stroke="#E0E8FF" stroke-width="1"/>
    <line x1="47" y1="118" x2="69" y2="118" stroke="#E0E8FF" stroke-width="1"/>
    <line x1="47" y1="126" x2="69" y2="126" stroke="#E0E8FF" stroke-width="1"/>
    <line x1="73" y1="102" x2="95" y2="102" stroke="#E0E8FF" stroke-width="1"/>
    <line x1="73" y1="110" x2="95" y2="110" stroke="#E0E8FF" stroke-width="1"/>
    <line x1="73" y1="118" x2="95" y2="118" stroke="#E0E8FF" stroke-width="1"/>
    <!-- 전구 (단어 아이디어) -->
    <circle cx="155" cy="62" r="22" fill="#FFD166" opacity="0.9"/>
    <rect x="149" y="82" width="12" height="6" rx="2" fill="#E8B84B"/>
    <rect x="151" y="88" width="8" height="4" rx="2" fill="#D4A43A"/>
    <line x1="155" y1="35" x2="155" y2="28" stroke="#FFD166" stroke-width="2.5" stroke-linecap="round"/>
    <line x1="175" y1="42" x2="181" y2="36" stroke="#FFD166" stroke-width="2.5" stroke-linecap="round"/>
    <line x1="135" y1="42" x2="129" y2="36" stroke="#FFD166" stroke-width="2.5" stroke-linecap="round"/>
    <line x1="182" y1="62" x2="189" y2="62" stroke="#FFD166" stroke-width="2.5" stroke-linecap="round"/>
    <line x1="128" y1="62" x2="121" y2="62" stroke="#FFD166" stroke-width="2.5" stroke-linecap="round"/>
    <!-- 전구 안 W 글자 -->
    <text x="148" y="67" font-size="14" font-weight="800" fill="#1C2340">W</text>
    <!-- 말풍선 (토론) -->
    <rect x="110" y="112" width="72" height="34" rx="10" fill="#5BC8AF" opacity="0.9"/>
    <polygon points="118,146 110,158 130,146" fill="#5BC8AF" opacity="0.9"/>
    <line x1="120" y1="124" x2="172" y2="124" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.7"/>
    <line x1="120" y1="133" x2="165" y2="133" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.7"/>
    <!-- 별 장식 -->
    <text x="30" y="70" font-size="14" fill="#FFD166" opacity="0.7">✦</text>
    <text x="188" y="115" font-size="10" fill="#7EB8F7" opacity="0.7">✦</text>
    <text x="50" y="160" font-size="8" fill="#5BC8AF" opacity="0.6">★</text>
  </svg>
</div>
""", unsafe_allow_html=True)

# ── What You'll Learn ───────────────────────────────────────────────────────
st.markdown("""
<div class="learn-grid">

  <div class="learn-card">
    <div class="learn-icon">📖</div>
    <div class="learn-en">Vocabulary</div>
    <div class="learn-kr">어휘 학습</div>
    <div class="learn-desc">
      Flashcard-style word cards help you recall meanings actively.
      You rate your own confidence — <em>knew it / unsure / didn't know</em> —
      so revision focuses exactly where you need it.
    </div>
  </div>

  <div class="learn-card">
    <div class="learn-icon">🔍</div>
    <div class="learn-en">Reading Comprehension</div>
    <div class="learn-kr">독해 능력</div>
    <div class="learn-desc">
      Tag each sentence in a textbook passage as you read:
      identify the main idea, find evidence for questions,
      and flag grammar points or anything confusing.
    </div>
  </div>

  <div class="learn-card">
    <div class="learn-icon">💬</div>
    <div class="learn-en">Critical Discussion</div>
    <div class="learn-kr">비판적 사고 & 토론</div>
    <div class="learn-desc">
      After everyone submits, a live heatmap reveals where classmates
      agreed or differed. Use it as the starting point for
      a teacher-led discussion on the text.
    </div>
  </div>

</div>
""", unsafe_allow_html=True)

# ── 앱 소개 두 칸 ────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-pair">

  <!-- Word -->
  <div class="app-block">
    <div class="app-block-header">
      <div class="app-block-icon" style="background:#EEEDFE;">🗂</div>
      <div>
        <div class="app-block-title">Word — Flip & Recall</div>
        <div class="app-block-sub">Vocabulary · Self-Assessment · Real-time Feedback</div>
      </div>
    </div>
    <ul class="step-list">
      <li>
        <div class="step-dot" style="background:#EEEDFE; color:#3C3489;">1</div>
        <span>The teacher displays a word card on screen.</span>
      </li>
      <li>
        <div class="step-dot" style="background:#EEEDFE; color:#3C3489;">2</div>
        <span>Students silently recall the meaning during a 5-second <em>Think Time</em>.</span>
      </li>
      <li>
        <div class="step-dot" style="background:#EEEDFE; color:#3C3489;">3</div>
        <span>The card flips to reveal the meaning and example sentence.</span>
      </li>
      <li>
        <div class="step-dot" style="background:#EEEDFE; color:#3C3489;">4</div>
        <span>Each student rates privately — ✅ Knew it / 🤔 Unsure / ❌ Didn't know.</span>
      </li>
      <li>
        <div class="step-dot" style="background:#EEEDFE; color:#3C3489;">5</div>
        <span>The teacher sees live results and decides whether to explain more or move on.</span>
      </li>
    </ul>
    <div style="margin-top:12px;">
      <span class="chip" style="background:#EEEDFE; color:#3C3489;">Self-rating</span>
      <span class="chip" style="background:#E1F5EE; color:#085041;">Live tally</span>
      <span class="chip" style="background:#FAEEDA; color:#633806;">Auto review list</span>
    </div>
  </div>

  <!-- Reading -->
  <div class="app-block">
    <div class="app-block-header">
      <div class="app-block-icon" style="background:#E1F5EE;">📖</div>
      <div>
        <div class="app-block-title">Reading — Text Spotlight</div>
        <div class="app-block-sub">Tagging · Heatmap · Class Discussion</div>
      </div>
    </div>
    <ul class="step-list">
      <li>
        <div class="step-dot" style="background:#E1F5EE; color:#085041;">1</div>
        <span>The teacher uploads a textbook passage and side-note questions.</span>
      </li>
      <li>
        <div class="step-dot" style="background:#E1F5EE; color:#085041;">2</div>
        <span>Students read independently and tag each sentence using 4 categories.</span>
      </li>
      <li>
        <div class="step-dot" style="background:#E1F5EE; color:#085041;">3</div>
        <span>Tags are hidden during reading — no one influences anyone else.</span>
      </li>
      <li>
        <div class="step-dot" style="background:#E1F5EE; color:#085041;">4</div>
        <span>After everyone submits, the teacher reveals the heatmap to the whole class.</span>
      </li>
      <li>
        <div class="step-dot" style="background:#E1F5EE; color:#085041;">5</div>
        <span>Discussion flows naturally from the sentences everyone flagged most.</span>
      </li>
    </ul>
    <div style="margin-top:12px;">
      <span class="chip" style="background:#FAEEDA; color:#633806;">📍 Main idea</span>
      <span class="chip" style="background:#E1F5EE; color:#085041;">🔍 Evidence</span>
      <span class="chip" style="background:#EEEDFE; color:#3C3489;">✏️ Grammar</span>
      <span class="chip" style="background:#FCEBEB; color:#A32D2D;">❓ Confusing</span>
    </div>
  </div>

</div>
""", unsafe_allow_html=True)

# ── How It Works 타임라인 ────────────────────────────────────────────────────
st.markdown("""
<div class="timeline">
  <div class="tl-title">How a Lesson Works</div>

  <div class="tl-row">
    <div class="tl-badge" style="background:#EEEDFE; color:#3C3489;">1</div>
    <div class="tl-body">
      <div class="tl-name">🗂 Warm-up · Word Cards <span style="font-size:12px; color:#8FA8E8; font-weight:400;">~10 min</span></div>
      <div class="tl-desc">The teacher runs through 10–15 key vocabulary cards before reading. Students self-assess each word.</div>
    </div>
  </div>
  <div class="tl-line"></div>

  <div class="tl-row">
    <div class="tl-badge" style="background:#E1F5EE; color:#085041;">2</div>
    <div class="tl-body">
      <div class="tl-name">📖 Individual Reading & Tagging <span style="font-size:12px; color:#8FA8E8; font-weight:400;">~10 min</span></div>
      <div class="tl-desc">Students read the textbook passage on their device and tag sentences independently. Notes are private until submission.</div>
    </div>
  </div>
  <div class="tl-line"></div>

  <div class="tl-row">
    <div class="tl-badge" style="background:#FAEEDA; color:#633806;">3</div>
    <div class="tl-body">
      <div class="tl-name">📊 Heatmap Reveal</div>
      <div class="tl-desc">The teacher publishes results. Every student's screen shows the same heatmap — which sentences got the most tags and why.</div>
    </div>
  </div>
  <div class="tl-line"></div>

  <div class="tl-row">
    <div class="tl-badge" style="background:#FCEBEB; color:#A32D2D;">4</div>
    <div class="tl-body">
      <div class="tl-name">💬 Class Discussion</div>
      <div class="tl-desc">The teacher leads discussion starting from the most-tagged sentences. Anonymous memos are read aloud to spark conversation.</div>
    </div>
  </div>
  <div class="tl-line"></div>

  <div class="tl-row">
    <div class="tl-badge" style="background:#F0F4FF; color:#3D5291;">↻</div>
    <div class="tl-body">
      <div class="tl-name">🔄 Next Class Connection</div>
      <div class="tl-desc">Words tagged <em>"Confusing"</em> in Reading automatically become the next Word session's focus. Each lesson feeds the next.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

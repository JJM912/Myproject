"""
pages/1_Word.py — Flip & Recall 어휘 카드
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db
import flip_recall

st.set_page_config(page_title="Word · Flip & Recall", page_icon="🗂", layout="wide")
db.init_db()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp { background: #F0F4FF; }
section[data-testid="stSidebar"] { background: #1C2340; }
section[data-testid="stSidebar"] * { color: #C8CFEE !important; }
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {
    border-radius: 8px; margin: 2px 0; padding: 8px 14px;
    font-size: 15px; font-weight: 600;
}
section[data-testid="stSidebar"] a[aria-current="page"] {
    background: #2E3A6E !important; color: #fff !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    role = st.session_state.get("role", None)
    if not role:
        role = st.radio("역할", ["👤 학생", "👩‍🏫 교사"], label_visibility="collapsed")
        st.session_state["role"] = role
    else:
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

is_teacher = (st.session_state.get("role", "") == "👩‍🏫 교사")

if is_teacher:
    flip_recall.teacher_view()
else:
    sname = st.session_state.get("student_name", "")
    if sname and sname != "__teacher__":
        flip_recall.student_view(sname)
    else:
        st.info("👈 사이드바에서 이름을 입력하세요.")

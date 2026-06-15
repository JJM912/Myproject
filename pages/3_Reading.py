"""pages/3_Reading.py — Reading: Text Spotlight"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db
import text_spotlight

st.set_page_config(page_title="Reading", page_icon="📖", layout="wide")
db.init_db()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
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

text_spotlight.render(st.session_state.get("student_name", ""))

"""
text_spotlight.py — Reading: Text Spotlight
역할 구분 없이 단일 화면. 학생은 위쪽에서 태깅, 교사는 아래 '수업 설정'으로 지문 등록·공개 제어.
"""
import streamlit as st
import re
import db
from collections import defaultdict

TAGS = {
    "글의 주제":       {"color": "#633806", "bg": "#FAEEDA", "icon": "📍"},
    "날개 문제 근거":  {"color": "#085041", "bg": "#E1F5EE", "icon": "🔍"},
    "문법·구조":       {"color": "#3C3489", "bg": "#EEEDFE", "icon": "✏️"},
    "이해 안 됨":      {"color": "#A32D2D", "bg": "#FCEBEB", "icon": "❓"},
}

SAMPLE_TEXT = """When I first moved to a new school, I felt completely lost. Everyone already had their own friends, and I knew no one. During lunch, I sat alone in the corner of the cafeteria. One day, a girl named Mina came up to me and asked if I wanted to join her table. That simple act of kindness changed everything. I realized that sometimes the smallest gesture can make the biggest difference in someone's life."""

SAMPLE_QUESTIONS = [
    "Why did the writer feel lost at the new school?",
    "What lesson did the writer learn from Mina?",
]


def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def render(student_name):
    st.markdown("## 📖 Reading — Text Spotlight")

    sentences = db.ts_get_sentences()
    revealed = db.get_state("ts_state", "reveal", "false") == "true"
    sname = student_name.strip() if student_name else ""

    # ══════════════════════════════════════════════════════════════════
    # 활동 영역
    # ══════════════════════════════════════════════════════════════════
    if not sentences:
        st.info("아직 지문이 없습니다. 선생님이 지문을 등록하면 여기에 나타납니다.")
    elif revealed:
        # 결과 공개 → 모두 히트맵
        st.success("🔓 우리 반 히트맵 — 함께 보며 토론해요!")
        render_heatmap(show_memos=True)
    else:
        # 태깅 화면
        questions = db.ts_get_questions()
        if questions:
            with st.expander("📌 날개 문제 (근거 문장을 찾아보세요)", expanded=True):
                for i, q in enumerate(questions, 1):
                    st.markdown(f"**Q{i}.** {q['text']}")

        legend = " ".join(
            f"<span style='background:{t['bg']}; color:{t['color']}; padding:3px 10px; "
            f"border-radius:20px; font-size:12px; font-weight:700; margin-right:4px;'>"
            f"{t['icon']} {name}</span>"
            for name, t in TAGS.items()
        )
        st.markdown(legend, unsafe_allow_html=True)
        st.markdown("")

        if not sname:
            st.warning("👈 사이드바에서 이름을 입력하면 태그를 달 수 있어요.")
        elif db.ts_is_submitted(sname):
            st.success("✅ 제출 완료! 선생님이 히트맵을 공개하면 전체 결과를 볼 수 있어요.")
        else:
            tag_options = list(TAGS.keys())
            for sent in sentences:
                idx = sent["idx"]
                st.markdown(f"""
                <div style="background:white; border:1px solid #E0E8FF; border-radius:10px;
                            padding:12px 16px; margin-bottom:4px;">
                  <span style="font-size:12px; color:#8FA8E8;">문장 {idx + 1}</span><br>
                  <span style="font-size:15px; line-height:1.7;">{sent['text']}</span>
                </div>
                """, unsafe_allow_html=True)

                existing = db.ts_get_student_tags(sname, idx)
                selected = st.multiselect(
                    f"태그 {idx+1}", tag_options, default=existing,
                    key=f"tag_{idx}", label_visibility="collapsed",
                )
                existing_memo = db.ts_get_student_memo(sname, idx)
                memo = st.text_input(
                    f"메모 {idx+1}", value=existing_memo, key=f"memo_{idx}",
                    placeholder="자유 메모: 공감, 궁금증, 작가 의도 추측 등...",
                    label_visibility="collapsed",
                )
                if st.button("💾 저장", key=f"save_{idx}"):
                    db.ts_save_tags(sname, idx, selected)
                    db.ts_save_memo(sname, idx, memo)
                    st.toast(f"문장 {idx+1} 저장됨")
                st.markdown("")

            st.warning("모든 문장 태깅이 끝나면 제출하세요. 제출 후에는 수정할 수 없어요.")
            if st.button("📤 최종 제출", type="primary"):
                db.ts_mark_submitted(sname)
                st.rerun()

    if st.button("🔄 새로고침", key="ts_refresh"):
        st.rerun()

    # ══════════════════════════════════════════════════════════════════
    # 수업 설정 (교사용 — 접힘)
    # ══════════════════════════════════════════════════════════════════
    st.markdown("---")
    with st.expander("⚙️ 수업 설정 (선생님용)", expanded=False):

        st.markdown("**① 지문 & 날개 문제 등록**")
        if st.button("📚 샘플 지문 불러오기"):
            st.session_state["ts_text_input"] = SAMPLE_TEXT
            st.session_state["ts_q_input"] = "\n".join(SAMPLE_QUESTIONS)
            st.rerun()

        text = st.text_area("영어 지문", value=st.session_state.get("ts_text_input", ""),
                            height=150, key="ts_text_input")
        questions = st.text_area("날개 문제 (한 줄에 하나씩)",
                                value=st.session_state.get("ts_q_input", ""),
                                height=80, key="ts_q_input")
        if st.button("✅ 지문 등록 / 새 수업 시작", type="primary"):
            if text.strip():
                db.ts_set_text(split_sentences(text))
                q_list = [q.strip() for q in questions.split("\n") if q.strip()]
                db.ts_set_questions(q_list)
                db.set_state("ts_state", "reveal", "false")
                st.success("지문 등록 완료")
                st.rerun()
            else:
                st.warning("지문을 입력해 주세요.")

        st.markdown("---")
        st.markdown("**② 제출 현황 & 공개 제어**")
        participants = db.ts_get_participants()
        submitted = db.ts_get_submitted_list()
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("참여", f"{len(participants)}명")
        sc2.metric("제출", f"{len(submitted)}명")
        sc3.metric("작성 중", f"{len(set(participants)-set(submitted))}명")
        if submitted:
            st.caption(f"✅ 제출: {', '.join(submitted)}")

        rc1, rc2 = st.columns(2)
        if rc1.button("🔓 히트맵 공개", type="primary", use_container_width=True):
            db.set_state("ts_state", "reveal", "true")
            st.rerun()
        if rc2.button("🔒 다시 잠금", use_container_width=True):
            db.set_state("ts_state", "reveal", "false")
            st.rerun()

        cur = "🔓 공개 중" if revealed else "🔒 잠금 중"
        st.caption(f"현재: {cur}")

        if st.button("🗑️ 학생 데이터 초기화 (지문 유지)"):
            db.ts_reset_all()
            db.set_state("ts_state", "reveal", "false")
            st.rerun()

        st.markdown("---")
        st.markdown("**③ 히트맵 미리보기 (선생님만)**")
        render_heatmap(show_memos=True)


def render_heatmap(show_memos=False):
    sentences = db.ts_get_sentences()
    all_tags = db.ts_get_all_tags()
    all_memos = db.ts_get_all_memos()
    participants = db.ts_get_participants()
    total_students = max(len(participants), 1)

    if not all_tags and not all_memos:
        st.caption("아직 학생 태그가 없습니다.")
        return

    sent_tag_counts = defaultdict(lambda: defaultdict(int))
    for t in all_tags:
        sent_tag_counts[t["sentence_idx"]][t["tag"]] += 1
    sent_memos = defaultdict(list)
    for m in all_memos:
        sent_memos[m["sentence_idx"]].append(m)

    for sent in sentences:
        idx = sent["idx"]
        tag_counts = sent_tag_counts.get(idx, {})
        total_tags = sum(tag_counts.values())
        heat = total_tags / total_students
        if heat >= 1.0:
            bar = "#3C3489"
        elif heat >= 0.5:
            bar = "#9F9CE0"
        elif heat > 0:
            bar = "#D8D6F5"
        else:
            bar = "#eee"

        chips = ""
        for tag_name, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            info = TAGS.get(tag_name, {"bg": "#eee", "color": "#555", "icon": ""})
            chips += (f"<span style='background:{info['bg']}; color:{info['color']}; "
                      f"padding:2px 9px; border-radius:20px; font-size:12px; font-weight:700; "
                      f"margin-right:4px;'>{info['icon']} {tag_name} {count}</span> ")

        memo_html = ""
        if show_memos and idx in sent_memos:
            memo_html = "<div style='margin-top:8px;'>"
            for m in sent_memos[idx]:
                memo_html += (f"<div style='font-size:13px; color:#666; margin-top:3px;'>"
                              f"💬 <b>{m['student']}</b>: {m['memo']}</div>")
            memo_html += "</div>"

        st.markdown(f"""
        <div style="background:white; border-left:4px solid {bar};
                    border-radius:0 10px 10px 0; padding:12px 16px; margin-bottom:6px;
                    border-top:1px solid #eee; border-right:1px solid #eee; border-bottom:1px solid #eee;">
          <span style="font-size:12px; color:#8FA8E8;">문장 {idx+1} · 태그 {total_tags}개</span><br>
          <span style="font-size:15px; line-height:1.7;">{sent['text']}</span>
          <div style="margin-top:8px;">{chips if chips else "<span style='color:#bbb; font-size:13px;'>태그 없음</span>"}</div>
          {memo_html}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("##### 태그 유형별 집계")
    type_total = defaultdict(int)
    for t in all_tags:
        type_total[t["tag"]] += 1
    cols = st.columns(len(TAGS))
    for col, (name, info) in zip(cols, TAGS.items()):
        col.markdown(f"""
        <div style="background:{info['bg']}; border-radius:10px; padding:10px; text-align:center;">
          <div style="font-size:1.5rem; font-weight:800; color:{info['color']};">{type_total.get(name, 0)}</div>
          <div style="font-size:12px; color:{info['color']};">{info['icon']} {name}</div>
        </div>
        """, unsafe_allow_html=True)

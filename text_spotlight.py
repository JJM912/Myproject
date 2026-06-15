"""
text_spotlight.py — 앱 2: Text Spotlight
학생이 개별로 지문에 태그를 달고, 전체 제출 후 히트맵이 모든 화면에 공개됩니다.
태깅 중에는 다른 학생의 선택이 숨겨져 쏠림 현상을 방지합니다.
"""
import streamlit as st
import re
import db


# 태그 정의
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


# ══════════════════════════════════════════════════════════════════════
# 교사 화면
# ══════════════════════════════════════════════════════════════════════
def teacher_view():
    st.markdown("## 👩‍🏫 Text Spotlight — 교사 화면")
    st.caption("지문과 날개 문제를 등록하고, 학생 제출 현황을 확인한 뒤 히트맵을 공개하세요.")

    # ── 지문 등록 ──────────────────────────────────────────────────────
    with st.expander("📄 지문 & 날개 문제 등록", expanded=True):
        if st.button("📚 샘플 지문 불러오기"):
            st.session_state["ts_text_input"] = SAMPLE_TEXT
            st.session_state["ts_q_input"] = "\n".join(SAMPLE_QUESTIONS)
            st.rerun()

        text = st.text_area(
            "영어 지문",
            value=st.session_state.get("ts_text_input", ""),
            height=160,
            key="ts_text_input",
        )
        questions = st.text_area(
            "날개 문제 (한 줄에 하나씩)",
            value=st.session_state.get("ts_q_input", ""),
            height=90,
            key="ts_q_input",
            placeholder="Why did the writer feel lost?\nWhat lesson did the writer learn?",
        )

        if st.button("✅ 지문 등록 / 새 수업 시작", type="primary"):
            if text.strip():
                sentences = split_sentences(text)
                db.ts_set_text(sentences)
                q_list = [q.strip() for q in questions.split("\n") if q.strip()]
                db.ts_set_questions(q_list)
                db.set_state("ts_state", "reveal", "false")
                st.success(f"지문 등록 완료 — {len(sentences)}문장 / 날개 문제 {len(q_list)}개")
            else:
                st.warning("지문을 입력해 주세요.")

    sentences = db.ts_get_sentences()
    if not sentences:
        st.info("지문을 먼저 등록해 주세요.")
        return

    # ── 제출 현황 ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📋 제출 현황")
    participants = db.ts_get_participants()
    submitted = db.ts_get_submitted_list()

    c1, c2, c3 = st.columns(3)
    c1.metric("참여 학생", f"{len(participants)}명")
    c2.metric("제출 완료", f"{len(submitted)}명")
    not_submitted = set(participants) - set(submitted)
    c3.metric("작성 중", f"{len(not_submitted)}명")

    if submitted:
        st.caption(f"✅ 제출 완료: {', '.join(submitted)}")
    if not_submitted:
        st.caption(f"✍️ 작성 중: {', '.join(not_submitted)}")

    if st.button("🔄 현황 새로고침"):
        st.rerun()

    # ── 공개 제어 ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🎬 히트맵 공개 제어")
    revealed = db.get_state("ts_state", "reveal", "false") == "true"

    rc1, rc2 = st.columns(2)
    if rc1.button("🔓 전체 히트맵 공개", type="primary"):
        db.set_state("ts_state", "reveal", "true")
        st.rerun()
    if rc2.button("🔒 다시 잠금"):
        db.set_state("ts_state", "reveal", "false")
        st.rerun()

    status = "🔓 공개 중 — 모든 학생 화면에 히트맵 표시" if revealed else "🔒 잠금 중 — 학생은 자기 태그만 봄"
    st.info(f"현재 상태: {status}")

    if st.button("🗑️ 학생 데이터 초기화 (지문 유지)"):
        db.ts_reset_all()
        db.set_state("ts_state", "reveal", "false")
        st.rerun()

    # ── 교사용 히트맵 미리보기 (항상 표시) ──────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 히트맵 (교사 미리보기)")
    st.caption("교사는 공개 전에도 미리 볼 수 있습니다.")
    render_heatmap(show_memos=True)


# ══════════════════════════════════════════════════════════════════════
# 학생 화면
# ══════════════════════════════════════════════════════════════════════
def student_view(student_name):
    st.markdown("## 👤 Text Spotlight")
    sentences = db.ts_get_sentences()
    if not sentences:
        st.info("교사가 지문을 등록하면 여기에 나타납니다.")
        if st.button("🔄 새로고침"):
            st.rerun()
        return

    revealed = db.get_state("ts_state", "reveal", "false") == "true"

    # 결과가 공개되면 모든 학생이 히트맵을 봄
    if revealed:
        st.caption("전체 결과가 공개됐습니다. 함께 보며 토론해요!")
        st.success("🔓 학급 전체 히트맵")
        render_heatmap(show_memos=True)
        if st.button("🔄 새로고침"):
            st.rerun()
        return

    # 태깅 화면
    st.caption(f"{student_name} 님 — 각 문장을 읽고 해당하는 태그를 선택하세요. (다른 학생 선택은 제출 전까지 숨겨집니다)")

    # 날개 문제 표시
    questions = db.ts_get_questions()
    if questions:
        with st.expander("📌 날개 문제 (근거 문장을 찾아보세요)", expanded=True):
            for i, q in enumerate(questions, 1):
                st.markdown(f"**Q{i}.** {q['text']}")

    # 태그 범례
    legend = " ".join(
        f"<span style='background:{t['bg']}; color:{t['color']}; padding:3px 10px; "
        f"border-radius:20px; font-size:12px; font-weight:600; margin-right:4px;'>"
        f"{t['icon']} {name}</span>"
        for name, t in TAGS.items()
    )
    st.markdown(legend, unsafe_allow_html=True)
    st.markdown("---")

    already_submitted = db.ts_is_submitted(student_name)
    if already_submitted:
        st.success("✅ 제출 완료! 교사가 히트맵을 공개하면 전체 결과를 볼 수 있습니다.")
        if st.button("🔄 새로고침"):
            st.rerun()
        return

    # 문장별 태깅
    tag_options = list(TAGS.keys())
    for sent in sentences:
        idx = sent["idx"]
        st.markdown(f"""
        <div style="background:white; border:1px solid #e9ecef; border-radius:10px;
                    padding:12px 16px; margin-bottom:4px;">
          <span style="font-size:12px; color:#888;">문장 {idx + 1}</span><br>
          <span style="font-size:15px; line-height:1.7;">{sent['text']}</span>
        </div>
        """, unsafe_allow_html=True)

        existing = db.ts_get_student_tags(student_name, idx)
        selected = st.multiselect(
            f"태그 (문장 {idx + 1})",
            tag_options,
            default=existing,
            key=f"tag_sel_{idx}",
            label_visibility="collapsed",
        )

        existing_memo = db.ts_get_student_memo(student_name, idx)
        memo = st.text_input(
            f"메모 (문장 {idx + 1})",
            value=existing_memo,
            key=f"memo_{idx}",
            placeholder="자유 메모: 공감, 궁금증, 작가 의도 추측 등...",
            label_visibility="collapsed",
        )

        if st.button("💾 이 문장 저장", key=f"save_{idx}"):
            db.ts_save_tags(student_name, idx, selected)
            db.ts_save_memo(student_name, idx, memo)
            st.toast(f"문장 {idx + 1} 저장됨")

        st.markdown("")

    st.markdown("---")
    st.warning("모든 문장 태깅이 끝나면 아래 버튼을 눌러 제출하세요. 제출 후에는 수정할 수 없습니다.")
    if st.button("📤 최종 제출", type="primary"):
        db.ts_mark_submitted(student_name)
        st.rerun()


# ══════════════════════════════════════════════════════════════════════
# 히트맵 렌더링 (공통)
# ══════════════════════════════════════════════════════════════════════
def render_heatmap(show_memos=False):
    sentences = db.ts_get_sentences()
    all_tags = db.ts_get_all_tags()
    all_memos = db.ts_get_all_memos()
    participants = db.ts_get_participants()
    total_students = max(len(participants), 1)

    if not all_tags and not all_memos:
        st.caption("아직 학생 태그가 없습니다.")
        return

    # 문장별 태그 집계
    from collections import defaultdict
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

        # 열 강도에 따른 좌측 바 색
        if heat >= 1.0:
            bar = "#3C3489"
        elif heat >= 0.5:
            bar = "#9F9CE0"
        elif heat > 0:
            bar = "#D8D6F5"
        else:
            bar = "#eee"

        # 태그 칩
        chips = ""
        for tag_name, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            info = TAGS.get(tag_name, {"bg": "#eee", "color": "#555", "icon": ""})
            chips += (
                f"<span style='background:{info['bg']}; color:{info['color']}; "
                f"padding:2px 9px; border-radius:20px; font-size:12px; font-weight:600; "
                f"margin-right:4px;'>{info['icon']} {tag_name} {count}</span> "
            )

        # 메모
        memo_html = ""
        if show_memos and idx in sent_memos:
            memo_html = "<div style='margin-top:8px;'>"
            for m in sent_memos[idx]:
                memo_html += (
                    f"<div style='font-size:13px; color:#666; margin-top:3px;'>"
                    f"💬 <b>{m['student']}</b>: {m['memo']}</div>"
                )
            memo_html += "</div>"

        st.markdown(f"""
        <div style="background:white; border-left:4px solid {bar};
                    border-radius:0 10px 10px 0; padding:12px 16px; margin-bottom:6px;
                    border-top:1px solid #eee; border-right:1px solid #eee; border-bottom:1px solid #eee;">
          <span style="font-size:12px; color:#888;">문장 {idx + 1} · 태그 {total_tags}개</span><br>
          <span style="font-size:15px; line-height:1.7;">{sent['text']}</span>
          <div style="margin-top:8px;">{chips if chips else "<span style='color:#bbb; font-size:13px;'>태그 없음</span>"}</div>
          {memo_html}
        </div>
        """, unsafe_allow_html=True)

    # 태그 유형별 총계
    st.markdown("##### 태그 유형별 집계")
    type_total = defaultdict(int)
    for t in all_tags:
        type_total[t["tag"]] += 1
    cols = st.columns(len(TAGS))
    for col, (name, info) in zip(cols, TAGS.items()):
        col.markdown(f"""
        <div style="background:{info['bg']}; border-radius:10px; padding:10px; text-align:center;">
          <div style="font-size:1.5rem; font-weight:700; color:{info['color']};">{type_total.get(name, 0)}</div>
          <div style="font-size:12px; color:{info['color']};">{info['icon']} {name}</div>
        </div>
        """, unsafe_allow_html=True)

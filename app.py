import streamlit as st
from notion_client import Client
from openai import OpenAI
from datetime import datetime

# ══════════════════════════════════════════════════════════════
# 페이지 기본 설정
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="K-water AI연구소 · 업무현황",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# 사이버펑크 CSS 테마
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Noto+Sans+KR:wght@300;400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: #0a0e1a;
    color: #c8d8f0;
}
.stApp { background: #0a0e1a; }

.cp-header {
    font-family: 'Orbitron', monospace;
    font-size: 1.6rem;
    font-weight: 900;
    color: #00f5ff;
    text-shadow: 0 0 20px #00f5ff88;
    letter-spacing: 3px;
    border-bottom: 1px solid #00f5ff44;
    padding-bottom: 8px;
    margin-bottom: 4px;
}
.cp-sub {
    font-size: 0.78rem;
    color: #5a7a9a;
    letter-spacing: 2px;
    margin-bottom: 20px;
}
.member-card {
    background: linear-gradient(135deg, #0d1526 0%, #111d30 100%);
    border: 1px solid #1e3a5f;
    border-left: 3px solid #00f5ff;
    border-radius: 6px;
    padding: 14px 18px;
    margin: 6px 0;
}
.member-name { font-family:'Orbitron',monospace; font-size:0.9rem; color:#00f5ff; font-weight:700; }
.member-role { font-size:0.8rem; color:#8ab4cc; margin-top:2px; }

.badge-done    { background:#003322; color:#00ff88; border:1px solid #00ff88; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-family:'Orbitron',monospace; }
.badge-review  { background:#1a1a00; color:#ffcc00; border:1px solid #ffcc00; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-family:'Orbitron',monospace; }
.badge-pending { background:#1a0022; color:#cc66ff; border:1px solid #cc66ff; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-family:'Orbitron',monospace; }
.badge-none    { background:#111; color:#556677; border:1px solid #334455; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-family:'Orbitron',monospace; }

.ai-result {
    background: #071020;
    border: 1px solid #00f5ff33;
    border-radius: 8px;
    padding: 18px;
    font-size: 0.9rem;
    line-height: 1.8;
    white-space: pre-wrap;
    color: #b0d4e8;
}
.stat-box { background:linear-gradient(135deg,#0d1526,#0a1a2e); border:1px solid #1e3a5f; border-radius:8px; padding:16px; text-align:center; }
.stat-number { font-family:'Orbitron',monospace; font-size:2rem; font-weight:900; color:#00f5ff; text-shadow:0 0 12px #00f5ff66; }
.stat-label  { font-size:0.72rem; color:#5a7a9a; letter-spacing:1px; margin-top:4px; }
.cp-divider  { border:none; border-top:1px solid #1e3a5f; margin:20px 0; }

.cp-table { width:100%; border-collapse:collapse; font-size:0.85rem; }
.cp-table th { background:#0d1a2e; color:#00f5ff; font-family:'Orbitron',monospace; font-size:0.72rem; letter-spacing:2px; padding:10px 14px; border-bottom:1px solid #00f5ff44; text-align:left; }
.cp-table td { padding:10px 14px; border-bottom:1px solid #1e3a5f; color:#b0c8e0; vertical-align:top; }
.cp-table tr:hover td { background:#0d1830; }

.stTextInput>div>div>input,
.stTextArea>div>div>textarea { background:#0d1526 !important; border:1px solid #1e3a5f !important; color:#c8d8f0 !important; }
.stButton>button { background:linear-gradient(90deg,#003344,#005566) !important; color:#00f5ff !important; border:1px solid #00f5ff44 !important; font-family:'Orbitron',monospace !important; font-size:0.78rem !important; letter-spacing:1px !important; }
.stButton>button:hover { border-color:#00f5ff !important; box-shadow:0 0 14px #00f5ff44 !important; }
div[data-testid="stSidebar"] { background:#060d1a !important; border-right:1px solid #1e3a5f !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 기본 멤버 데이터 (26년 기준 — 실제 이름으로 교체)
# ══════════════════════════════════════════════════════════════
DEFAULT_MEMBERS = [
    {"이름": "홍길동",   "직급": "수석",   "주업무": "AI 기반 홍수예측 모델 개발",        "세부": "딥러닝 모델 설계, 실시간 하천유량 예측", "상태": "검토완료"},
    {"이름": "김민준",   "직급": "선임",   "주업무": "댐 안전성 디지털트윈 구축",         "세부": "IoT 센서 연계, 구조물 이상징후 탐지",   "상태": "검토중"},
    {"이름": "이서연",   "직급": "선임",   "주업무": "MLOps 플랫폼 운영",                 "세부": "파이프라인 자동화, 모델 배포 관리",      "상태": "미검토"},
    {"이름": "박지훈",   "직급": "연구원", "주업무": "수질 AI 분석 시스템",               "세부": "수질 데이터 전처리, 이상치 탐지",        "상태": "검토완료"},
    {"이름": "최수아",   "직급": "연구원", "주업무": "AI 공공서비스 정책 연구",            "세부": "국가과학기술 마스터플랜 대응 정책 분석", "상태": "미검토"},
    {"이름": "정태양",   "직급": "연구원", "주업무": "풍력예보 AI 모델 기술동향",          "세부": "기상데이터 융합, 예보 정확도 개선",      "상태": "검토중"},
]

STATUS_OPTIONS = ["검토완료", "검토중", "미검토", "보류"]
STATUS_BADGE   = {"검토완료":"badge-done","검토중":"badge-review","미검토":"badge-pending","보류":"badge-none"}
STATUS_EMOJI   = {"검토완료":"✅","검토중":"🔄","미검토":"🕐","보류":"⏸️"}

if "members" not in st.session_state:
    st.session_state.members = [m.copy() for m in DEFAULT_MEMBERS]
if "ai_outputs" not in st.session_state:
    st.session_state.ai_outputs = {}

# ══════════════════════════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    # GitHub에서 로고 불러오기 (실제 repo/브랜치명으로 교체)
    LOGO_URL = "https://github.com/newcave/2026NotionKWAI/logo.png"
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:16px;">
      <img src="{LOGO_URL}" onerror="this.style.display='none'"
           style="width:150px; border-radius:8px; border:1px solid #00f5ff44;" />
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="cp-header" style="font-size:1rem;">K-WATER<br>AI LAB</div>', unsafe_allow_html=True)
    st.markdown('<div class="cp-sub">AI RESEARCH CENTER · 2026</div>', unsafe_allow_html=True)
    st.divider()

    notion_token = st.text_input("🔑 Notion Internal Token", type="password", placeholder="secret_xxx")
    openai_key   = st.text_input("🤖 OpenAI API Key",        type="password", placeholder="sk-xxx")

    # ── 모델 선택 (추천 포함) ──
    st.markdown("##### 🧠 AI 모델")
    model_options = {
        "gpt-4o  ★ 균형·기본추천":      "gpt-4o",
        "gpt-4o-mini  빠름·저비용":     "gpt-4o-mini",
        "o3  ★★ 고추론·복잡분석 최강":  "o3",
        "o4-mini  추론·경량화":          "o4-mini",
    }
    model_label    = st.selectbox("모델 선택", list(model_options.keys()))
    selected_model = model_options[model_label]

    st.caption("""
💡 **모델 선택 가이드**
- **gpt-4o**: 요약·편집·번역 → 일반 업무 최적
- **o3**: 복잡한 연구 분석, 정책 추론 → 최고 성능
- **o4-mini**: o3 수준 추론, 비용 절감
- **gpt-4o-mini**: 빠른 초안, 대량 처리
    """)

    st.divider()
    notion_page_id = st.text_input("📄 Notion 저장 페이지 ID", placeholder="30531c56-8f2f-...")
    st.markdown(f'<div style="font-family:Orbitron,monospace;font-size:0.7rem;color:#334455;margin-top:16px;">{datetime.now().strftime("%Y.%m.%d %H:%M")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 클라이언트 & AI 호출
# ══════════════════════════════════════════════════════════════
notion = Client(auth=notion_token) if notion_token else None
oai    = OpenAI(api_key=openai_key) if openai_key else None

def call_ai(system: str, user: str) -> str:
    if not oai:
        return "⚠️ OpenAI API Key를 사이드바에 입력해주세요."
    kwargs = dict(model=selected_model, messages=[
        {"role":"system","content":system},
        {"role":"user",  "content":user}
    ])
    if selected_model in ("o3","o4-mini"):
        kwargs["max_completion_tokens"] = 1500
    else:
        kwargs["max_tokens"] = 1500
    return oai.chat.completions.create(**kwargs).choices[0].message.content

def save_to_notion(title: str, content: str):
    if not notion or not notion_page_id:
        return False
    notion.blocks.children.append(
        block_id=notion_page_id,
        children=[
            {"object":"block","type":"heading_2",
             "heading_2":{"rich_text":[{"text":{"content":title}}]}},
            {"object":"block","type":"paragraph",
             "paragraph":{"rich_text":[{"text":{"content":content}}]}}
        ]
    )
    return True

# ══════════════════════════════════════════════════════════════
# 메인 헤더
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="cp-header">2026 AI연구소 그룹멤버 업무현황</div>', unsafe_allow_html=True)
st.markdown('<div class="cp-sub">K-WATER AI RESEARCH CENTER · MEMBER WORK REVIEW DASHBOARD</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📊 전체 현황", "👤 개인 상세·검토", "🤖 일괄 AI 요약", "⚙️ 멤버 관리"])

# ════════════════════════════════════════════════════════════
# TAB 1: 전체 현황
# ════════════════════════════════════════════════════════════
with tab1:
    members = st.session_state.members
    total   = len(members)
    done    = sum(1 for m in members if m["상태"]=="검토완료")
    ongoing = sum(1 for m in members if m["상태"]=="검토중")
    pending = sum(1 for m in members if m["상태"]=="미검토")

    c1,c2,c3,c4 = st.columns(4)
    for col,(label,val,color) in zip(
        [c1,c2,c3,c4],
        [("전체 멤버",total,"#00f5ff"),("검토 완료",done,"#00ff88"),
         ("검토 중",ongoing,"#ffcc00"),("미검토",pending,"#cc66ff")]
    ):
        col.markdown(f'<div class="stat-box"><div class="stat-number" style="color:{color};text-shadow:0 0 12px {color}66;">{val}</div><div class="stat-label">{label}</div></div>',
                     unsafe_allow_html=True)

    st.markdown('<hr class="cp-divider">', unsafe_allow_html=True)
    st.markdown("### 📋 멤버별 주업무 현황표 (2026)")

    rows = ""
    for m in members:
        badge = STATUS_BADGE.get(m["상태"],"badge-none")
        emoji = STATUS_EMOJI.get(m["상태"],"")
        ai_mark = '<span style="color:#00f5ff;">✦</span>' if m["이름"] in st.session_state.ai_outputs else ""
        rows += f"""<tr>
            <td><span class="member-name">{m['이름']}</span></td>
            <td style="color:#667788;font-size:0.8rem;">{m['직급']}</td>
            <td style="color:#8ab4cc;">{m['주업무']}</td>
            <td style="color:#667788;font-size:0.8rem;">{m['세부']}</td>
            <td><span class="{badge}">{emoji} {m['상태']}</span></td>
            <td style="text-align:center;">{ai_mark}</td>
        </tr>"""

    st.markdown(f"""<table class="cp-table"><thead><tr>
        <th>이름</th><th>직급</th><th>주업무</th><th>세부내용</th><th>검토상태</th><th>AI요약</th>
    </tr></thead><tbody>{rows}</tbody></table>""", unsafe_allow_html=True)

    st.markdown('<hr class="cp-divider">', unsafe_allow_html=True)
    st.markdown("### 📝 전체 팀 업무 AI 종합보고서")

    if st.button("🚀 전체 멤버 종합보고서 생성", use_container_width=True):
        member_text = "\n".join(
            f"- {m['이름']} ({m['직급']}): {m['주업무']} / {m['세부']} [검토:{m['상태']}]"
            for m in members
        )
        with st.spinner("AI 보고서 작성 중..."):
            report = call_ai(
                "당신은 K-water AI연구소 소장입니다. 팀원 업무를 분석해 2026년 팀 전체 업무현황 보고서를 작성하세요. "
                "형식: [개요] → [멤버별 핵심업무 요약] → [연구 시너지 분석] → [소장 종합의견 및 지시사항]",
                f"2026년 K-water AI연구소 멤버 업무 목록:\n{member_text}"
            )
        st.markdown(f'<div class="ai-result">{report}</div>', unsafe_allow_html=True)
        if st.button("💾 Notion에 종합보고서 저장"):
            if save_to_notion(f"[AI종합보고서] 2026 팀 업무현황 {datetime.now().strftime('%Y.%m.%d')}", report):
                st.success("✅ Notion 저장 완료!")

# ════════════════════════════════════════════════════════════
# TAB 2: 개인 상세 · 검토
# ════════════════════════════════════════════════════════════
with tab2:
    members  = st.session_state.members
    names    = [m["이름"] for m in members]
    sel_name = st.selectbox("👤 멤버 선택", names, key="tab2_select")
    m_idx    = names.index(sel_name)
    member   = members[m_idx]

    col_l, col_r = st.columns([3, 1])
    with col_l:
        st.markdown(f"""<div class="member-card">
            <div class="member-name">{member['이름']}</div>
            <div class="member-role">{member['직급']} · K-water AI연구소</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("**📌 주업무**")
        new_role   = st.text_input("주업무 수정", value=member["주업무"], key=f"role_{m_idx}")
        st.markdown("**📝 세부내용**")
        new_detail = st.text_area("세부내용 수정", value=member["세부"], height=80, key=f"detail_{m_idx}")

        col_s1, col_s2 = st.columns(2)
        new_status = col_s1.selectbox("검토 상태", STATUS_OPTIONS,
                                       index=STATUS_OPTIONS.index(member["상태"]), key=f"status_{m_idx}")
        if col_s2.button("💾 저장", key=f"save_{m_idx}", use_container_width=True):
            st.session_state.members[m_idx].update({"주업무":new_role,"세부":new_detail,"상태":new_status})
            st.success("저장 완료!")
            st.rerun()

    with col_r:
        badge = STATUS_BADGE.get(member["상태"],"badge-none")
        emoji = STATUS_EMOJI.get(member["상태"],"")
        st.markdown(f"""<div style="text-align:center;margin-top:30px;">
            <span class="{badge}" style="font-size:1rem;padding:8px 20px;">{emoji} {member['상태']}</span>
        </div>""", unsafe_allow_html=True)
        if sel_name in st.session_state.ai_outputs:
            st.markdown('<div style="text-align:center;margin-top:12px;color:#00f5ff;font-family:Orbitron,monospace;font-size:0.75rem;">✦ AI 요약 완료</div>', unsafe_allow_html=True)

    st.divider()

    # 개인 AI 분석
    st.markdown("#### 🤖 개인 업무 AI 검토")
    style_sel = st.selectbox("검토 관점", [
        "소장 검토 보고서  (배경·강점·개선·의견)",
        "3줄 핵심 요약",
        "연구 성과 중심 평가",
        "타 부서 협업 방안 제안",
    ], key="tab2_style")
    custom_q = st.text_input("추가 검토 포인트 (선택)", placeholder="예: 26년 중점 추진 과제는?")

    STYLE_SYS = {
        "소장 검토 보고서  (배경·강점·개선·의견)": "[업무핵심요약] [강점분석] [개선제안] [소장코멘트] 형식으로 작성하세요.",
        "3줄 핵심 요약": "3줄로 핵심만 요약하세요. 간결하게.",
        "연구 성과 중심 평가": "연구 성과, 기술 기여도 중심으로 평가하고 향후 방향을 제시하세요.",
        "타 부서 협업 방안 제안": "다른 연구팀·부서와의 시너지 협업 방안 3가지를 구체적으로 제안하세요.",
    }

    if st.button(f"✨ {sel_name} AI 분석 실행", use_container_width=True):
        prompt = f"이름:{member['이름']} ({member['직급']})\n주업무:{member['주업무']}\n세부:{member['세부']}\n추가질문:{custom_q or '없음'}"
        with st.spinner("분석 중..."):
            result = call_ai(
                f"당신은 K-water AI연구소 소장입니다. {STYLE_SYS[style_sel]}",
                prompt
            )
        st.session_state.ai_outputs[sel_name] = result
        st.session_state.members[m_idx]["상태"] = "검토완료"

    if sel_name in st.session_state.ai_outputs:
        st.markdown(f'<div class="ai-result">{st.session_state.ai_outputs[sel_name]}</div>', unsafe_allow_html=True)
        if st.button("💾 Notion 저장", use_container_width=True, key="save_notion_tab2"):
            title = f"[AI검토] {sel_name} · {datetime.now().strftime('%Y.%m.%d')}"
            if save_to_notion(title, st.session_state.ai_outputs[sel_name]):
                st.success("✅ Notion 저장 완료!")
            else:
                st.warning("Notion Token과 페이지 ID를 사이드바에서 확인해주세요.")

# ════════════════════════════════════════════════════════════
# TAB 3: 일괄 AI 요약
# ════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🤖 전체 멤버 AI 요약 일괄 생성")

    col_a, col_b = st.columns(2)
    target = col_a.multiselect(
        "대상 멤버",
        [m["이름"] for m in st.session_state.members],
        default=[m["이름"] for m in st.session_state.members if m["상태"] != "검토완료"]
    )
    batch_style = col_b.selectbox("요약 스타일", [
        "소장 검토 보고서", "3줄 핵심요약", "강점·보완점 분석", "연구 성과 중심"
    ])
    BATCH_SYS = {
        "소장 검토 보고서":   "[업무요약][강점][개선사항][종합의견] 형식으로 작성하세요.",
        "3줄 핵심요약":       "3줄로 핵심만 요약하세요.",
        "강점·보완점 분석":   "[강점 3가지] [보완점 2가지] [액션아이템] 형식으로 작성하세요.",
        "연구 성과 중심":     "연구 성과와 기술 기여도 중심으로 평가하고 향후 방향을 제시하세요.",
    }

    if st.button("🚀 일괄 AI 요약 실행", use_container_width=True):
        if not oai:
            st.warning("OpenAI API Key를 입력해주세요.")
        elif not target:
            st.warning("대상 멤버를 선택해주세요.")
        else:
            prog = st.progress(0, text="처리 중...")
            target_members = [m for m in st.session_state.members if m["이름"] in target]
            for i, m in enumerate(target_members):
                result = call_ai(
                    f"당신은 K-water AI연구소 소장입니다. {BATCH_SYS[batch_style]}",
                    f"이름:{m['이름']} ({m['직급']})\n주업무:{m['주업무']}\n세부:{m['세부']}"
                )
                st.session_state.ai_outputs[m["이름"]] = result
                idx = [x["이름"] for x in st.session_state.members].index(m["이름"])
                st.session_state.members[idx]["상태"] = "검토완료"
                prog.progress((i+1)/len(target_members), text=f"{m['이름']} 완료...")
            st.success(f"✅ {len(target)}명 AI 요약 완료!")
            st.rerun()

    st.markdown('<hr class="cp-divider">', unsafe_allow_html=True)

    if st.session_state.ai_outputs:
        for name, output in st.session_state.ai_outputs.items():
            with st.expander(f"✦  {name} — AI 검토 결과"):
                st.markdown(f'<div class="ai-result">{output}</div>', unsafe_allow_html=True)
                if st.button(f"💾 {name} Notion 저장", key=f"batch_save_{name}"):
                    if save_to_notion(f"[AI검토] {name} · {datetime.now().strftime('%Y.%m.%d')}", output):
                        st.success("저장 완료!")
    else:
        st.info("아직 AI 요약 결과가 없습니다. 위에서 실행해주세요.")

# ════════════════════════════════════════════════════════════
# TAB 4: 멤버 관리
# ════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### ⚙️ 멤버 추가 / 삭제")

    with st.expander("➕ 새 멤버 추가"):
        c1,c2 = st.columns(2)
        nn = c1.text_input("이름")
        nr = c2.selectbox("직급", ["수석","선임","연구원","인턴"])
        nj = st.text_input("주업무")
        nd = st.text_area("세부내용", height=70)
        if st.button("➕ 추가", use_container_width=True):
            if nn and nj:
                st.session_state.members.append({"이름":nn,"직급":nr,"주업무":nj,"세부":nd,"상태":"미검토"})
                st.success(f"{nn} 추가 완료!")
                st.rerun()

    with st.expander("🗑️ 멤버 삭제"):
        del_name = st.selectbox("삭제 대상", [m["이름"] for m in st.session_state.members])
        if st.button("🗑️ 삭제", use_container_width=True):
            st.session_state.members = [m for m in st.session_state.members if m["이름"] != del_name]
            st.session_state.ai_outputs.pop(del_name, None)
            st.success(f"{del_name} 삭제 완료")
            st.rerun()

    st.divider()
    if st.button("🔄 기본값으로 초기화", use_container_width=True):
        st.session_state.members    = [m.copy() for m in DEFAULT_MEMBERS]
        st.session_state.ai_outputs = {}
        st.success("초기화 완료")
        st.rerun()

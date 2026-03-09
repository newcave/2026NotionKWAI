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
# CSS 테마 (사이버펑크)
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Noto+Sans+KR:wght@300;400;700&display=swap');
html,body,[class*="css"]{ font-family:'Noto Sans KR',sans-serif; background:#0a0e1a; color:#c8d8f0; }
.stApp{ background:#0a0e1a; }
.cp-header{ font-family:'Orbitron',monospace; font-size:1.6rem; font-weight:900; color:#00f5ff;
  text-shadow:0 0 20px #00f5ff88; letter-spacing:3px; border-bottom:1px solid #00f5ff44;
  padding-bottom:8px; margin-bottom:4px; }
.cp-sub{ font-size:0.78rem; color:#5a7a9a; letter-spacing:2px; margin-bottom:20px; }
.cp-divider{ border:none; border-top:1px solid #1e3a5f; margin:20px 0; }

/* 멤버 카드 */
.member-card{ background:linear-gradient(135deg,#0d1526,#111d30); border:1px solid #1e3a5f;
  border-left:3px solid #00f5ff; border-radius:6px; padding:14px 18px; margin:6px 0; }
.member-name{ font-family:'Orbitron',monospace; font-size:0.9rem; color:#00f5ff; font-weight:700; }
.member-role{ font-size:0.8rem; color:#8ab4cc; margin-top:2px; }

/* 뱃지 */
.badge-done   { background:#003322; color:#00ff88; border:1px solid #00ff88; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-family:'Orbitron',monospace; }
.badge-review { background:#1a1a00; color:#ffcc00; border:1px solid #ffcc00; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-family:'Orbitron',monospace; }
.badge-pending{ background:#1a0022; color:#cc66ff; border:1px solid #cc66ff; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-family:'Orbitron',monospace; }
.badge-none   { background:#111;    color:#556677; border:1px solid #334455; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-family:'Orbitron',monospace; }
.key-ok { background:#003322; color:#00ff88; border:1px solid #00ff88; border-radius:4px; padding:3px 10px; font-size:0.72rem; font-family:'Orbitron',monospace; }
.key-no { background:#1a0000; color:#ff4466; border:1px solid #ff4466; border-radius:4px; padding:3px 10px; font-size:0.72rem; font-family:'Orbitron',monospace; }
.key-ovr{ background:#1a1a00; color:#ffcc00; border:1px solid #ffcc00; border-radius:4px; padding:3px 10px; font-size:0.72rem; font-family:'Orbitron',monospace; }

/* Notion 원문 박스 */
.notion-raw{ background:#060f1c; border:1px solid #1e3a5f; border-left:3px solid #334466;
  border-radius:6px; padding:16px; font-size:0.82rem; line-height:1.9; color:#8ab4cc;
  white-space:pre-wrap; max-height:320px; overflow-y:auto; }
/* 링크/파일 박스 */
.attach-box{ background:#071525; border:1px solid #1e3a5f; border-radius:6px;
  padding:12px 16px; font-size:0.8rem; color:#7a9ab8; margin-top:8px; }
.attach-box a{ color:#00f5ff; text-decoration:none; }
.attach-box a:hover{ text-decoration:underline; }

/* AI 결과 */
.ai-result{ background:#071020; border:1px solid #00f5ff33; border-radius:8px;
  padding:18px; font-size:0.9rem; line-height:1.8; white-space:pre-wrap; color:#b0d4e8; }

/* 통계 */
.stat-box{ background:linear-gradient(135deg,#0d1526,#0a1a2e); border:1px solid #1e3a5f;
  border-radius:8px; padding:16px; text-align:center; }
.stat-number{ font-family:'Orbitron',monospace; font-size:2rem; font-weight:900;
  color:#00f5ff; text-shadow:0 0 12px #00f5ff66; }
.stat-label{ font-size:0.72rem; color:#5a7a9a; letter-spacing:1px; margin-top:4px; }

/* 테이블 */
.cp-table{ width:100%; border-collapse:collapse; font-size:0.85rem; }
.cp-table th{ background:#0d1a2e; color:#00f5ff; font-family:'Orbitron',monospace;
  font-size:0.72rem; letter-spacing:2px; padding:10px 14px; border-bottom:1px solid #00f5ff44; text-align:left; }
.cp-table td{ padding:10px 14px; border-bottom:1px solid #1e3a5f; color:#b0c8e0; vertical-align:top; }
.cp-table tr:hover td{ background:#0d1830; }

/* Streamlit 위젯 */
.stTextInput>div>div>input,.stTextArea>div>div>textarea{
  background:#0d1526 !important; border:1px solid #1e3a5f !important; color:#c8d8f0 !important; }
.stButton>button{ background:linear-gradient(90deg,#003344,#005566) !important;
  color:#00f5ff !important; border:1px solid #00f5ff44 !important;
  font-family:'Orbitron',monospace !important; font-size:0.78rem !important; letter-spacing:1px !important; }
.stButton>button:hover{ border-color:#00f5ff !important; box-shadow:0 0 14px #00f5ff44 !important; }
div[data-testid="stSidebar"]{ background:#060d1a !important; border-right:1px solid #1e3a5f !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# secrets 헬퍼
# ══════════════════════════════════════════════════════════════
def _secret(key, fallback=""):
    try:    return st.secrets.get(key, fallback)
    except: return fallback

# ══════════════════════════════════════════════════════════════
# 기본 멤버 데이터 (notion_page_id 필드 추가)
# ══════════════════════════════════════════════════════════════
DEFAULT_MEMBERS = [
    {"이름":"홍길동",  "직급":"수석",   "주업무":"AI 기반 홍수예측 모델 개발",       "세부":"딥러닝 모델 설계, 실시간 하천유량 예측", "상태":"미검토", "notion_page_id":""},
    {"이름":"김민준",  "직급":"선임",   "주업무":"댐 안전성 디지털트윈 구축",        "세부":"IoT 센서 연계, 구조물 이상징후 탐지",   "상태":"미검토", "notion_page_id":""},
    {"이름":"이서연",  "직급":"선임",   "주업무":"MLOps 플랫폼 운영",                "세부":"파이프라인 자동화, 모델 배포 관리",      "상태":"미검토", "notion_page_id":""},
    {"이름":"박지훈",  "직급":"연구원", "주업무":"수질 AI 분석 시스템",              "세부":"수질 데이터 전처리, 이상치 탐지",        "상태":"미검토", "notion_page_id":""},
    {"이름":"최수아",  "직급":"연구원", "주업무":"AI 공공서비스 정책 연구",           "세부":"국가과학기술 마스터플랜 대응 정책 분석", "상태":"미검토", "notion_page_id":""},
    {"이름":"정태양",  "직급":"연구원", "주업무":"풍력예보 AI 모델 기술동향",         "세부":"기상데이터 융합, 예보 정확도 개선",      "상태":"미검토", "notion_page_id":""},
]
STATUS_OPTIONS = ["미검토","검토중","검토완료","보류"]
STATUS_BADGE   = {"검토완료":"badge-done","검토중":"badge-review","미검토":"badge-pending","보류":"badge-none"}
STATUS_EMOJI   = {"검토완료":"✅","검토중":"🔄","미검토":"🕐","보류":"⏸️"}

if "members"        not in st.session_state: st.session_state.members        = [m.copy() for m in DEFAULT_MEMBERS]
if "ai_outputs"     not in st.session_state: st.session_state.ai_outputs     = {}   # {이름: ai 결과}
if "notion_contents" not in st.session_state: st.session_state.notion_contents = {}  # {이름: {text, links}}

# ══════════════════════════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    LOGO_URL = "https://raw.githubusercontent.com/newcave/2026NotionKWAI/main/AI%EC%97%B0%EA%B5%AC%EC%86%8C%EB%A1%9C%EA%B3%A0_%EC%82%AC%EC%9D%B4%EB%B2%84%ED%8E%91%ED%81%AC1%EB%B2%88.png"
    st.markdown(f'<div style="text-align:center;margin-bottom:16px;"><img src="{LOGO_URL}" onerror="this.style.display=\'none\'" style="width:150px;border-radius:8px;border:1px solid #00f5ff44;" /></div>', unsafe_allow_html=True)
    st.markdown('<div class="cp-header" style="font-size:1rem;">K-WATER<br>AI LAB</div>', unsafe_allow_html=True)
    st.markdown('<div class="cp-sub">AI RESEARCH CENTER · 2026</div>', unsafe_allow_html=True)
    st.divider()

    # API 키 (secrets 우선, 사이드바 오버라이드)
    st.markdown("##### 🔐 API 설정")
    _sn = _secret("NOTION_TOKEN");  _so = _secret("OPENAI_API_KEY")
    notion_input = st.text_input("🔑 Notion Token", type="password",
        placeholder="secret 자동사용 중" if _sn else "secret_xxx 입력 필요")
    openai_input = st.text_input("🤖 OpenAI API Key", type="password",
        placeholder="secret 자동사용 중" if _so else "sk-xxx 입력 필요")
    notion_token = notion_input or _sn
    openai_key   = openai_input or _so

    def _kbadge(label, val, ovr):
        if not val:  return f'<span class="key-no">✗ {label} 미설정</span>'
        if ovr:      return f'<span class="key-ovr">⚡ {label} 오버라이드</span>'
        return f'<span class="key-ok">✓ {label} secrets 연결</span>'
    st.markdown(_kbadge("Notion", notion_token, bool(notion_input)) + "<br>" +
                _kbadge("OpenAI", openai_key,   bool(openai_input)), unsafe_allow_html=True)

    st.divider()
    st.markdown("##### 🧠 AI 모델")
    MODEL_MAP = {
        "gpt-4o  ★ 균형·추천":       "gpt-4o",
        "gpt-4o-mini  빠름·저비용":  "gpt-4o-mini",
        "o3  ★★ 고추론·최강":        "o3",
        "o4-mini  추론·경량":         "o4-mini",
    }
    selected_model = MODEL_MAP[st.selectbox("모델", list(MODEL_MAP.keys()))]

    # Notion 결과 저장용 페이지 ID
    st.divider()
    _sp = _secret("NOTION_SAVE_PAGE_ID")
    save_page_input = st.text_input("📄 AI 결과 저장 페이지 ID",
        placeholder="secret 자동사용 중" if _sp else "결과 저장할 페이지 ID")
    save_page_id = save_page_input or _sp

    st.markdown(f'<div style="font-family:Orbitron,monospace;font-size:0.7rem;color:#334455;margin-top:12px;">{datetime.now().strftime("%Y.%m.%d %H:%M")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 클라이언트
# ══════════════════════════════════════════════════════════════
notion = Client(auth=notion_token) if notion_token else None
oai    = OpenAI(api_key=openai_key) if openai_key   else None

# ══════════════════════════════════════════════════════════════
# Notion 페이지 읽기 — 텍스트 + 링크/파일 분리 추출
# ══════════════════════════════════════════════════════════════
def extract_page(page_id: str) -> dict:
    """
    Returns:
        text  : 본문 텍스트 (줄바꿈 포함)
        links : [{label, url}] 링크/첨부파일 목록
        title : 페이지 제목
    """
    if not notion:
        return {"title":"", "text":"⚠️ Notion 미연결", "links":[]}

    # 페이지 제목
    try:
        page = notion.pages.retrieve(page_id=page_id)
        props = page.get("properties", {})
        title = ""
        for v in props.values():
            if v.get("type") == "title" and v["title"]:
                title = v["title"][0]["plain_text"]; break
    except Exception as e:
        return {"title":"", "text":f"❌ 페이지 읽기 실패: {e}", "links":[]}

    # 블록 순회
    text_lines = []
    links      = []

    def _rich(rich_text_list):
        return "".join(t.get("plain_text","") for t in rich_text_list)

    def _traverse(block_id, depth=0):
        try:
            res = notion.blocks.children.list(block_id=block_id)
        except:
            return
        for b in res.get("results", []):
            bt = b["type"]
            indent = "  " * depth

            # ── 텍스트 계열 블록 ──────────────────────────
            if bt in ("paragraph","heading_1","heading_2","heading_3",
                       "bulleted_list_item","numbered_list_item",
                       "toggle","quote","callout","to_do"):
                rt = b[bt].get("rich_text", [])
                line = _rich(rt)
                if line.strip():
                    prefix = {"heading_1":"# ","heading_2":"## ","heading_3":"### ",
                               "bulleted_list_item":f"{indent}• ",
                               "numbered_list_item":f"{indent}1. ",
                               "quote":f"{indent}> ","callout":f"{indent}💡 "}.get(bt, indent)
                    text_lines.append(prefix + line)
                    # 인라인 링크 수집
                    for t in rt:
                        href = t.get("href") or (t.get("text",{}).get("link") or {}).get("url","")
                        if href:
                            links.append({"label": t.get("plain_text","링크"), "url": href})

            # ── 링크 미리보기 / 북마크 ─────────────────────
            elif bt in ("bookmark","link_preview","embed"):
                url = b[bt].get("url","")
                cap = _rich(b[bt].get("caption",[]))
                if url:
                    links.append({"label": cap or url, "url": url})
                    text_lines.append(f"{indent}🔗 {cap or url}")

            # ── 파일 / 이미지 / PDF ────────────────────────
            elif bt in ("file","image","pdf","video","audio"):
                inner = b[bt]
                url = inner.get("file",{}).get("url","") or inner.get("external",{}).get("url","")
                cap = _rich(inner.get("caption",[]))
                label = cap or bt.upper()
                if url:
                    links.append({"label": f"[{bt.upper()}] {label}", "url": url})
                    text_lines.append(f"{indent}📎 {label}")

            # ── 테이블 ────────────────────────────────────
            elif bt == "table":
                _traverse(b["id"], depth + 1)

            elif bt == "table_row":
                cells = b["table_row"].get("cells", [])
                row_text = " | ".join(_rich(c) for c in cells)
                if row_text.strip():
                    text_lines.append(f"{indent}{row_text}")

            # ── 코드 ──────────────────────────────────────
            elif bt == "code":
                lang = b["code"].get("language","")
                code = _rich(b["code"].get("rich_text",[]))
                text_lines.append(f"\n```{lang}\n{code}\n```\n")

            # ── 구분선 ────────────────────────────────────
            elif bt == "divider":
                text_lines.append("─" * 40)

            # ── 하위 블록 재귀 ────────────────────────────
            if b.get("has_children"):
                _traverse(b["id"], depth + 1)

    _traverse(page_id)
    return {
        "title": title,
        "text":  "\n".join(text_lines) if text_lines else "(내용 없음)",
        "links": links
    }

# ══════════════════════════════════════════════════════════════
# AI 호출
# ══════════════════════════════════════════════════════════════
def call_ai(system: str, user: str) -> str:
    if not oai:
        return "⚠️ OpenAI API Key가 설정되지 않았습니다."
    kwargs = dict(model=selected_model,
                  messages=[{"role":"system","content":system},
                             {"role":"user","content":user}])
    if selected_model in ("o3","o4-mini"):
        kwargs["max_completion_tokens"] = 2000
    else:
        kwargs["max_tokens"] = 2000
    return oai.chat.completions.create(**kwargs).choices[0].message.content

def save_to_notion(title: str, content: str) -> bool:
    if not notion or not save_page_id:
        return False
    notion.blocks.children.append(
        block_id=save_page_id,
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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 전체 현황",
    "📄 Notion 읽기",
    "👤 개인 AI 검토",
    "🤖 일괄 처리",
    "⚙️ 멤버 관리"
])

# ════════════════════════════════════════════════════════════
# TAB 1: 전체 현황
# ════════════════════════════════════════════════════════════
with tab1:
    members = st.session_state.members
    total   = len(members)
    done    = sum(1 for m in members if m["상태"]=="검토완료")
    ongoing = sum(1 for m in members if m["상태"]=="검토중")
    pending = sum(1 for m in members if m["상태"]=="미검토")
    linked  = sum(1 for m in members if m.get("notion_page_id",""))

    c1,c2,c3,c4,c5 = st.columns(5)
    for col,(label,val,color) in zip([c1,c2,c3,c4,c5],[
        ("전체",       total,  "#00f5ff"),
        ("Notion 연결",linked, "#00aaff"),
        ("검토완료",   done,   "#00ff88"),
        ("검토중",     ongoing,"#ffcc00"),
        ("미검토",     pending,"#cc66ff"),
    ]):
        col.markdown(
            f'<div class="stat-box"><div class="stat-number" style="color:{color};text-shadow:0 0 12px {color}66;">{val}</div>'
            f'<div class="stat-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="cp-divider">', unsafe_allow_html=True)
    st.markdown("### 📋 멤버별 주업무 현황표")

    rows = ""
    for m in members:
        badge     = STATUS_BADGE.get(m["상태"],"badge-none")
        emoji     = STATUS_EMOJI.get(m["상태"],"")
        notion_lk = "✦" if m.get("notion_page_id") else '<span style="color:#334455;">—</span>'
        ai_mark   = '<span style="color:#00f5ff;">✦</span>' if m["이름"] in st.session_state.ai_outputs else '<span style="color:#334455;">—</span>'
        rows += (
            f'<tr><td><span class="member-name">{m["이름"]}</span></td>'
            f'<td style="color:#667788;font-size:0.8rem;">{m["직급"]}</td>'
            f'<td style="color:#8ab4cc;">{m["주업무"]}</td>'
            f'<td style="color:#667788;font-size:0.8rem;">{m["세부"]}</td>'
            f'<td style="text-align:center;color:#00aaff;">{notion_lk}</td>'
            f'<td><span class="{badge}">{emoji} {m["상태"]}</span></td>'
            f'<td style="text-align:center;">{ai_mark}</td></tr>'
        )
    st.markdown(
        '<table class="cp-table"><thead><tr>'
        '<th>이름</th><th>직급</th><th>주업무</th><th>세부</th>'
        '<th>Notion</th><th>검토상태</th><th>AI요약</th>'
        f'</tr></thead><tbody>{rows}</tbody></table>', unsafe_allow_html=True)

    # 전체 보고서
    st.markdown('<hr class="cp-divider">', unsafe_allow_html=True)
    st.markdown("### 📝 전체 팀 AI 종합보고서")
    if st.button("🚀 종합보고서 생성", use_container_width=True):
        parts = []
        for m in members:
            nc = st.session_state.notion_contents.get(m["이름"], {})
            notion_text = nc.get("text","(Notion 미연동)")[:1500]
            parts.append(
                f"▶ {m['이름']} ({m['직급']})\n"
                f"  주업무: {m['주업무']} / {m['세부']}\n"
                f"  Notion 내용:\n{notion_text}\n"
            )
        with st.spinner("AI 보고서 작성 중..."):
            report = call_ai(
                "당신은 K-water AI연구소 소장입니다. "
                "팀원별 Notion 업무 내용을 분석해 2026년 전체 팀 업무현황 보고서를 작성하세요. "
                "형식: [개요] → [멤버별 핵심업무 요약] → [팀 연구 시너지 분석] → [소장 종합의견 및 지시사항]",
                "\n\n".join(parts)
            )
        st.session_state["team_report"] = report

    if "team_report" in st.session_state:
        st.markdown(f'<div class="ai-result">{st.session_state["team_report"]}</div>', unsafe_allow_html=True)
        if st.button("💾 Notion 저장", key="save_team"):
            if save_to_notion(f"[AI종합보고서] {datetime.now().strftime('%Y.%m.%d')}", st.session_state["team_report"]):
                st.success("✅ Notion 저장 완료!")
            else:
                st.warning("저장 페이지 ID를 사이드바에서 확인해주세요.")

# ════════════════════════════════════════════════════════════
# TAB 2: Notion 페이지 읽기 (멤버 페이지 ID 등록 + 내용 확인)
# ════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 📄 멤버별 Notion 페이지 연결 및 내용 확인")
    st.caption("각 멤버의 Notion 페이지 URL 마지막 32자리를 입력하세요.")

    members = st.session_state.members

    for i, m in enumerate(members):
        with st.expander(f"{'🟢' if m.get('notion_page_id') else '⚪'} {m['이름']} ({m['직급']})"):
            col_a, col_b = st.columns([4, 1])

            # 페이지 ID 입력
            pid = col_a.text_input(
                "Notion 페이지 ID",
                value=m.get("notion_page_id",""),
                placeholder="예: 30531c568f2f81178b54cd7ee19097a7",
                key=f"pid_{i}"
            )
            if col_b.button("저장", key=f"pid_save_{i}", use_container_width=True):
                st.session_state.members[i]["notion_page_id"] = pid.strip().replace("-","")
                st.success("저장됨")
                st.rerun()

            # 내용 읽기 버튼
            cur_pid = m.get("notion_page_id","")
            if cur_pid:
                c1, c2 = st.columns(2)
                if c1.button(f"📥 내용 불러오기", key=f"load_{i}", use_container_width=True):
                    with st.spinner(f"{m['이름']} 페이지 읽는 중..."):
                        result = extract_page(cur_pid)
                    st.session_state.notion_contents[m["이름"]] = result
                    st.session_state.members[i]["상태"] = "검토중"
                    st.success(f"✅ 불러오기 완료 — 제목: {result['title'] or '(없음)'}")
                    st.rerun()

                if c2.button(f"🗑️ 캐시 초기화", key=f"clear_{i}", use_container_width=True):
                    st.session_state.notion_contents.pop(m["이름"], None)
                    st.rerun()

            # 읽어온 내용 표시
            nc = st.session_state.notion_contents.get(m["이름"])
            if nc:
                st.markdown(f"**📌 페이지 제목**: `{nc.get('title','—')}`")

                st.markdown("**📝 본문 내용**")
                st.markdown(f'<div class="notion-raw">{nc["text"]}</div>', unsafe_allow_html=True)

                if nc.get("links"):
                    st.markdown("**🔗 링크 / 첨부파일**")
                    link_html = "".join(
                        f'<div>• <a href="{lk["url"]}" target="_blank">{lk["label"]}</a></div>'
                        for lk in nc["links"]
                    )
                    st.markdown(f'<div class="attach-box">{link_html}</div>', unsafe_allow_html=True)
            elif cur_pid:
                st.info("'내용 불러오기' 버튼을 눌러주세요.")

    # 전체 일괄 불러오기
    st.markdown('<hr class="cp-divider">', unsafe_allow_html=True)
    linked_members = [m for m in st.session_state.members if m.get("notion_page_id","")]
    st.caption(f"Notion 연결된 멤버: {len(linked_members)}명 / 전체 {len(st.session_state.members)}명")
    if st.button("📥 연결된 전체 멤버 일괄 불러오기", use_container_width=True):
        if not notion:
            st.warning("Notion Token을 확인해주세요.")
        elif not linked_members:
            st.warning("먼저 멤버별 페이지 ID를 등록해주세요.")
        else:
            prog = st.progress(0, text="불러오는 중...")
            for i, m in enumerate(linked_members):
                result = extract_page(m["notion_page_id"])
                st.session_state.notion_contents[m["이름"]] = result
                idx = [x["이름"] for x in st.session_state.members].index(m["이름"])
                st.session_state.members[idx]["상태"] = "검토중"
                prog.progress((i+1)/len(linked_members), text=f"{m['이름']} 완료...")
            st.success(f"✅ {len(linked_members)}명 Notion 내용 로드 완료!")
            st.rerun()

# ════════════════════════════════════════════════════════════
# TAB 3: 개인 AI 검토
# ════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 👤 개인 업무 AI 검토")

    members  = st.session_state.members
    names    = [m["이름"] for m in members]
    sel_name = st.selectbox("멤버 선택", names, key="tab3_select")
    m_idx    = names.index(sel_name)
    member   = members[m_idx]
    nc       = st.session_state.notion_contents.get(sel_name, {})

    col_l, col_r = st.columns([3, 1])
    with col_l:
        st.markdown(
            f'<div class="member-card">'
            f'<div class="member-name">{member["이름"]}</div>'
            f'<div class="member-role">{member["직급"]} · K-water AI연구소</div>'
            f'</div>', unsafe_allow_html=True)
        if nc.get("title"):
            st.caption(f"📄 Notion 페이지: **{nc['title']}**")

    with col_r:
        badge = STATUS_BADGE.get(member["상태"],"badge-none")
        emoji = STATUS_EMOJI.get(member["상태"],"")
        st.markdown(
            f'<div style="text-align:center;margin-top:24px;">'
            f'<span class="{badge}" style="font-size:1rem;padding:8px 20px;">{emoji} {member["상태"]}</span>'
            f'</div>', unsafe_allow_html=True)

    # Notion 내용 미리보기
    if nc.get("text"):
        with st.expander("📄 Notion 원문 보기"):
            st.markdown(f'<div class="notion-raw">{nc["text"]}</div>', unsafe_allow_html=True)
            if nc.get("links"):
                link_html = "".join(f'<div>• <a href="{lk["url"]}" target="_blank">{lk["label"]}</a></div>' for lk in nc["links"])
                st.markdown(f'<div class="attach-box">{link_html}</div>', unsafe_allow_html=True)
    else:
        st.info("💡 Tab2에서 이 멤버의 Notion 내용을 먼저 불러와주세요.")

    st.divider()

    # AI 검토 설정
    style_sel = st.selectbox("검토 관점", [
        "소장 검토 보고서  (업무요약·강점·개선·코멘트)",
        "3줄 핵심요약",
        "연구 성과 중심 평가",
        "타 부서 협업 방안 제안",
        "2026년 추진과제 도출",
    ], key="tab3_style")
    custom_q  = st.text_input("추가 검토 포인트 (선택)", placeholder="예: 예산 대비 성과는?")

    STYLE_SYS = {
        "소장 검토 보고서  (업무요약·강점·개선·코멘트)":
            "[업무핵심요약] [강점분석] [개선제안] [소장코멘트] 형식으로 작성하세요.",
        "3줄 핵심요약": "3줄로 핵심만 요약하세요.",
        "연구 성과 중심 평가": "연구 성과, 기술 기여도 중심으로 평가하고 향후 방향을 제시하세요.",
        "타 부서 협업 방안 제안": "다른 팀·부서와의 시너지 협업 방안 3가지를 제안하세요.",
        "2026년 추진과제 도출": "내용을 바탕으로 2026년 중점 추진과제 3가지를 구체적으로 도출하세요.",
    }

    if st.button(f"✨ {sel_name} AI 검토 실행", use_container_width=True):
        notion_text = nc.get("text","(Notion 내용 없음 — 기본 업무 정보로 분석)")
        notion_links = "\n".join(f"- {lk['label']}: {lk['url']}" for lk in nc.get("links",[]))
        prompt = (
            f"이름: {member['이름']} ({member['직급']})\n"
            f"주업무: {member['주업무']}\n세부: {member['세부']}\n\n"
            f"=== Notion 업무 내용 ===\n{notion_text[:3000]}\n\n"
            f"=== 첨부 링크 ===\n{notion_links or '없음'}\n\n"
            f"추가질문: {custom_q or '없음'}"
        )
        with st.spinner("AI 분석 중..."):
            result = call_ai(
                f"당신은 K-water AI연구소 소장입니다. {STYLE_SYS[style_sel]}",
                prompt
            )
        st.session_state.ai_outputs[sel_name] = result
        st.session_state.members[m_idx]["상태"] = "검토완료"

    if sel_name in st.session_state.ai_outputs:
        st.markdown(f'<div class="ai-result">{st.session_state.ai_outputs[sel_name]}</div>', unsafe_allow_html=True)
        if st.button("💾 Notion 저장", use_container_width=True, key="save_tab3"):
            title = f"[AI검토] {sel_name} · {datetime.now().strftime('%Y.%m.%d')}"
            if save_to_notion(title, st.session_state.ai_outputs[sel_name]):
                st.success("✅ Notion 저장 완료!")
            else:
                st.warning("저장 페이지 ID를 사이드바에서 확인해주세요.")

# ════════════════════════════════════════════════════════════
# TAB 4: 일괄 처리 (읽기 + AI 요약 한번에)
# ════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🤖 전체 멤버 일괄 처리")
    st.caption("Notion 읽기 → AI 요약 → 상태 자동 업데이트를 한 번에 실행합니다.")

    col_a, col_b = st.columns(2)
    linked_names = [m["이름"] for m in st.session_state.members if m.get("notion_page_id","")]
    target = col_a.multiselect(
        "대상 멤버 (Notion 연결된 멤버만 표시)",
        linked_names,
        default=linked_names
    )
    batch_style = col_b.selectbox("AI 요약 스타일", [
        "소장 검토 보고서", "3줄 핵심요약", "강점·보완점 분석", "2026년 추진과제 도출"
    ])
    BATCH_SYS = {
        "소장 검토 보고서":      "[업무요약][강점][개선사항][종합의견] 형식으로 작성하세요.",
        "3줄 핵심요약":          "3줄로 핵심만 요약하세요.",
        "강점·보완점 분석":      "[강점 3가지] [보완점 2가지] [액션아이템] 형식으로 작성하세요.",
        "2026년 추진과제 도출":  "2026년 중점 추진과제 3가지를 구체적으로 도출하세요.",
    }

    if st.button("🚀 일괄 실행 (Notion 읽기 + AI 요약)", use_container_width=True):
        if not notion:
            st.warning("Notion Token을 확인해주세요.")
        elif not oai:
            st.warning("OpenAI API Key를 확인해주세요.")
        elif not target:
            st.warning("대상 멤버를 선택해주세요.")
        else:
            prog = st.progress(0, text="처리 중...")
            target_members = [m for m in st.session_state.members if m["이름"] in target]
            for i, m in enumerate(target_members):
                # STEP 1: Notion 읽기
                prog.progress((i*2)/(len(target_members)*2), text=f"📥 {m['이름']} Notion 읽는 중...")
                nc = extract_page(m["notion_page_id"])
                st.session_state.notion_contents[m["이름"]] = nc

                # STEP 2: AI 요약
                prog.progress((i*2+1)/(len(target_members)*2), text=f"🤖 {m['이름']} AI 분석 중...")
                notion_text  = nc.get("text","")[:3000]
                notion_links = "\n".join(f"- {lk['label']}: {lk['url']}" for lk in nc.get("links",[]))
                prompt = (
                    f"이름: {m['이름']} ({m['직급']})\n"
                    f"주업무: {m['주업무']}\n세부: {m['세부']}\n\n"
                    f"=== Notion 업무 내용 ===\n{notion_text}\n\n"
                    f"=== 첨부 링크 ===\n{notion_links or '없음'}"
                )
                result = call_ai(
                    f"당신은 K-water AI연구소 소장입니다. {BATCH_SYS[batch_style]}",
                    prompt
                )
                st.session_state.ai_outputs[m["이름"]] = result
                idx = [x["이름"] for x in st.session_state.members].index(m["이름"])
                st.session_state.members[idx]["상태"] = "검토완료"

            prog.progress(1.0, text="완료!")
            st.success(f"✅ {len(target)}명 처리 완료!")
            st.rerun()

    st.markdown('<hr class="cp-divider">', unsafe_allow_html=True)

    if st.session_state.ai_outputs:
        for name, output in st.session_state.ai_outputs.items():
            nc = st.session_state.notion_contents.get(name, {})
            with st.expander(f"✦  {name} — AI 검토 결과 {'| '+nc['title'] if nc.get('title') else ''}"):
                st.markdown(f'<div class="ai-result">{output}</div>', unsafe_allow_html=True)
                if st.button(f"💾 Notion 저장", key=f"batch_save_{name}"):
                    if save_to_notion(f"[AI검토] {name} · {datetime.now().strftime('%Y.%m.%d')}", output):
                        st.success("저장 완료!")
    else:
        st.info("아직 AI 요약 결과가 없습니다.")

# ════════════════════════════════════════════════════════════
# TAB 5: 멤버 관리
# ════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### ⚙️ 멤버 추가 / 삭제")
    with st.expander("➕ 새 멤버 추가"):
        c1,c2 = st.columns(2)
        nn = c1.text_input("이름"); nr = c2.selectbox("직급", ["수석","선임","연구원","인턴"])
        nj = st.text_input("주업무"); nd = st.text_area("세부내용", height=70)
        np_id = st.text_input("Notion 페이지 ID (선택)")
        if st.button("➕ 추가", use_container_width=True):
            if nn and nj:
                st.session_state.members.append(
                    {"이름":nn,"직급":nr,"주업무":nj,"세부":nd,"상태":"미검토",
                     "notion_page_id":np_id.strip().replace("-","")})
                st.success(f"{nn} 추가 완료!")
                st.rerun()

    with st.expander("🗑️ 멤버 삭제"):
        del_name = st.selectbox("삭제 대상", [m["이름"] for m in st.session_state.members])
        if st.button("🗑️ 삭제", use_container_width=True):
            st.session_state.members = [m for m in st.session_state.members if m["이름"] != del_name]
            st.session_state.ai_outputs.pop(del_name, None)
            st.session_state.notion_contents.pop(del_name, None)
            st.success(f"{del_name} 삭제 완료")
            st.rerun()

    st.divider()
    if st.button("🔄 기본값으로 초기화", use_container_width=True):
        st.session_state.members         = [m.copy() for m in DEFAULT_MEMBERS]
        st.session_state.ai_outputs      = {}
        st.session_state.notion_contents = {}
        st.success("초기화 완료")
        st.rerun()

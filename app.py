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
# CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Noto+Sans+KR:wght@300;400;700&display=swap');
html,body,[class*="css"]{ font-family:'Noto Sans KR',sans-serif; background:#0a0e1a; color:#c8d8f0; }
.stApp{ background:#0a0e1a; }
.cp-header{ font-family:'Orbitron',monospace; font-size:1.5rem; font-weight:900; color:#00f5ff;
  text-shadow:0 0 20px #00f5ff88; letter-spacing:3px;
  border-bottom:1px solid #00f5ff44; padding-bottom:8px; margin-bottom:4px; }
.cp-sub{ font-size:0.78rem; color:#5a7a9a; letter-spacing:2px; margin-bottom:20px; }
.cp-divider{ border:none; border-top:1px solid #1e3a5f; margin:16px 0; }

/* 멤버 카드 */
.member-card{ background:linear-gradient(135deg,#0d1526,#111d30);
  border:1px solid #1e3a5f; border-left:3px solid #00f5ff;
  border-radius:6px; padding:14px 18px; margin:4px 0; }
.member-name{ font-family:'Orbitron',monospace; font-size:0.9rem; color:#00f5ff; font-weight:700; }
.member-role{ font-size:0.8rem; color:#8ab4cc; margin-top:2px; }

/* Notion 탐색 카드 */
.notion-page-card{ background:#0d1526; border:1px solid #1e3a5f; border-radius:6px;
  padding:12px 16px; margin:4px 0; display:flex; align-items:center; gap:12px; }
.notion-page-title{ color:#c8d8f0; font-size:0.88rem; }
.notion-page-id{ color:#334455; font-size:0.72rem; font-family:monospace; }
.notion-page-url a{ color:#00aaff; font-size:0.75rem; text-decoration:none; }

/* 뱃지 */
.badge-done   { background:#003322; color:#00ff88; border:1px solid #00ff88; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-family:'Orbitron',monospace; }
.badge-review { background:#1a1a00; color:#ffcc00; border:1px solid #ffcc00; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-family:'Orbitron',monospace; }
.badge-pending{ background:#1a0022; color:#cc66ff; border:1px solid #cc66ff; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-family:'Orbitron',monospace; }
.badge-none   { background:#111;    color:#556677; border:1px solid #334455; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-family:'Orbitron',monospace; }
.key-ok { background:#003322; color:#00ff88; border:1px solid #00ff88; border-radius:4px; padding:3px 10px; font-size:0.72rem; font-family:'Orbitron',monospace; }
.key-no { background:#1a0000; color:#ff4466; border:1px solid #ff4466; border-radius:4px; padding:3px 10px; font-size:0.72rem; font-family:'Orbitron',monospace; }
.key-ovr{ background:#1a1a00; color:#ffcc00; border:1px solid #ffcc00; border-radius:4px; padding:3px 10px; font-size:0.72rem; font-family:'Orbitron',monospace; }

/* 콘텐츠 */
.notion-raw{ background:#060f1c; border:1px solid #1e3a5f; border-left:3px solid #334466;
  border-radius:6px; padding:16px; font-size:0.82rem; line-height:1.9; color:#8ab4cc;
  white-space:pre-wrap; max-height:300px; overflow-y:auto; }
.attach-box{ background:#071525; border:1px solid #1e3a5f; border-radius:6px;
  padding:12px 16px; font-size:0.8rem; color:#7a9ab8; margin-top:8px; }
.attach-box a{ color:#00f5ff; text-decoration:none; }
.ai-result{ background:#071020; border:1px solid #00f5ff33; border-radius:8px;
  padding:18px; font-size:0.9rem; line-height:1.8; white-space:pre-wrap; color:#b0d4e8; }
.stat-box{ background:linear-gradient(135deg,#0d1526,#0a1a2e); border:1px solid #1e3a5f;
  border-radius:8px; padding:16px; text-align:center; }
.stat-number{ font-family:'Orbitron',monospace; font-size:2rem; font-weight:900;
  color:#00f5ff; text-shadow:0 0 12px #00f5ff66; }
.stat-label{ font-size:0.72rem; color:#5a7a9a; letter-spacing:1px; margin-top:4px; }
.cp-table{ width:100%; border-collapse:collapse; font-size:0.85rem; }
.cp-table th{ background:#0d1a2e; color:#00f5ff; font-family:'Orbitron',monospace;
  font-size:0.72rem; letter-spacing:2px; padding:10px 14px; border-bottom:1px solid #00f5ff44; text-align:left; }
.cp-table td{ padding:10px 14px; border-bottom:1px solid #1e3a5f; color:#b0c8e0; vertical-align:top; }
.cp-table tr:hover td{ background:#0d1830; }
.info-box{ background:#071525; border:1px solid #00aaff44; border-left:3px solid #00aaff;
  border-radius:6px; padding:12px 16px; font-size:0.85rem; color:#8ab4cc; margin:8px 0; }

/* Streamlit */
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

STATUS_OPTIONS = ["미검토","검토중","검토완료","보류"]
STATUS_BADGE   = {"검토완료":"badge-done","검토중":"badge-review","미검토":"badge-pending","보류":"badge-none"}
STATUS_EMOJI   = {"검토완료":"✅","검토중":"🔄","미검토":"🕐","보류":"⏸️"}

# ── 세션 초기화 ────────────────────────────────────────────
if "members"          not in st.session_state: st.session_state.members          = []   # [{이름,직급,주업무,세부,상태,notion_page_id,notion_url}]
if "ai_outputs"       not in st.session_state: st.session_state.ai_outputs       = {}
if "notion_contents"  not in st.session_state: st.session_state.notion_contents  = {}
if "discovered_pages" not in st.session_state: st.session_state.discovered_pages = []   # 탐색된 Notion 페이지 목록

# ══════════════════════════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    LOGO_URL = "https://raw.githubusercontent.com/newcave/2026NotionKWAI/main/AI%EC%97%B0%EA%B5%AC%EC%86%8C%EB%A1%9C%EA%B3%A0_%EC%82%AC%EC%9D%B4%EB%B2%84%ED%8E%91%ED%81%AC1%EB%B2%88.png"
    st.markdown(f'<div style="text-align:center;margin-bottom:16px;"><img src="{LOGO_URL}" onerror="this.style.display=\'none\'" style="width:150px;border-radius:8px;border:1px solid #00f5ff44;" /></div>', unsafe_allow_html=True)
    st.markdown('<div class="cp-header" style="font-size:1rem;">K-WATER<br>AI LAB</div>', unsafe_allow_html=True)
    st.markdown('<div class="cp-sub">AI RESEARCH CENTER · 2026</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown("##### 🔐 API 설정")
    _sn = _secret("NOTION_TOKEN"); _so = _secret("OPENAI_API_KEY")
    notion_input = st.text_input("🔑 Notion Token", type="password",
        placeholder="secret 자동사용 중" if _sn else "secret_xxx 입력 필요")
    openai_input = st.text_input("🤖 OpenAI API Key", type="password",
        placeholder="secret 자동사용 중" if _so else "sk-xxx 입력 필요")
    notion_token = notion_input or _sn
    openai_key   = openai_input or _so

    def _kbadge(label, val, ovr):
        if not val:  return f'<span class="key-no">✗ {label} 미설정</span>'
        if ovr:      return f'<span class="key-ovr">⚡ {label} 오버라이드</span>'
        return f'<span class="key-ok">✓ {label} 연결됨</span>'
    st.markdown(_kbadge("Notion", notion_token, bool(notion_input)) + "<br>" +
                _kbadge("OpenAI", openai_key,   bool(openai_input)), unsafe_allow_html=True)

    st.divider()
    st.markdown("##### 🧠 AI 모델")
    MODEL_MAP = {
        "gpt-4o  ★ 균형·추천":      "gpt-4o",
        "gpt-4o-mini  빠름·저비용": "gpt-4o-mini",
        "o3  ★★ 고추론·최강":       "o3",
        "o4-mini  추론·경량":        "o4-mini",
    }
    selected_model = MODEL_MAP[st.selectbox("모델", list(MODEL_MAP.keys()))]

    st.divider()
    _sp = _secret("NOTION_SAVE_PAGE_ID")
    save_page_input = st.text_input("📄 AI 결과 저장 페이지 ID",
        placeholder="secret 자동사용 중" if _sp else "저장 페이지 ID")
    save_page_id = save_page_input or _sp

    st.markdown(f'<div style="font-family:Orbitron,monospace;font-size:0.7rem;color:#334455;margin-top:12px;">{datetime.now().strftime("%Y.%m.%d %H:%M")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 클라이언트
# ══════════════════════════════════════════════════════════════
notion = Client(auth=notion_token) if notion_token else None
oai    = OpenAI(api_key=openai_key) if openai_key   else None

# ══════════════════════════════════════════════════════════════
# Notion 유틸
# ══════════════════════════════════════════════════════════════
def get_page_title(page: dict) -> str:
    """페이지 객체에서 제목 추출"""
    props = page.get("properties", {})
    for v in props.values():
        if v.get("type") == "title" and v.get("title"):
            return v["title"][0]["plain_text"]
    # child_page 타입
    if page.get("object") == "block" and page.get("type") == "child_page":
        return page["child_page"].get("title", "(제목없음)")
    return "(제목없음)"

def discover_notion_pages(query: str = "") -> list:
    """
    Notion integration이 접근 가능한 모든 페이지 탐색.
    Returns: [{id, title, url, last_edited}]
    """
    if not notion:
        return []
    results = []
    try:
        resp = notion.search(
            query=query,
            filter={"property": "object", "value": "page"},
            sort={"direction": "descending", "timestamp": "last_edited_time"}
        )
        for p in resp.get("results", []):
            title = get_page_title(p)
            results.append({
                "id":          p["id"].replace("-",""),
                "id_fmt":      p["id"],          # 하이픈 있는 형태 (표시용)
                "title":       title,
                "url":         p.get("url",""),
                "last_edited": p.get("last_edited_time","")[:10],
                "icon":        p.get("icon",{}).get("emoji","📄") if p.get("icon",{}) else "📄",
            })
    except Exception as e:
        st.error(f"Notion 탐색 오류: {e}")
    return results

def extract_page(page_id: str) -> dict:
    """페이지 전체 내용 추출 (텍스트 + 링크/파일)"""
    if not notion:
        return {"title":"", "text":"⚠️ Notion 미연결", "links":[]}
    try:
        page  = notion.pages.retrieve(page_id=page_id)
        title = get_page_title(page)
    except Exception as e:
        return {"title":"", "text":f"❌ 페이지 읽기 실패: {e}", "links":[]}

    text_lines, links = [], []

    def _rich(rt): return "".join(t.get("plain_text","") for t in rt)

    def _traverse(bid, depth=0):
        try: res = notion.blocks.children.list(block_id=bid)
        except: return
        indent = "  " * depth
        for b in res.get("results", []):
            bt = b["type"]
            if bt in ("paragraph","heading_1","heading_2","heading_3",
                       "bulleted_list_item","numbered_list_item",
                       "toggle","quote","callout","to_do"):
                rt   = b[bt].get("rich_text", [])
                line = _rich(rt)
                if line.strip():
                    pfx = {"heading_1":"# ","heading_2":"## ","heading_3":"### ",
                            "bulleted_list_item":f"{indent}• ",
                            "numbered_list_item":f"{indent}1. ",
                            "quote":f"{indent}> ","callout":f"{indent}💡 "}.get(bt, indent)
                    text_lines.append(pfx + line)
                for t in rt:
                    href = (t.get("text",{}).get("link") or {}).get("url","")
                    if href: links.append({"label": t.get("plain_text","링크"), "url": href})
            elif bt in ("bookmark","link_preview","embed"):
                url = b[bt].get("url","")
                cap = _rich(b[bt].get("caption",[]))
                if url:
                    links.append({"label": cap or url, "url": url})
                    text_lines.append(f"{indent}🔗 {cap or url}")
            elif bt in ("file","image","pdf","video","audio"):
                inner = b[bt]
                url   = inner.get("file",{}).get("url","") or inner.get("external",{}).get("url","")
                cap   = _rich(inner.get("caption",[]))
                label = cap or bt.upper()
                if url:
                    links.append({"label": f"[{bt.upper()}] {label}", "url": url})
                    text_lines.append(f"{indent}📎 {label}")
            elif bt == "table_row":
                cells = b["table_row"].get("cells", [])
                row   = " | ".join(_rich(c) for c in cells)
                if row.strip(): text_lines.append(f"{indent}{row}")
            elif bt == "code":
                lang = b["code"].get("language","")
                code = _rich(b["code"].get("rich_text",[]))
                text_lines.append(f"\n```{lang}\n{code}\n```\n")
            elif bt == "divider":
                text_lines.append("─" * 36)
            if b.get("has_children"):
                _traverse(b["id"], depth+1)

    _traverse(page_id)
    return {
        "title": title,
        "text":  "\n".join(text_lines) if text_lines else "(내용 없음)",
        "links": links
    }

def call_ai(system: str, user: str) -> str:
    if not oai: return "⚠️ OpenAI API Key가 설정되지 않았습니다."
    kwargs = dict(model=selected_model,
                  messages=[{"role":"system","content":system},{"role":"user","content":user}])
    if selected_model in ("o3","o4-mini"): kwargs["max_completion_tokens"] = 2000
    else:                                   kwargs["max_tokens"]            = 2000
    return oai.chat.completions.create(**kwargs).choices[0].message.content

def save_to_notion(title: str, content: str) -> bool:
    if not notion or not save_page_id: return False
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

# ══════════════════════════════════════════════════════════════
# ❶ 첫 화면: Notion 연결 안 된 경우 or 멤버 없는 경우
# ══════════════════════════════════════════════════════════════
if not notion_token:
    st.markdown("""
    <div class="info-box">
    🔑 사이드바에서 <b>Notion Internal Token</b>을 입력하면 연결된 페이지를 자동으로 탐색합니다.
    </div>""", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════
# ❷ Notion 페이지 탐색 & 멤버 등록 (멤버가 없을 때 안내)
# ══════════════════════════════════════════════════════════════
if not st.session_state.members:
    st.markdown("""
    <div class="info-box">
    💡 <b>Notion에서 멤버 페이지를 자동 탐색</b>합니다.<br>
    Integration이 연결된 페이지 목록을 불러온 뒤, 멤버로 등록할 페이지를 선택하세요.
    </div>""", unsafe_allow_html=True)

    col_search, col_btn = st.columns([3,1])
    search_q = col_search.text_input("검색어 (선택)", placeholder="이름, 업무 키워드 등... 비워두면 전체 탐색")
    if col_btn.button("🔍 Notion 페이지 탐색", use_container_width=True):
        with st.spinner("Notion 페이지 탐색 중..."):
            pages = discover_notion_pages(search_q)
        st.session_state.discovered_pages = pages
        if not pages:
            st.warning("탐색된 페이지가 없습니다. Integration이 페이지에 연결되었는지 확인해주세요.")

    if st.session_state.discovered_pages:
        pages = st.session_state.discovered_pages
        st.success(f"✅ {len(pages)}개 페이지 발견 — 멤버로 등록할 페이지를 선택하세요.")

        # 선택 체크박스
        selected_ids = []
        for p in pages:
            col_chk, col_info = st.columns([1, 9])
            checked = col_chk.checkbox("", key=f"chk_{p['id']}", value=True)
            col_info.markdown(
                f'<div class="notion-page-card">'
                f'<span style="font-size:1.2rem;">{p["icon"]}</span>'
                f'<div>'
                f'<div class="notion-page-title"><b>{p["title"]}</b></div>'
                f'<div class="notion-page-id">ID: {p["id_fmt"]}  |  수정: {p["last_edited"]}</div>'
                f'<div class="notion-page-url"><a href="{p["url"]}" target="_blank">🔗 Notion에서 열기</a></div>'
                f'</div></div>',
                unsafe_allow_html=True
            )
            if checked:
                selected_ids.append(p["id"])

        st.divider()
        st.markdown("##### ✏️ 선택한 페이지를 멤버로 등록")
        st.caption("페이지 제목이 멤버 이름으로 자동 설정됩니다. 직급·주업무는 나중에 수정 가능.")

        # 선택된 페이지를 미리보기 + 직급 입력
        sel_pages = [p for p in pages if p["id"] in selected_ids]
        rank_choices = ["수석","선임","연구원","인턴"]
        new_member_configs = {}
        if sel_pages:
            cols = st.columns(min(len(sel_pages), 3))
            for idx, p in enumerate(sel_pages):
                with cols[idx % 3]:
                    st.markdown(f"**{p['icon']} {p['title']}**")
                    rank  = st.selectbox("직급", rank_choices, key=f"rank_{p['id']}")
                    role  = st.text_input("주업무 (선택)", key=f"role_{p['id']}",
                                          placeholder="예: AI 홍수예측 모델")
                    new_member_configs[p["id"]] = {"rank": rank, "role": role}

            if st.button("✅ 선택한 페이지를 멤버로 등록하고 시작", use_container_width=True):
                for p in sel_pages:
                    cfg = new_member_configs[p["id"]]
                    st.session_state.members.append({
                        "이름":           p["title"],
                        "직급":           cfg["rank"],
                        "주업무":         cfg["role"] or "(Notion에서 자동 추출 예정)",
                        "세부":           "",
                        "상태":           "미검토",
                        "notion_page_id": p["id"],
                        "notion_url":     p["url"],
                    })
                st.success(f"✅ {len(sel_pages)}명 등록 완료! Notion 내용을 자동으로 불러옵니다...")
                # 바로 Notion 내용 로드
                prog = st.progress(0, text="내용 불러오는 중...")
                for i, m in enumerate(st.session_state.members):
                    nc = extract_page(m["notion_page_id"])
                    st.session_state.notion_contents[m["이름"]] = nc
                    # Notion 내용에서 주업무 자동 추출 (첫 줄 활용)
                    if not m["주업무"] or m["주업무"] == "(Notion에서 자동 추출 예정)":
                        first_line = nc["text"].split("\n")[0].strip()[:60] if nc["text"] else ""
                        if first_line:
                            st.session_state.members[i]["주업무"] = first_line
                    st.session_state.members[i]["상태"] = "검토중"
                    prog.progress((i+1)/len(st.session_state.members), text=f"{m['이름']} 완료...")
                st.rerun()
        else:
            st.info("위에서 페이지를 1개 이상 선택해주세요.")
    st.stop()

# ══════════════════════════════════════════════════════════════
# ❸ 멤버 등록된 경우 → 메인 탭 UI
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 전체 현황",
    "👤 개인 AI 검토",
    "🤖 일괄 처리",
    "🔄 멤버 재탐색",
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
    loaded  = sum(1 for m in members if m["이름"] in st.session_state.notion_contents)

    c1,c2,c3,c4,c5 = st.columns(5)
    for col,(label,val,color) in zip([c1,c2,c3,c4,c5],[
        ("전체 멤버",  total,  "#00f5ff"),
        ("내용 로드",  loaded, "#00aaff"),
        ("검토완료",   done,   "#00ff88"),
        ("검토중",     ongoing,"#ffcc00"),
        ("미검토",     pending,"#cc66ff"),
    ]):
        col.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-number" style="color:{color};text-shadow:0 0 12px {color}66;">{val}</div>'
            f'<div class="stat-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="cp-divider">', unsafe_allow_html=True)
    st.markdown("### 📋 멤버별 주업무 현황표 (2026)")

    rows = ""
    for m in members:
        badge   = STATUS_BADGE.get(m["상태"],"badge-none")
        emoji   = STATUS_EMOJI.get(m["상태"],"")
        nc      = st.session_state.notion_contents.get(m["이름"],{})
        loaded_mark = "✦" if nc else '<span style="color:#334455;">—</span>'
        ai_mark     = '<span style="color:#00f5ff;">✦</span>' if m["이름"] in st.session_state.ai_outputs else '<span style="color:#334455;">—</span>'
        notion_link = f'<a href="{m.get("notion_url","")}" target="_blank" style="color:#00aaff;font-size:0.75rem;">🔗</a>' if m.get("notion_url") else "—"
        rows += (
            f'<tr><td><span class="member-name">{m["이름"]}</span></td>'
            f'<td style="color:#667788;font-size:0.8rem;">{m["직급"]}</td>'
            f'<td style="color:#8ab4cc;">{m["주업무"]}</td>'
            f'<td style="color:#667788;font-size:0.8rem;">{m["세부"] or "—"}</td>'
            f'<td style="text-align:center;">{notion_link}</td>'
            f'<td style="text-align:center;color:#00aaff;">{loaded_mark}</td>'
            f'<td><span class="{badge}">{emoji} {m["상태"]}</span></td>'
            f'<td style="text-align:center;">{ai_mark}</td></tr>'
        )
    st.markdown(
        '<table class="cp-table"><thead><tr>'
        '<th>이름</th><th>직급</th><th>주업무</th><th>세부</th>'
        '<th>Notion</th><th>로드</th><th>검토상태</th><th>AI</th>'
        f'</tr></thead><tbody>{rows}</tbody></table>', unsafe_allow_html=True)

    st.markdown('<hr class="cp-divider">', unsafe_allow_html=True)
    st.markdown("### 📝 전체 팀 AI 종합보고서")
    if st.button("🚀 종합보고서 생성", use_container_width=True):
        parts = []
        for m in members:
            nc = st.session_state.notion_contents.get(m["이름"], {})
            parts.append(
                f"▶ {m['이름']} ({m['직급']})\n"
                f"  주업무: {m['주업무']}\n"
                f"  Notion 내용:\n{nc.get('text','(미로드)')[:1500]}\n"
            )
        with st.spinner("AI 보고서 작성 중..."):
            report = call_ai(
                "당신은 K-water AI연구소 소장입니다. 팀원별 Notion 업무 내용을 분석해 "
                "2026년 전체 팀 업무현황 보고서를 작성하세요. "
                "형식: [개요] → [멤버별 핵심업무 요약] → [팀 연구 시너지 분석] → [소장 종합의견 및 지시사항]",
                "\n\n".join(parts)
            )
        st.session_state["team_report"] = report

    if "team_report" in st.session_state:
        st.markdown(f'<div class="ai-result">{st.session_state["team_report"]}</div>', unsafe_allow_html=True)
        if st.button("💾 Notion 저장", key="save_team"):
            if save_to_notion(f"[AI종합보고서] {datetime.now().strftime('%Y.%m.%d')}", st.session_state["team_report"]):
                st.success("✅ 저장 완료!")
            else:
                st.warning("저장 페이지 ID를 사이드바에서 확인해주세요.")

# ════════════════════════════════════════════════════════════
# TAB 2: 개인 AI 검토
# ════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 👤 개인 업무 AI 검토")
    members  = st.session_state.members
    names    = [m["이름"] for m in members]
    sel_name = st.selectbox("멤버 선택", names, key="tab2_sel")
    m_idx    = names.index(sel_name)
    member   = members[m_idx]
    nc       = st.session_state.notion_contents.get(sel_name, {})

    col_l, col_r = st.columns([3,1])
    with col_l:
        notion_url = member.get("notion_url","")
        title_link = f'<a href="{notion_url}" target="_blank" style="color:#00aaff;font-size:0.78rem;margin-left:8px;">🔗 Notion 열기</a>' if notion_url else ""
        st.markdown(
            f'<div class="member-card">'
            f'<div class="member-name">{member["이름"]}{title_link}</div>'
            f'<div class="member-role">{member["직급"]} · K-water AI연구소</div>'
            f'</div>', unsafe_allow_html=True)

        if nc.get("title"):
            st.caption(f"📄 Notion 페이지 제목: **{nc['title']}**")

        # 주업무 수정
        new_role   = st.text_input("📌 주업무", value=member["주업무"], key=f"role2_{m_idx}")
        new_detail = st.text_area("📝 세부내용", value=member.get("세부",""), height=70, key=f"det2_{m_idx}")
        col_s1, col_s2 = st.columns(2)
        new_status = col_s1.selectbox("검토 상태", STATUS_OPTIONS,
                        index=STATUS_OPTIONS.index(member["상태"]), key=f"st2_{m_idx}")
        if col_s2.button("💾 저장", key=f"sv2_{m_idx}", use_container_width=True):
            st.session_state.members[m_idx].update({"주업무":new_role,"세부":new_detail,"상태":new_status})
            st.success("저장 완료!")
            st.rerun()

    with col_r:
        badge = STATUS_BADGE.get(member["상태"],"badge-none")
        emoji = STATUS_EMOJI.get(member["상태"],"")
        st.markdown(
            f'<div style="text-align:center;margin-top:24px;">'
            f'<span class="{badge}" style="font-size:1rem;padding:8px 18px;">{emoji} {member["상태"]}</span>'
            f'</div>', unsafe_allow_html=True)
        if sel_name in st.session_state.ai_outputs:
            st.markdown('<div style="text-align:center;margin-top:10px;color:#00f5ff;font-family:Orbitron,monospace;font-size:0.72rem;">✦ AI 완료</div>', unsafe_allow_html=True)

    # Notion 원문
    if nc.get("text"):
        with st.expander("📄 Notion 원문 보기"):
            st.markdown(f'<div class="notion-raw">{nc["text"]}</div>', unsafe_allow_html=True)
            if nc.get("links"):
                html = "".join(f'<div>• <a href="{lk["url"]}" target="_blank">{lk["label"]}</a></div>' for lk in nc["links"])
                st.markdown(f'<div class="attach-box">{html}</div>', unsafe_allow_html=True)
    else:
        col_reload, _ = st.columns([1,2])
        if col_reload.button("📥 Notion 내용 다시 불러오기", key=f"reload_{m_idx}"):
            with st.spinner("불러오는 중..."):
                result = extract_page(member["notion_page_id"])
            st.session_state.notion_contents[sel_name] = result
            st.rerun()

    st.divider()
    st.markdown("#### 🤖 AI 검토 실행")
    style_sel = st.selectbox("검토 관점", [
        "소장 검토 보고서  (업무요약·강점·개선·코멘트)",
        "3줄 핵심요약",
        "연구 성과 중심 평가",
        "타 부서 협업 방안 제안",
        "2026년 추진과제 도출",
    ], key="tab2_style")
    custom_q = st.text_input("추가 검토 포인트", placeholder="예: 예산 대비 성과는?")
    STYLE_SYS = {
        "소장 검토 보고서  (업무요약·강점·개선·코멘트)": "[업무핵심요약] [강점분석] [개선제안] [소장코멘트] 형식으로 작성.",
        "3줄 핵심요약":             "3줄로 핵심만 요약.",
        "연구 성과 중심 평가":      "연구 성과, 기술 기여도 중심으로 평가하고 향후 방향 제시.",
        "타 부서 협업 방안 제안":   "다른 팀·부서와의 시너지 협업 방안 3가지 제안.",
        "2026년 추진과제 도출":     "2026년 중점 추진과제 3가지를 구체적으로 도출.",
    }

    if st.button(f"✨ {sel_name} AI 검토 실행", use_container_width=True):
        nc = st.session_state.notion_contents.get(sel_name, {})
        notion_text  = nc.get("text","(Notion 내용 없음)")[:3000]
        notion_links = "\n".join(f"- {lk['label']}: {lk['url']}" for lk in nc.get("links",[]))
        prompt = (
            f"이름: {member['이름']} ({member['직급']})\n"
            f"주업무: {member['주업무']}\n\n"
            f"=== Notion 업무 내용 ===\n{notion_text}\n\n"
            f"=== 첨부·링크 ===\n{notion_links or '없음'}\n\n"
            f"추가질문: {custom_q or '없음'}"
        )
        with st.spinner("AI 분석 중..."):
            result = call_ai(f"당신은 K-water AI연구소 소장입니다. {STYLE_SYS[style_sel]}", prompt)
        st.session_state.ai_outputs[sel_name] = result
        st.session_state.members[m_idx]["상태"] = "검토완료"

    if sel_name in st.session_state.ai_outputs:
        st.markdown(f'<div class="ai-result">{st.session_state.ai_outputs[sel_name]}</div>', unsafe_allow_html=True)
        if st.button("💾 Notion 저장", use_container_width=True, key="save_t2"):
            if save_to_notion(f"[AI검토] {sel_name} · {datetime.now().strftime('%Y.%m.%d')}",
                               st.session_state.ai_outputs[sel_name]):
                st.success("✅ 저장 완료!")
            else:
                st.warning("저장 페이지 ID를 사이드바에서 확인해주세요.")

# ════════════════════════════════════════════════════════════
# TAB 3: 일괄 처리
# ════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🤖 전체 멤버 일괄 처리")
    st.caption("Notion 재로드 → AI 요약 → 상태 자동 업데이트")

    col_a, col_b = st.columns(2)
    target = col_a.multiselect(
        "대상 멤버",
        [m["이름"] for m in st.session_state.members],
        default=[m["이름"] for m in st.session_state.members]
    )
    batch_style = col_b.selectbox("AI 요약 스타일", [
        "소장 검토 보고서", "3줄 핵심요약", "강점·보완점 분석", "2026년 추진과제 도출"
    ])
    reload_notion = st.checkbox("Notion 내용 재로드 포함", value=False)

    BATCH_SYS = {
        "소장 검토 보고서":     "[업무요약][강점][개선사항][종합의견] 형식으로 작성.",
        "3줄 핵심요약":         "3줄로 핵심만 요약.",
        "강점·보완점 분석":     "[강점 3가지] [보완점 2가지] [액션아이템] 형식으로 작성.",
        "2026년 추진과제 도출": "2026년 중점 추진과제 3가지를 구체적으로 도출.",
    }

    if st.button("🚀 일괄 실행", use_container_width=True):
        if not oai:
            st.warning("OpenAI API Key를 확인해주세요.")
        elif not target:
            st.warning("대상 멤버를 선택해주세요.")
        else:
            prog = st.progress(0, text="처리 중...")
            tgt  = [m for m in st.session_state.members if m["이름"] in target]
            total_steps = len(tgt) * (2 if reload_notion else 1)
            step = 0
            for m in tgt:
                if reload_notion:
                    prog.progress(step/total_steps, text=f"📥 {m['이름']} Notion 읽는 중...")
                    nc = extract_page(m["notion_page_id"])
                    st.session_state.notion_contents[m["이름"]] = nc
                    step += 1
                nc = st.session_state.notion_contents.get(m["이름"], {})
                prog.progress(step/total_steps, text=f"🤖 {m['이름']} AI 분석 중...")
                notion_text  = nc.get("text","")[:3000]
                notion_links = "\n".join(f"- {lk['label']}: {lk['url']}" for lk in nc.get("links",[]))
                result = call_ai(
                    f"당신은 K-water AI연구소 소장입니다. {BATCH_SYS[batch_style]}",
                    f"이름:{m['이름']} ({m['직급']})\n주업무:{m['주업무']}\n\n"
                    f"=== Notion 내용 ===\n{notion_text}\n=== 링크 ===\n{notion_links or '없음'}"
                )
                st.session_state.ai_outputs[m["이름"]] = result
                idx = [x["이름"] for x in st.session_state.members].index(m["이름"])
                st.session_state.members[idx]["상태"] = "검토완료"
                step += 1
            prog.progress(1.0, text="완료!")
            st.success(f"✅ {len(target)}명 처리 완료!")
            st.rerun()

    st.markdown('<hr class="cp-divider">', unsafe_allow_html=True)
    for name, output in st.session_state.ai_outputs.items():
        nc = st.session_state.notion_contents.get(name, {})
        with st.expander(f"✦  {name}  {'| '+nc['title'] if nc.get('title') else ''}"):
            st.markdown(f'<div class="ai-result">{output}</div>', unsafe_allow_html=True)
            if st.button(f"💾 Notion 저장", key=f"bs_{name}"):
                if save_to_notion(f"[AI검토] {name} · {datetime.now().strftime('%Y.%m.%d')}", output):
                    st.success("저장 완료!")

# ════════════════════════════════════════════════════════════
# TAB 4: 멤버 재탐색
# ════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🔄 Notion 페이지 재탐색 / 멤버 추가")
    st.caption("새 Integration 연결 페이지를 탐색하거나 멤버를 추가합니다.")

    col_sq, col_sbtn = st.columns([3,1])
    sq = col_sq.text_input("검색어", placeholder="이름 또는 키워드", key="rescan_q")
    if col_sbtn.button("🔍 탐색", use_container_width=True, key="rescan_btn"):
        with st.spinner("탐색 중..."):
            pages = discover_notion_pages(sq)
        st.session_state.discovered_pages = pages

    if st.session_state.discovered_pages:
        pages = st.session_state.discovered_pages
        existing_ids = {m["notion_page_id"] for m in st.session_state.members}
        new_pages    = [p for p in pages if p["id"] not in existing_ids]
        old_pages    = [p for p in pages if p["id"] in existing_ids]

        st.markdown(f"**전체 {len(pages)}개** — 신규 {len(new_pages)}개 / 기등록 {len(old_pages)}개")

        if new_pages:
            st.markdown("#### ➕ 새로 추가할 수 있는 페이지")
            for p in new_pages:
                col_c, col_i, col_a = st.columns([1,7,2])
                chk = col_c.checkbox("", key=f"rechk_{p['id']}")
                col_i.markdown(
                    f'**{p["icon"]} {p["title"]}**  '
                    f'<span style="color:#334455;font-size:0.75rem;">{p["last_edited"]}</span>  '
                    f'<a href="{p["url"]}" target="_blank" style="color:#00aaff;font-size:0.75rem;">🔗</a>',
                    unsafe_allow_html=True
                )
                if chk:
                    rank = col_a.selectbox("직급", ["수석","선임","연구원","인턴"], key=f"rerank_{p['id']}")
                    if st.button(f"➕ {p['title']} 추가", key=f"readd_{p['id']}"):
                        st.session_state.members.append({
                            "이름": p["title"], "직급": rank,
                            "주업무": "(Notion에서 추출 예정)", "세부": "",
                            "상태": "미검토",
                            "notion_page_id": p["id"], "notion_url": p["url"],
                        })
                        st.success(f"{p['title']} 추가됨!")
                        st.rerun()
        else:
            st.info("새로 추가할 페이지가 없습니다 (모두 기등록).")

        if old_pages:
            with st.expander(f"기등록 페이지 {len(old_pages)}개"):
                for p in old_pages:
                    st.markdown(f"✦ **{p['title']}** — {p['last_edited']}")

# ════════════════════════════════════════════════════════════
# TAB 5: 멤버 관리
# ════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### ⚙️ 멤버 정보 수정 / 삭제")

    for i, m in enumerate(st.session_state.members):
        with st.expander(f"{STATUS_EMOJI.get(m['상태'],'⚪')} {m['이름']} ({m['직급']})"):
            c1, c2 = st.columns(2)
            m["이름"]   = c1.text_input("이름",  value=m["이름"],  key=f"mn_{i}")
            m["직급"]   = c2.selectbox("직급", ["수석","선임","연구원","인턴"],
                            index=["수석","선임","연구원","인턴"].index(m["직급"]) if m["직급"] in ["수석","선임","연구원","인턴"] else 2,
                            key=f"mr_{i}")
            m["주업무"] = st.text_input("주업무", value=m["주업무"], key=f"mj_{i}")
            m["세부"]   = st.text_area("세부내용", value=m.get("세부",""), height=60, key=f"md_{i}")
            st.caption(f"Notion ID: `{m.get('notion_page_id','—')}`")

            col_sv, col_del = st.columns(2)
            if col_sv.button("💾 저장", key=f"msv_{i}", use_container_width=True):
                st.session_state.members[i] = m
                st.success("저장 완료!")
                st.rerun()
            if col_del.button("🗑️ 삭제", key=f"mdl_{i}", use_container_width=True):
                st.session_state.members.pop(i)
                st.session_state.ai_outputs.pop(m["이름"], None)
                st.session_state.notion_contents.pop(m["이름"], None)
                st.rerun()

    st.divider()
    col_reset, col_restart = st.columns(2)
    if col_reset.button("🔄 AI 결과만 초기화", use_container_width=True):
        st.session_state.ai_outputs     = {}
        st.session_state.notion_contents = {}
        for i in range(len(st.session_state.members)):
            st.session_state.members[i]["상태"] = "미검토"
        st.success("초기화 완료")
        st.rerun()
    if col_restart.button("⚠️ 멤버 전체 초기화 (처음부터)", use_container_width=True):
        st.session_state.members         = []
        st.session_state.ai_outputs      = {}
        st.session_state.notion_contents = {}
        st.session_state.discovered_pages = []
        st.success("전체 초기화. 페이지를 새로고침해주세요.")
        st.rerun()

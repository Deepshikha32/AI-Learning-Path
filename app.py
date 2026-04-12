# ================================================================
#  app.py — Dashboard
#  Run: streamlit run app.py
# ================================================================
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import json
from collections import defaultdict
from core.engine import (load_kb, generate_roadmap, upsert_user,
                          get_user, CLUSTERS, goal_domain_mismatch,
                          toggle_topic, get_all_users_summary)
from core.sidebar import render_sidebar

st.set_page_config(
    page_title="LearnPath AI — Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── INJECT CSS ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background: #f0f4ff !important;
}
.stApp { background: #f0f4ff !important; }

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%) !important;
    min-width: 240px !important;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebarContent"] { padding: 1rem 0.8rem !important; }

/* Main content */
.block-container { padding: 2rem 2.5rem 2rem 2.5rem !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }

/* Form inputs */
.stTextInput > div > div > input {
    background: #f8fafc !important; border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important; color: #1e293b !important; font-size: .88rem !important;
}
.stTextInput > div > div > input::placeholder {
    color: #94a3b8 !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6366f1 !important; box-shadow: 0 0 0 3px #6366f120 !important;
}
.stTextInput > div > div > input:disabled {
    background: #f1f5f9 !important; color: #1e293b !important; border-color: #cbd5e1 !important;
    cursor: default !important;
}
.stSelectbox > div > div {
    background: #f8fafc !important; border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important; color: #1e293b !important;
}
.stSelectbox > div > div > div {
    color: #1e293b !important;
}
.stNumberInput > div > div > input {
    background: #f8fafc !important; border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important; color: #1e293b !important;
}
.stNumberInput > div > div > input::placeholder {
    color: #94a3b8 !important;
}
div[data-baseweb="select"] > div {
    background: #f8fafc !important; border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important; color: #1e293b !important;
    position: relative !important;
}
div[data-baseweb="select"] > div::after {
    content: '▼' !important;
    position: absolute !important;
    right: 12px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    pointer-events: none !important;
    font-size: 0.65rem !important;
    color: #94a3b8 !important;
}
div[data-baseweb="select"] > div > div {
    color: #1e293b !important;
    padding-right: 28px !important;
}
div[data-baseweb="select"]::after {
    content: '▼' !important;
}
label { color: #475569 !important; font-size: .78rem !important; font-weight: 600 !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; font-weight: 700 !important;
    font-size: .95rem !important; padding: 0.6rem 1.5rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all .2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px #10b98144 !important;
}
.stDownloadButton > button {
    background: white !important; border: 1.5px solid #e2e8f0 !important;
    color: #6366f1 !important; font-weight: 600 !important;
    border-radius: 10px !important;
}
/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #e8edf5 !important; border-radius: 12px !important;
    padding: 4px !important; gap: 3px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border-radius: 8px !important;
    color: #64748b !important; font-weight: 500 !important;
    padding: 8px 18px !important; font-size: .84rem !important;
}
.stTabs [aria-selected="true"] {
    background: white !important; color: #6366f1 !important;
    font-weight: 700 !important; box-shadow: 0 1px 4px rgba(0,0,0,.1) !important;
}
.stCheckbox > label > div { border-color: #c4b5fd !important; }
.stSlider > div > div > div > div {
    background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
}

/* Cards */
.card {
    background: white; border: 1.5px solid #e2e8f0;
    border-radius: 18px; padding: 22px;
    box-shadow: 0 1px 4px rgba(0,0,0,.05); margin-bottom: 16px;
}
.card-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1rem; font-weight: 700; color: #0f172a; margin-bottom: 4px;
}
.card-sub { font-size: .76rem; color: #64748b; margin-bottom: 16px; }

/* Stats */
.stat-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 18px; }
.stat-card {
    background: white; border: 1.5px solid #e2e8f0; border-radius: 16px;
    padding: 18px; position: relative; overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.stat-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 3px; background: linear-gradient(90deg, #6366f1, #8b5cf6);
}
.stat-icon {
    width: 38px; height: 38px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; margin-bottom: 10px;
}
.stat-num {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.9rem; font-weight: 800; color: #0f172a; line-height: 1;
}
.stat-lbl { font-size: .71rem; color: #64748b; font-weight: 500; margin-top: 4px; }

/* Week label */
.wk { display: inline-flex; align-items: center; gap: 6px;
    background: linear-gradient(135deg,#ede9fe,#ddd6fe);
    border: 1px solid #c4b5fd; border-radius: 8px;
    padding: 5px 14px; margin: 10px 0 5px;
    font-family: 'Plus Jakarta Sans',sans-serif;
    font-size: .78rem; font-weight: 700; color: #5b21b6; }

/* Topic row */
.trow { display: flex; align-items: center; gap: 10px;
    background: #f8fafc; border: 1.5px solid #e2e8f0;
    border-radius: 10px; padding: 9px 13px; margin: 4px 0; }
.trow.done { background: #f0fdf4; border-color: #bbf7d0; }
.tstep { background: #ede9fe; color: #6d28d9; font-size: .65rem;
    font-weight: 800; width: 22px; height: 22px; border-radius: 5px;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.tname { flex: 1; font-size: .84rem; font-weight: 500; color: #1e293b; }
.tname.done { text-decoration: line-through; color: #94a3b8; }
.tcat { background: #e0e7ff; color: #4338ca; font-size: .64rem;
    font-weight: 600; padding: 2px 7px; border-radius: 4px; }
.tdur { font-size: .73rem; font-weight: 700; color: #8b5cf6; min-width: 30px; text-align: right; }
.lbeg { background: #dcfce7; color: #15803d; font-size: .6rem; font-weight: 700; padding: 2px 6px; border-radius: 3px; }
.lint { background: #dbeafe; color: #1d4ed8; font-size: .6rem; font-weight: 700; padding: 2px 6px; border-radius: 3px; }
.ladv { background: #fef3c7; color: #b45309; font-size: .6rem; font-weight: 700; padding: 2px 6px; border-radius: 3px; }

/* Cluster */
.cl-ban { border-radius: 14px; padding: 14px 20px; margin-bottom: 18px;
    display: flex; align-items: center; gap: 14px; border: 1.5px solid; }

/* Progress bar */
.pb { background: #f1f5f9; border-radius: 6px; height: 7px; overflow: hidden; }
.pbf { height: 100%; border-radius: 6px; }

/* Skill row */
.skrow { margin-bottom: 11px; }
.sktop { display: flex; justify-content: space-between; margin-bottom: 3px; }
.skname { font-size: .78rem; font-weight: 500; color: #374151;
    display: flex; align-items: center; gap: 6px; }
.skpct { font-size: .78rem; font-weight: 700; }

/* Divider */
.fdiv { height: 1px; background: linear-gradient(90deg,transparent,#e2e8f0,transparent); margin: 18px 0; }

/* Alert */
.awarn { background: #fef9c3; border: 1.5px solid #fde68a; border-radius: 10px;
    padding: 12px 16px; margin: 10px 0; font-size: .82rem; color: #713f12; }
.ainfo { background: #e0f2fe; border: 1.5px solid #bae6fd; border-radius: 10px;
    padding: 12px 16px; margin: 10px 0; font-size: .82rem; color: #0c4a6e; }
.asuc  { background: #dcfce7; border: 1.5px solid #bbf7d0; border-radius: 10px;
    padding: 12px 16px; margin: 10px 0; font-size: .82rem; color: #14532d; }

/* Resource */
.res { display: flex; align-items: center; gap: 12px;
    background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px;
    padding: 10px 14px; margin: 7px 0; }
.res-btn { background: linear-gradient(135deg,#6366f1,#8b5cf6); color: white;
    border: none; border-radius: 7px; padding: 5px 12px; font-size: .7rem;
    font-weight: 600; text-decoration: none; flex-shrink: 0; margin-left: auto; }

/* Sched */
.sched { display: grid; grid-template-columns: repeat(7,1fr); gap: 6px; margin-top: 10px; }
.sdlbl { font-size: .63rem; font-weight: 600; color: #94a3b8; text-align: center; margin-bottom: 3px; }
.sdslot { border-radius: 7px; padding: 7px 3px; font-size: .69rem; font-weight: 600; text-align: center; }
.sdslot.a { background: linear-gradient(135deg,#6366f1,#8b5cf6); color: white; }
.sdslot.r { background: #ede9fe; color: #6d28d9; }
.sdslot.x { background: #f1f5f9; color: #94a3b8; }

/* Roadmap preview */
.rpnode { display: flex; align-items: center; gap: 10px; margin: 4px 0; }
.rpdot { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center;
    justify-content: center; font-size: .7rem; font-weight: 700; color: white;
    flex-shrink: 0; box-shadow: 0 2px 6px rgba(0,0,0,.12); }
.rpline { width: 2px; height: 16px; background: #e2e8f0; margin-left: 13px; }
.rplbl { font-size: .79rem; font-weight: 500; color: #374151; flex: 1; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ────────────────────────────────────────────
for k, v in [("generated", False), ("result", None), ("name", ""),
             ("goal", ""), ("domain", "Education"), ("age", 22),
             ("skill", "Beginner"), ("hrs", 1.5), ("health", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── IMPORT AND RENDER SIDEBAR ───────────────────────────────
render_sidebar()

# ── TOPBAR ───────────────────────────────────────────────────
name_d   = st.session_state.name or "Learner"
initials = "".join(w[0].upper() for w in name_d.split()[:2]) or "L"
goal_d   = st.session_state.goal or "No goal set"

# Add sidebar toggle button in top-right corner with expand hint
top_left, top_mid, top_right = st.columns([2.5, 0.5, 1])
with top_left:
    st.markdown(f"""
    <div style="margin-bottom:4px">
      <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.7rem;font-weight:800;color:#0f172a">Welcome, {name_d}! 👋</div>
      <div style="color:#64748b;font-size:.86rem">Let's build your personalized learning path</div>
    </div>""", unsafe_allow_html=True)

with top_mid:
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:center;height:100%">
      <div style="font-size:1.2rem;color:#94a3b8;cursor:help;title='Click hamburger menu at top-left to expand sidebar'"></div>
    </div>""", unsafe_allow_html=True)

with top_right:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;background:white;border:1.5px solid #e2e8f0;border-radius:50px;padding:5px 14px 5px 5px;float:right">
      <div style="width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:.82rem">{initials}</div>
      <div>
        <div style="font-size:.82rem;font-weight:600;color:#1e293b">{name_d}</div>
        <div style="font-size:.68rem;color:#64748b">{goal_d[:25]}</div>
      </div>
    </div>""", unsafe_allow_html=True)

# Step bar
steps = ["1. Profile","2. Skill Assessment","3. Roadmap","4. Learning"]
step  = 4 if st.session_state.generated else 1
step_html = ""
for i, s in enumerate(steps, 1):
    n_cls = "#6366f1" if i <= step else "#f1f5f9"
    t_cls = "#6366f1" if i == step else ("#94a3b8" if i > step else "#374151")
    icon  = "✓" if i < step else str(i)
    step_html += f'<span style="display:inline-flex;align-items:center;gap:6px"><span style="width:24px;height:24px;border-radius:50%;background:{n_cls};color:{"white" if i<=step else "#94a3b8"};font-size:.7rem;font-weight:700;display:inline-flex;align-items:center;justify-content:center">{icon}</span><span style="font-size:.76rem;font-weight:{"600" if i==step else "400"};color:{t_cls}">{s}</span></span>'
    if i < 4: step_html += '<span style="color:#94a3b8;margin:0 8px;font-size:.7rem">──→</span>'

st.markdown(f'<div style="background:white;border:1.5px solid #e2e8f0;border-radius:50px;padding:6px 20px;display:inline-flex;align-items:center;margin-bottom:22px">{step_html}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  PROFILE FORM
# ════════════════════════════════════════════════════════════
kb = load_kb()

with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📋 Complete Your Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-sub">Fill in your details — all fields are used by the AI to generate your perfect roadmap</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([2, 0.8, 1.4, 1.6])
    with c1: name   = st.text_input("Full Name", placeholder="e.g. Arjun Sharma", value=st.session_state.name)
    with c2: age    = st.number_input("Age", 10, 90, int(st.session_state.age), 1)
    with c3:
        ag = "🧑 Young (15–30)" if age < 30 else ("👨 Adult (30–60)" if age < 60 else "👴 Senior (60+)")
        st.markdown(f"""
        <label style="display:block;margin-bottom:8px;color:#475569;font-size:.78rem;font-weight:600">Age Group</label>
        <div style="background:white;border:1.5px solid #e2e8f0;border-radius:10px;padding:10px 13px;color:#1e293b;font-size:.88rem;font-weight:500">{ag}</div>""", unsafe_allow_html=True)
    with c4:
        dom_list = [
            "Education", "Entrepreneurship", "Health", "Hobbies",
            "Gardening", "Programming", "Fitness", "Cooking",
            "Music", "Art", "Business", "Language Learning",
            "Personal Finance", "Mental Wellness", "Design", "Photography"
        ]
        domain   = st.selectbox("Domain", dom_list, index=dom_list.index(st.session_state.domain) if st.session_state.domain in dom_list else 0)

    c5, c6, c7, c8 = st.columns([2.5, 1.3, 1.3, 1.8])
    with c5: goal   = st.text_input("Learning Goal", placeholder="e.g. learn Python, lose weight, start a startup, learn guitar")
    with c6: skill  = st.selectbox("Current Skill Level", ["Beginner","Intermediate","Advanced"])
    with c7: hrs    = st.slider("Hours/Day", 0.5, 8.0, float(st.session_state.hrs), 0.5)
    with c8: health = st.text_input("Health Condition (optional)", placeholder="e.g. knee pain, diabetes")
    st.markdown('</div>', unsafe_allow_html=True)

# Goal-domain mismatch check
if goal.strip():
    mismatch, suggested = goal_domain_mismatch(goal, domain)
    if mismatch and suggested:
        st.markdown(f"""
        <div class="awarn">⚠️ <strong>Domain Mismatch!</strong> Your goal "<em>{goal}</em>" seems to match
        <strong>{suggested}</strong>, but you selected <strong>{domain}</strong>.
        Consider switching for better results.</div>""", unsafe_allow_html=True)
        ca, cb, _ = st.columns([1.2, 1.2, 4])
        with ca:
            if st.button(f"✅ Switch to {suggested}"):
                st.session_state.domain = suggested; st.rerun()
        with cb:
            st.button("Keep my selection")

# ── CENTERED GENERATE BUTTON ─────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
c_l, c_mid, c_r = st.columns([2, 2, 2])
with c_mid:
    gen = st.button("🚀 Generate My Learning Path →", use_container_width=True)

if gen:
    if not goal.strip():
        st.warning("⚠️ Please enter a learning goal.")
    else:
        with st.spinner("🔄 Building your personalised AI roadmap..."):
            result = generate_roadmap(name or "Learner", age, domain, goal, skill, hrs, health, kb)
        st.session_state.update({
            "generated": True, "result": result,
            "name": name or "Learner", "goal": goal, "domain": domain,
            "age": age, "skill": skill, "hrs": hrs, "health": health
        })
        upsert_user(name or "Learner", age, domain, goal, skill, hrs, health, result["roadmap"])
        st.rerun()

st.markdown('<div class="fdiv"></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  RESULTS
# ════════════════════════════════════════════════════════════
if not st.session_state.generated:
    # Landing overview
    total_kb  = sum(len(t) for d in kb.values() for t in d.values())
    all_users = get_all_users_summary()
    st.markdown(f"""
    <div class="stat-grid">
      <div class="stat-card"><div class="stat-icon" style="background:#ede9fe">📚</div>
        <div class="stat-num">{total_kb}</div><div class="stat-lbl">Topics in Knowledge Base</div></div>
      <div class="stat-card"><div class="stat-icon" style="background:#d1fae5">👥</div>
        <div class="stat-num">{len(all_users)}</div><div class="stat-lbl">Registered Learners</div></div>
      <div class="stat-card"><div class="stat-icon" style="background:#fef3c7">🌐</div>
        <div class="stat-num">4</div><div class="stat-lbl">Domains</div></div>
      <div class="stat-card"><div class="stat-icon" style="background:#fce7f3">🤖</div>
        <div class="stat-num">5</div><div class="stat-lbl">AI Modules</div></div>
    </div>""", unsafe_allow_html=True)

    icons = {"Education":"🎓","Entrepreneurship":"💼","Health":"💪","Hobbies":"🎨"}
    clrs  = {"Education":"#6366f1","Entrepreneurship":"#0ea5e9","Health":"#10b981","Hobbies":"#ec4899"}
    cols  = st.columns(4)
    for col, (d, levels) in zip(cols, kb.items()):
        tot = sum(len(t) for t in levels.values())
        b, m, a = len(levels.get("Beginner",[])), len(levels.get("Intermediate",[])), len(levels.get("Advanced",[]))
        col.markdown(f"""
        <div class="card" style="border-top:3px solid {clrs[d]};text-align:center;padding:18px">
          <div style="font-size:1.6rem;margin-bottom:6px">{icons[d]}</div>
          <div style="font-family:'Plus Jakarta Sans';font-weight:700;font-size:.9rem;color:#0f172a">{d}</div>
          <div style="font-family:'Plus Jakarta Sans';font-size:1.7rem;font-weight:800;color:{clrs[d]};margin:4px 0">{tot}</div>
          <div style="font-size:.68rem;color:#94a3b8;margin-bottom:8px">topics</div>
          <div style="display:flex;gap:5px;justify-content:center;flex-wrap:wrap">
            <span class="lbeg">B:{b}</span><span class="lint">I:{m}</span><span class="ladv">A:{a}</span>
          </div>
        </div>""", unsafe_allow_html=True)
    st.stop()

# ── SHOW ROADMAP ─────────────────────────────────────────────
res     = st.session_state.result
roadmap = res["roadmap"]
cinfo   = res["cinfo"]
user    = get_user(st.session_state.name, st.session_state.age)
done    = user.get("completed", [])
pct     = round(len([t for t in roadmap if t["topic"] in done]) / max(len(roadmap), 1) * 100)

# Cluster banner
st.markdown(f"""
<div class="cl-ban" style="background:{cinfo['bg']};border-color:{cinfo['color']}44">
  <div style="font-size:1.8rem">{cinfo['icon']}</div>
  <div>
    <div style="font-family:'Plus Jakarta Sans';font-size:.95rem;font-weight:700;color:{cinfo['color']}">
      Cluster: {cinfo['name']}</div>
    <div style="font-size:.78rem;color:#64748b">{cinfo['desc']}</div>
  </div>
  <div style="margin-left:auto;text-align:right">
    <div style="font-size:.68rem;color:#94a3b8;margin-bottom:2px">Progress</div>
    <div style="font-family:'Plus Jakarta Sans';font-size:1.5rem;font-weight:800;color:{cinfo['color']}">{pct}%</div>
    <div class="pb" style="width:110px"><div class="pbf" style="width:{pct}%;background:{cinfo['color']}"></div></div>
  </div>
</div>""", unsafe_allow_html=True)

# Stats
done_count = len([t for t in roadmap if t["topic"] in done])
st.markdown(f"""
<div class="stat-grid">
  <div class="stat-card"><div class="stat-icon" style="background:#ede9fe">📋</div>
    <div class="stat-num">{res['total_t']}</div><div class="stat-lbl">Total Topics</div></div>
  <div class="stat-card"><div class="stat-icon" style="background:#d1fae5">📅</div>
    <div class="stat-num">{res['total_w']}</div><div class="stat-lbl">Weeks</div></div>
  <div class="stat-card"><div class="stat-icon" style="background:#fef3c7">⏱</div>
    <div class="stat-num">{res['total_h']}h</div><div class="stat-lbl">Total Hours</div></div>
  <div class="stat-card"><div class="stat-icon" style="background:#fce7f3">✅</div>
    <div class="stat-num">{done_count}</div><div class="stat-lbl">Completed</div></div>
</div>""", unsafe_allow_html=True)

# Two columns
left, right = st.columns([1.55, 1])
lbadge = {"Beginner":'<span class="lbeg">BEG</span>',
           "Intermediate":'<span class="lint">INT</span>',
           "Advanced":'<span class="ladv">ADV</span>'}

with left:
    tab1, tab2, tab3 = st.tabs(["📋 Step-by-Step Plan", "🌐 Node Graph", "🔗 Learning Resources"])

    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">Week-by-Week Plan — {len(roadmap)} Topics</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-sub">✅ Tick topics as you complete them — saved automatically</div>', unsafe_allow_html=True)
        cw = 0
        for step_item in roadmap:
            if step_item["week"] != cw:
                cw = step_item["week"]
                wh = sum(t["duration"] for t in roadmap if t["week"] == cw)
                st.markdown(f'<div class="wk">📅 Week {cw} · {wh:.1f}h</div>', unsafe_allow_html=True)
            is_done = step_item["topic"] in done
            col1, col2 = st.columns([0.045, 0.955])
            with col1:
                chk = st.checkbox("", value=is_done,
                                  key=f"d_chk_{step_item['step']}",
                                  label_visibility="collapsed")
                if chk != is_done:
                    toggle_topic(st.session_state.name, st.session_state.age, step_item["topic"])
                    st.rerun()
            with col2:
                dn = "done" if is_done else ""
                st.markdown(f"""
                <div class="trow {dn}">
                  <div class="tstep">#{step_item['step']:02d}</div>
                  {lbadge.get(step_item.get('level','Beginner'),'')}
                  <div class="tname {dn}">{step_item['topic']}</div>
                  <div class="tcat">{step_item.get('category','')}</div>
                  <div class="tdur">{step_item['duration']}h</div>
                </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        d1, d2 = st.columns(2)
        df = pd.DataFrame([{"Step":s["step"],"Week":s["week"],"Topic":s["topic"],
                              "Level":s.get("level",""),"Category":s.get("category",""),
                              "Hours":s["duration"],"Done":s["topic"] in done} for s in roadmap])
        with d1:
            st.download_button("📥 CSV", df.to_csv(index=False).encode(),
                               f"{st.session_state.name}_roadmap.csv", "text/csv",
                               use_container_width=True)
        with d2:
            st.download_button("📥 JSON",
                               json.dumps([{"step":s["step"],"week":s["week"],"topic":s["topic"],
                                            "hours":s["duration"],"done":s["topic"] in done}
                                           for s in roadmap], indent=2).encode(),
                               f"{st.session_state.name}_roadmap.json","application/json",
                               use_container_width=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🌐 Node Graph — Knowledge Tree</div>', unsafe_allow_html=True)
        st.caption("Root → Weeks → Topics. Green = completed, default = pending.")

        from collections import defaultdict as ddict
        weeks_map = ddict(list)
        for t in roadmap: weeks_map[t["week"]].append(t)
        swks = sorted(weeks_map.keys())

        NW,NH,HG,VG,MR = 170,40,28,65,4
        PX = 50
        mc = max(min(len(weeks_map[w]),MR) for w in swks)
        SW = max(PX*2 + mc*NW + (mc-1)*HG, 680)
        nodes = []
        prev  = [(SW//2, PX+18)]
        cy    = PX + 18 + 55
        lcols = {"Beginner":"#10b981","Intermediate":"#6366f1","Advanced":"#f59e0b"}

        nodes.append(f'<rect x="{SW//2-65}" y="{PX-18}" width="130" height="36" rx="18" fill="#6366f1" filter="url(#sh)"/>')
        nodes.append(f'<text x="{SW//2}" y="{PX+5}" text-anchor="middle" font-family="Inter" font-size="12.5" font-weight="700" fill="white">🧠 Learning Path</text>')

        for wk in swks:
            tops = weeks_map[wk]
            wx, wy = SW//2, cy
            nodes.append(f'<rect x="{wx-52}" y="{wy-13}" width="104" height="26" rx="13" fill="#ede9fe" stroke="#c4b5fd" stroke-width="1.5"/>')
            nodes.append(f'<text x="{wx}" y="{wy+4}" text-anchor="middle" font-family="Inter" font-size="11" font-weight="700" fill="#6d28d9">Week {wk}</text>')
            for px, py in prev:
                nodes.append(f'<line x1="{px}" y1="{py}" x2="{wx}" y2="{wy-13}" stroke="#c4b5fd" stroke-width="1.5" stroke-dasharray="4,3"/>')
            cy = wy + 26 + 26
            rows = [tops[i:i+MR] for i in range(0,len(tops),MR)]
            wb = []
            for row in rows:
                rn = len(row); rw = rn*NW+(rn-1)*HG
                sx = (SW-rw)//2; ry = cy
                for ci, t in enumerate(row):
                    nx_ = sx+ci*(NW+HG); ny_ = ry
                    cx_ = nx_+NW//2; cy2 = ny_+NH//2
                    id_ = t["topic"] in done
                    col = "#94a3b8" if id_ else lcols.get(t.get("level","Beginner"),"#6366f1")
                    fill= "#f0fdf4" if id_ else "white"
                    nodes.append(f'<line x1="{wx}" y1="{wy+13}" x2="{cx_}" y2="{ny_}" stroke="#ddd6fe" stroke-width="1.5"/>')
                    tick = "✓ " if id_ else ""
                    nm   = t["topic"][:20]+("…" if len(t["topic"])>20 else "")
                    nodes.append(f'<rect x="{nx_}" y="{ny_}" width="{NW}" height="{NH}" rx="8" fill="{fill}" stroke="{col}" stroke-width="1.8" filter="url(#sh)"/>')
                    nodes.append(f'<circle cx="{nx_+12}" cy="{ny_+NH//2}" r="4" fill="{col}"/>')
                    nodes.append(f'<text x="{nx_+22}" y="{ny_+14}" font-family="Inter" font-size="10" font-weight="600" fill="{"#94a3b8" if id_ else "#1e293b"}">{tick}{nm}</text>')
                    nodes.append(f'<text x="{nx_+22}" y="{ny_+27}" font-family="Inter" font-size="9" fill="#94a3b8">{t["duration"]}h · {t.get("category","")[:13]}</text>')
                    wb.append((cx_, ny_+NH))
                cy = ry+NH+18
            prev = wb[:MR]; cy += VG-18

        SH = cy+PX
        svg = f"""<svg width="100%" viewBox="0 0 {SW} {SH}" xmlns="http://www.w3.org/2000/svg">
          <defs><filter id="sh" x="-10%" y="-10%" width="130%" height="140%">
            <feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-opacity="0.07"/></filter></defs>
          <rect width="{SW}" height="{SH}" fill="#f8fafc" rx="12"/>
          {''.join(nodes)}</svg>"""
        st.markdown(f'<div style="overflow:auto;background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:14px;padding:12px">{svg}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        from core.engine import get_resources
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🔗 AI Learning Resources</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-sub">Click Open to launch YouTube, Coursera, Khan Academy and more directly</div>', unsafe_allow_html=True)
        for s in roadmap[:10]:
            with st.expander(f"{'✅' if s['topic'] in done else '📖'} {s['topic']} ({s['duration']}h)"):
                for r in get_resources(s["topic"], res["domain"], s.get("level","Beginner")):
                    st.markdown(f"""
                    <div class="res">
                      <span style="font-size:1.2rem">{r['icon']}</span>
                      <div>
                        <div style="font-size:.83rem;font-weight:600;color:#1e293b">{r['title']}</div>
                        <div style="font-size:.71rem;color:#64748b">{r['desc']} · {r['platform']}</div>
                      </div>
                      <a href="{r['url']}" target="_blank" class="res-btn">Open →</a>
                    </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with right:
    # Skill mastery
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Skill Mastery</div>', unsafe_allow_html=True)
    cat_h = defaultdict(float); cat_done = defaultdict(float)
    for t in roadmap:
        c = t.get("category","General")
        cat_h[c] += t["duration"]
        if t["topic"] in done: cat_done[c] += t["duration"]
    colors = ["#6366f1","#10b981","#f59e0b","#ec4899","#0ea5e9","#8b5cf6","#14b8a6","#f97316"]
    for i,(cat,h) in enumerate(sorted(cat_h.items(),key=lambda x:-x[1])[:7]):
        dp = round(cat_done[cat]/h*100) if h>0 else 0
        c  = colors[i%len(colors)]
        st.markdown(f"""
        <div class="skrow">
          <div class="sktop">
            <span class="skname">
              <span style="width:8px;height:8px;border-radius:50%;background:{c};display:inline-block"></span>
              {cat[:18]}
            </span>
            <span class="skpct" style="color:{c}">{dp}%</span>
          </div>
          <div class="pb"><div class="pbf" style="width:{dp}%;background:{c}"></div></div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Weekly schedule
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📆 Weekly Schedule</div>', unsafe_allow_html=True)
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    sh = '<div class="sched">'
    for i, d in enumerate(days):
        if i < 5:   sh += f'<div><div class="sdlbl">{d}</div><div class="sdslot a">{hrs}h</div></div>'
        elif i==5:  sh += f'<div><div class="sdlbl">{d}</div><div class="sdslot r">Review</div></div>'
        else:       sh += f'<div><div class="sdlbl">{d}</div><div class="sdslot x">Rest</div></div>'
    sh += '</div>'
    st.markdown(sh, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Roadmap preview
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">🗺️ Your Roadmap</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card-sub">Goal: {st.session_state.goal}</div>', unsafe_allow_html=True)
    nc = ["#6366f1","#8b5cf6","#a78bfa","#c4b5fd","#ddd6fe","#ede9fe"]
    for i, s in enumerate(roadmap[:6]):
        dn   = s["topic"] in done
        col  = "#10b981" if dn else nc[min(i,len(nc)-1)]
        lbl  = ("✓ " if dn else "") + s["topic"][:24]
        bdg  = "Done" if dn else ("In Progress" if i==done_count else "Upcoming")
        bc   = "#10b981" if dn else ("#6366f1" if i==done_count else "#94a3b8")
        st.markdown(f"""
        <div class="rpnode">
          <div class="rpdot" style="background:{col}">{'✓' if dn else i+1}</div>
          <div class="rplbl">{lbl}{'…' if len(s['topic'])>24 else ''}</div>
          <span style="font-size:.65rem;font-weight:600;color:{bc};background:{bc}15;padding:2px 7px;border-radius:4px">{bdg}</span>
        </div>
        {'<div class="rpline"></div>' if i < 5 else ''}""", unsafe_allow_html=True)
    if len(roadmap) > 6:
        st.caption(f"+ {len(roadmap)-6} more topics → visit Skill Roadmap page")
    st.markdown('</div>', unsafe_allow_html=True)

    # AI Recommendations
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">💡 AI Recommendations</div>', unsafe_allow_html=True)
    next_t = roadmap[done_count]["topic"][:28] if done_count < len(roadmap) else "All done!"
    recs = [
        f"📅 Study {hrs}h/day → finish in {res['total_w']} weeks",
        f"🎯 Next up: {next_t}",
        f"📈 {pct}% complete — keep going!",
        f"💪 {res['total_t'] - done_count} topics remaining",
    ]
    for r in recs:
        st.markdown(f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:8px 12px;margin:5px 0;font-size:.81rem;color:#374151">{r}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Related
    if res.get("related"):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🔗 You Might Also Enjoy</div>', unsafe_allow_html=True)
        for r in res["related"]:
            st.markdown(f"""
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:9px 12px;margin:6px 0">
              <div style="font-size:.65rem;color:#6366f1;font-weight:700;text-transform:uppercase">{r['domain']} · {r['level']}</div>
              <div style="font-size:.84rem;font-weight:600;color:#1e293b;margin:2px 0">{r['topic']}</div>
              <div style="font-size:.71rem;color:#64748b">📁 {r['category']} · ⏱ {r['duration']}h</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)



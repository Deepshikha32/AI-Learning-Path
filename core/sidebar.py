import streamlit as st

def render_sidebar():
    # Hide Streamlit's default page navigation
    st.markdown("""
    <style>
    [data-testid="stSidebarContent"] > ul { display: none !important; }
    [data-testid="stSidebarContent"] > div > ul { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    if "sidebar_collapsed" not in st.session_state:
        st.session_state.sidebar_collapsed = False

    with st.sidebar:
        # ── App Logo ─────────────────────────────────────────────
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;padding:6px 0;margin-bottom:14px">
          <div style="width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,#6366f1,#8b5cf6);
                      display:flex;align-items:center;justify-content:center;font-size:1.2rem">🧠</div>
          <div>
            <div style="font-size:1.05rem;font-weight:700;color:white">AI Learning Path</div>
            <div style="font-size:.65rem;color:#64748b">Adaptive Learning System</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── AI Coach — pinned at the TOP for instant visibility ──
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0d9488 0%,#059669 100%);
                    border-radius:14px;padding:13px 15px;margin-bottom:6px;
                    box-shadow:0 4px 18px rgba(13,148,136,0.50)">
          <div style="font-size:.6rem;font-weight:800;color:rgba(255,255,255,0.75);
                      text-transform:uppercase;letter-spacing:.12em;margin-bottom:2px">
            🤖 AI ASSISTANCE
          </div>
          <div style="font-size:.92rem;font-weight:700;color:white;margin-bottom:1px">
            Chat with AI Coach
          </div>
          <div style="font-size:.69rem;color:rgba(255,255,255,0.82)">
            Tips · Playlists · Schedules · Motivation
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💬  Open AI Coach →", use_container_width=True, key="nav_aicoach"):
            st.switch_page("pages/9_AICoach.py")

        # ── Divider ──────────────────────────────────────────────
        st.markdown("""
        <div style="font-size:.62rem;font-weight:700;color:#475569;text-transform:uppercase;
                    letter-spacing:.1em;margin:16px 0 8px;border-top:1px solid #334155;
                    padding-top:12px">MAIN MENU</div>
        """, unsafe_allow_html=True)

        # ── Navigation Pages ─────────────────────────────────────
        if st.button("📊  Dashboard", use_container_width=True, key="nav_dashboard"):
            st.switch_page("app.py")

        if st.button("🗺️  Skill Roadmap", use_container_width=True, key="nav_roadmap"):
            st.switch_page("pages/2_Roadmap.py")

        if st.button("📚  My Courses", use_container_width=True, key="nav_courses"):
            st.switch_page("pages/3_Courses.py")

        if st.button("📈  My Progress", use_container_width=True, key="nav_progress"):
            st.switch_page("pages/4_Progress.py")

        if st.button("📋  Assessments", use_container_width=True, key="nav_assessments"):
            st.switch_page("pages/5_Assessments.py")

        if st.button("🏅  Certificates", use_container_width=True, key="nav_certificates"):
            st.switch_page("pages/6_Certificates.py")

        if st.button("📉  Analytics", use_container_width=True, key="nav_analytics"):
            st.switch_page("pages/7_Analytics.py")

        if st.button("⚙️  Settings", use_container_width=True, key="nav_settings"):
            st.switch_page("pages/8_Settings.py")
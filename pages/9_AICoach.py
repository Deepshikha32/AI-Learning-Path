# ================================================================
#  pages/9_AICoach.py — AI Coach Guide & Chat
#  Personalized guidance and interactive chat with AI Coach
# ================================================================

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from core.engine import get_user, load_kb
from core.sidebar import render_sidebar
from datetime import datetime
import google.generativeai as genai  # kept for compatibility
from google import genai as genai_new
from google.genai import types as genai_types
import random

st.set_page_config(
    page_title="LearnPath AI — Your Buddy",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── INJECT CSS ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800;900&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background: #0d1117 !important;
}
.stApp { background: #0d1117 !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2.5rem !important; max-width: 100% !important; }

/* ── Style top-level columns as cards ── */
[data-testid="stColumn"] > div:first-child,
[data-testid="column"] > div:first-child {
    background: #161b2d;
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}
/* Reset nested columns */
[data-testid="stColumn"] [data-testid="stColumn"] > div:first-child,
[data-testid="column"] [data-testid="column"] > div:first-child {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
    border-radius: 0 !important;
}

/* Columns grow to content height only */
[data-testid="stHorizontalBlock"] { align-items: flex-start !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #1a1a2e 60%, #16213e 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.2) !important;
}
[data-testid="stSidebar"] * { color: #c7d2fe !important; }
[data-testid="stSidebarContent"] { padding: 1rem 0.8rem !important; }

/* ── Base text ── */
p, li, span, label { color: #c7d2fe !important; }
h1, h2, h3, h4, h5 { color: #e0e7ff !important; }
strong, b { color: #a5b4fc !important; }
a { color: #818cf8 !important; }
a:hover { color: #6366f1 !important; }
a[style*="background"] { color: white !important; }
a[style*="background"]:hover { color: white !important; opacity: 0.92; }

/* ── Cards ── */
.card {
    background: #161b2d;
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 18px; padding: 22px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    margin-bottom: 16px;
}
.card-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1rem; font-weight: 800; color: #e0e7ff !important;
    margin-bottom: 3px;
}
.card-sub { font-size: .76rem; color: #818cf8 !important; margin-bottom: 12px; opacity: 0.85; }

/* ── Chat window ── */
.chat-wrap {
    background: #0f1629;
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 16px; padding: 14px;
    max-height: 360px; min-height: 80px; overflow-y: auto;
    margin-bottom: 12px; scroll-behavior: smooth;
}
.chat-wrap::-webkit-scrollbar { width: 4px; }
.chat-wrap::-webkit-scrollbar-track { background: #1a1f35; }
.chat-wrap::-webkit-scrollbar-thumb { background: #4f46e5; border-radius: 4px; }

/* ── Bubbles ── */
.chat-bubble-wrap-user {
    display: flex; justify-content: flex-end;
    align-items: flex-end; gap: 8px; margin: 10px 0;
}
.chat-bubble-wrap-ai {
    display: flex; justify-content: flex-start;
    align-items: flex-end; gap: 8px; margin: 10px 0;
}
.avatar {
    width: 34px; height: 34px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
}
.avatar-ai   { background: linear-gradient(135deg, #4f46e5, #6366f1); box-shadow: 0 4px 12px rgba(99,102,241,0.5); }
.avatar-user { background: linear-gradient(135deg, #6366f1, #818cf8); box-shadow: 0 4px 12px rgba(99,102,241,0.4); }
.bubble-user {
    background: linear-gradient(135deg, #4f46e5, #6366f1);
    color: white; padding: 12px 18px;
    border-radius: 20px 20px 4px 20px;
    max-width: 70%; font-size: .87rem; line-height: 1.65;
    box-shadow: 0 6px 18px rgba(99,102,241,0.35);
}
.bubble-ai {
    background: #1e2540;
    border: 1px solid rgba(99,102,241,0.2);
    color: #e0e7ff; padding: 12px 18px;
    border-radius: 20px 20px 20px 4px;
    max-width: 82%; font-size: .87rem; line-height: 1.7;
    box-shadow: 0 3px 14px rgba(0,0,0,0.3);
}
.bubble-ai pre {
    background: #0f1629 !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 10px !important; padding: 12px 16px !important;
    overflow-x: auto !important; margin: 10px 0 !important;
}
.bubble-ai code {
    background: #1e2540 !important; color: #a5b4fc !important;
    border-radius: 5px !important; padding: 2px 6px !important;
    font-size: .83rem !important;
}
.bubble-ai pre code { background: transparent !important; padding: 0 !important; color: #c7d2fe !important; }

/* ── Text Input ── */
.stTextInput > div > div > input {
    background: #1e2540 !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 14px !important;
    color: #e0e7ff !important;
    font-size: .9rem !important;
    padding: 14px 18px !important;
    caret-color: #6366f1 !important;
    transition: all 0.2s !important;
}
.stTextInput > div > div > input::placeholder { color: #4f5b8a !important; opacity: 1; }
.stTextInput > div > div > input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.2) !important;
    outline: none !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; font-weight: 700 !important;
    font-size: .9rem !important; height: 44px !important;
    white-space: nowrap !important; overflow: hidden !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 26px rgba(99,102,241,0.5) !important;
    background: linear-gradient(135deg, #6366f1, #818cf8) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Clear button ── */
.clear-btn > div > button, .clear-btn button {
    background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
    box-shadow: 0 4px 12px rgba(220,38,38,0.25) !important;
}
.clear-btn button:hover { box-shadow: 0 8px 20px rgba(220,38,38,0.4) !important; }

/* ── Onboarding box ── */
.onboard-box {
    background: linear-gradient(135deg, #1e2540, #232b4a);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 16px; padding: 20px; margin-bottom: 20px;
}
.onboard-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.1rem; font-weight: 800; color: #e0e7ff !important; margin-bottom: 5px;
}
.onboard-desc { font-size: .84rem; color: #a5b4fc !important; }

/* ── Rec-box ── */
.rec-box {
    background: #1e2540; border-left: 4px solid #6366f1;
    border-radius: 10px; padding: 14px; margin: 8px 0;
    font-size: .83rem; color: #c7d2fe;
    box-shadow: 0 1px 6px rgba(0,0,0,0.3);

}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: white !important;
    border: 1.5px solid #ddd6fe !important;
    border-radius: 12px !important;
}
.streamlit-expanderHeader { color: #6d28d9 !important; }

/* ── Playlist link cards ── */
a div { transition: all 0.2s ease !important; border-color: #ddd6fe !important; }
a div:hover { box-shadow: 0 6px 18px rgba(109,40,217,0.15) !important; transform: translateX(3px); }
</style>
""", unsafe_allow_html=True)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "first_visit" not in st.session_state:
    st.session_state.first_visit = True
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "pending_msg" not in st.session_state:
    st.session_state.pending_msg = ""

# ── RENDER SIDEBAR ───────────────────────────────────────────
render_sidebar()

# Fetch API key silently
gemini_api_key = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not gemini_api_key:
    import os
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

# ── AI COACH RESPONSE GENERATOR ──────────────────────────────
def generate_coach_response(user_message, name, goal, skill_level, user_data, api_key):
    """
    Send every user message directly to Gemini AI — no keyword filtering.
    Gemini answers all questions: learning suggestions, coding, health, general knowledge, etc.
    Falls back gracefully if no API key or all models fail.
    """
    import re

    def fix_youtube_urls(text):
        """Normalize ALL youtube URLs to proper https://www.youtube.com/results format."""
        # Pre-clean: remove any double-protocol artifacts from old code
        text = re.sub(r'https?://www\.https?://', 'https://', text)
        text = re.sub(r'https?://https?://', 'https://', text)

        def normalize(m):
            full = m.group(0)
            q = re.search(r'search_query=([^\s)"\'<>]+)', full)
            if q:
                return f"https://www.youtube.com/results?search_query={q.group(1)}"
            return f"https://www.youtube.com/results?search_query={user_message.replace(' ', '+')}"

        return re.sub(
            r'(?:https?://)?(?:www\.)?youtube\.com/[^\s)"\'<>]+',
            normalize,
            text
        )

    if api_key:
        try:
            # Models that work on this account
            _MODELS = [
                "gemini-2.5-flash-lite",  # ✅ working, fast, free
                "gemini-2.5-flash",       # retry on 503
                "gemini-flash-lite-latest",
            ]
            client = genai_new.Client(api_key=api_key)

            system_instruction = f"""You are {name}'s AI Buddy — a friendly, knowledgeable AI companion built into LearnPath AI. Answer ANY question helpfully and concisely. Use emojis & bullet points.

User profile: skill={skill_level}, goal="{goal}".

You are part of the LearnPath AI app which has these pages — guide users to the right one when relevant:
• 🏠 Dashboard (Home): Set up your profile, generate your personalized AI learning roadmap
• 🗺️ Roadmap: View your full week-by-week learning plan with all topics and progress
• 📚 Courses: Browse available courses and learning materials for your domain
• 📈 Progress: Track completed topics, hours studied, and your overall learning progress
• 📝 Assessments: Take skill assessments to evaluate your knowledge level
• 🎓 Certificates: View and download your earned completion certificates
• 📊 Analytics: See detailed analytics — study streaks, time spent, performance charts
• ⚙️ Settings: Update your profile, goals, preferences, and notification settings
•  Buddy (this page): Chat with AI for any question, learning suggestions, playlists, advice

When suggesting YouTube resources, ALWAYS use full URLs: https://www.youtube.com/results?search_query=YOUR+TOPIC
NEVER write youtube.com/... without https://www. — always the full URL.
Keep responses concise. For learning suggestions give 5 specific actionable ideas."""

            # Only last 3 messages for speed
            recent = st.session_state.chat_history[-4:-1] if len(st.session_state.chat_history) > 1 else []
            history_parts = ""
            for msg in recent:
                role = "Buddy" if msg["role"] == "ai" else "User"
                history_parts += f"{role}: {msg['content'][:100]}\n"

            import time as _time
            for model_name in _MODELS:
                for attempt in range(2):  # up to 2 attempts per model
                    try:
                        user_prompt = f"User: {user_message}\nBuddy:"
                        if history_parts:
                            user_prompt = f"Recent chat:\n{history_parts}\n{user_prompt}"

                        contents = [genai_types.Content(
                            role="user",
                            parts=[genai_types.Part(text=user_prompt)]
                        )]
                        cfg = genai_types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.5,
                            max_output_tokens=300
                        )
                        resp = client.models.generate_content(
                            model=model_name, contents=contents, config=cfg
                        )
                        if resp and resp.text and resp.text.strip():
                            return fix_youtube_urls(resp.text.strip())
                        break
                    except Exception as e:
                        err = str(e)
                        if "503" in err or "UNAVAILABLE" in err:
                            _time.sleep(2)  # wait and retry same model
                            continue
                        break  # quota/other error → try next model

        except Exception:
            pass  # Fall through to offline fallback

    # ── OFFLINE FALLBACK (no API key or all Gemini models failed) ──────────
    msg_clean = user_message.lower().replace("?", "").replace("!", "")
    stopwords = {"how", "what", "when", "where", "why", "can", "the", "is",
                 "do", "to", "a", "an", "and", "am", "i", "me", "my", "for"}
    topic_words = [w for w in msg_clean.split() if len(w) > 3 and w not in stopwords]
    topic = "+".join(topic_words[:3]) if topic_words else goal.replace(" ", "+")

    if api_key:
        # Key exists but quota exhausted
        response  = f"⚠️ **Hey {name}!** The Gemini API quota for today is used up.\n\n"
        response += f"📌 **Your question:** _{user_message}_\n\n"
        response += f"🔑 **Quick fix:** Get a fresh free API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) and paste it in `.streamlit/secrets.toml`\n\n"
        response += f"🎯 **Meanwhile, here are YouTube resources:**\n"
    else:
        response  = f"🔑 **Hey {name}!** No Gemini API key found.\n\n"
        response += f"📌 **Your question:** _{user_message}_\n\n"
        response += f"➡️ Get a **free** API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)\n\n"
        response += f"🎯 **Meanwhile, here are YouTube resources:**\n"

    response += f"▶️ [Full Tutorial](https://www.youtube.com/results?search_query={topic}+tutorial+full+course)\n"
    response += f"🎓 [Beginner Guide](https://www.youtube.com/results?search_query={topic}+for+beginners)\n"
    response += f"📚 [Complete Course](https://www.youtube.com/results?search_query={topic}+complete+course)\n"
    return response

def generate_tips(skill_level, age, completed, total_topics, domain_topics):
    """Generate quick tips for the tip panel."""
    tips = []
    
    if completed == 0:
        tips.append("🌟 Start your first topic today! The first step is the most important.")
    elif completed < 5:
        tips.append(f"🚀 You're off to a great start! {completed} topics down, keep the momentum!")
    else:
        tips.append(f"💎 Impressive! You've mastered {completed} topics. That's real dedication!")
    
    if skill_level == "Beginner":
        tips.append("📚 Master the basics first - they're the foundation for everything.")
    elif skill_level == "Intermediate":
        tips.append("🎯 Time to build projects! Apply what you've learned to real scenarios.")
    else:
        tips.append("🏆 You're at an advanced level - now it's time to innovate and lead!")
    
    pct = round((completed / max(total_topics, 1)) * 100)
    if pct < 25:
        tips.append(f"⏳ {pct}% complete - you've got plenty of exciting learning ahead!")
    elif pct < 50:
        tips.append(f"🔥 Halfway there! {pct}% complete - the momentum is building!")
    elif pct < 100:
        tips.append(f"🎉 Almost there! {pct}% complete - the finish line is in sight!")
    else:
        tips.append("🏅 Congratulations! You've completed your learning journey!")
    
    if age < 25:
        tips.append("⚡ Youth is on your side - embrace curiosity and experiment boldly!")
    elif age < 40:
        tips.append("⚖️ Balance learning with real-world application for maximum impact.")
    else:
        tips.append("🎓 Your experience is your superpower - connect new learning to past knowledge.")
    
    return tips[:3]


# ── GET USER INFO ───────────────────────────────────────────
user_name = st.session_state.get("name", "Learner")
user_age  = st.session_state.get("age", 22)
user_goal = st.session_state.get("goal", "No goal set")
user_skill = st.session_state.get("skill", "Beginner")
user_data  = get_user(user_name, user_age)

# ── ENTER-TO-SEND CALLBACK ──────────────────────────────────
def on_enter():
    val = st.session_state.get(f"chat_input_{st.session_state.input_key}", "").strip()
    if val:
        st.session_state.pending_msg = val
        st.session_state.input_key += 1

# ── GOAL CHECK ───────────────────────────────────────────────
goal_is_set = user_goal and user_goal not in ("No goal set", "", "no goal set")

# ── HERO HEADER ──────────────────────────────────────────────
st.markdown(f"""
  <div style="margin-bottom:18px;display:flex;align-items:center;gap:14px">
    <div style="flex-shrink:0;filter:drop-shadow(0 0 10px rgba(239,68,68,0.6))">
      <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:54px;height:54px">
        <defs>
          <linearGradient id="hg" x1="14" y1="18" x2="50" y2="50" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#3b1515"/>
            <stop offset="100%" stop-color="#1e1010"/>
          </linearGradient>
          <radialGradient id="eg" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#fca5a5"/>
            <stop offset="100%" stop-color="#ef4444"/>
          </radialGradient>
        </defs>
        <!-- Antenna stem -->
        <rect x="30" y="7" width="4" height="11" rx="2" fill="#dc2626"/>
        <!-- Antenna ball -->
        <circle cx="32" cy="6" r="4" fill="#ef4444"/>
        <circle cx="32" cy="6" r="2" fill="#fca5a5"/>
        <!-- Head -->
        <rect x="12" y="18" width="40" height="30" rx="8" fill="url(#hg)" stroke="#ef4444" stroke-width="1.5"/>
        <!-- Left eye -->
        <circle cx="23" cy="33" r="6" fill="#0f0606" stroke="#dc2626" stroke-width="1.5"/>
        <circle cx="23" cy="33" r="3.2" fill="url(#eg)"/>
        <circle cx="21" cy="31" r="1" fill="white" opacity="0.6"/>
        <!-- Right eye -->
        <circle cx="41" cy="33" r="6" fill="#0f0606" stroke="#dc2626" stroke-width="1.5"/>
        <circle cx="41" cy="33" r="3.2" fill="url(#eg)"/>
        <circle cx="39" cy="31" r="1" fill="white" opacity="0.6"/>
        <!-- Mouth grille -->
        <rect x="22" y="42" width="20" height="3" rx="1.5" fill="#ef4444" opacity="0.8"/>
        <rect x="25" y="42" width="2" height="3" rx="1" fill="#fca5a5"/>
        <rect x="31" y="42" width="2" height="3" rx="1" fill="#fca5a5"/>
        <rect x="37" y="42" width="2" height="3" rx="1" fill="#fca5a5"/>
        <!-- Left ear -->
        <rect x="5" y="26" width="7" height="12" rx="3.5" fill="#1e1010" stroke="#ef4444" stroke-width="1.5"/>
        <rect x="7" y="29" width="3" height="6" rx="1.5" fill="#ef4444" opacity="0.5"/>
        <!-- Right ear -->
        <rect x="52" y="26" width="7" height="12" rx="3.5" fill="#1e1010" stroke="#ef4444" stroke-width="1.5"/>
        <rect x="54" y="29" width="3" height="6" rx="1.5" fill="#ef4444" opacity="0.5"/>
      </svg>
    </div>
    <div>
      <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.8rem;font-weight:900;
                  color:white;line-height:1.1">Your Buddy</div>
      <div style="color:#e0e7ff;font-size:.83rem;margin-top:3px">
        Your personal AI companion — ask me anything, anytime!</div>
    </div>
  </div>""", unsafe_allow_html=True)

# ── APP GUIDE (4+4 grid) ─────────────────────────────────────
st.markdown("""
<div style="margin-bottom:14px">
  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:.85rem;font-weight:700;
              color:#a5b4fc;margin-bottom:8px;letter-spacing:.2px">
    📱 Explore the App — Click any section to navigate
  </div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px">
    <a href="/" target="_self" style="text-decoration:none">
      <div style="background:#1e2540;border:1px solid rgba(99,102,241,0.25);border-radius:10px;padding:8px 12px;display:flex;align-items:center;gap:7px">
        <span style="font-size:1rem">🏠</span>
        <div><div style="font-size:.72rem;font-weight:700;color:#e0e7ff">Dashboard</div>
        <div style="font-size:.6rem;color:#818cf8">Profile &amp; roadmap</div></div>
      </div></a>
    <a href="/Roadmap" target="_self" style="text-decoration:none">
      <div style="background:#1e2540;border:1px solid rgba(99,102,241,0.25);border-radius:10px;padding:8px 12px;display:flex;align-items:center;gap:7px">
        <span style="font-size:1rem">🗺️</span>
        <div><div style="font-size:.72rem;font-weight:700;color:#e0e7ff">Roadmap</div>
        <div style="font-size:.6rem;color:#818cf8">Week-by-week plan</div></div>
      </div></a>
    <a href="/Courses" target="_self" style="text-decoration:none">
      <div style="background:#1e2540;border:1px solid rgba(99,102,241,0.25);border-radius:10px;padding:8px 12px;display:flex;align-items:center;gap:7px">
        <span style="font-size:1rem">📚</span>
        <div><div style="font-size:.72rem;font-weight:700;color:#e0e7ff">Courses</div>
        <div style="font-size:.6rem;color:#818cf8">Browse materials</div></div>
      </div></a>
    <a href="/Progress" target="_self" style="text-decoration:none">
      <div style="background:#1e2540;border:1px solid rgba(99,102,241,0.25);border-radius:10px;padding:8px 12px;display:flex;align-items:center;gap:7px">
        <span style="font-size:1rem">📈</span>
        <div><div style="font-size:.72rem;font-weight:700;color:#e0e7ff">Progress</div>
        <div style="font-size:.6rem;color:#818cf8">Track completion</div></div>
      </div></a>
    <a href="/Assessments" target="_self" style="text-decoration:none">
      <div style="background:#1e2540;border:1px solid rgba(99,102,241,0.25);border-radius:10px;padding:8px 12px;display:flex;align-items:center;gap:7px">
        <span style="font-size:1rem">📝</span>
        <div><div style="font-size:.72rem;font-weight:700;color:#e0e7ff">Assessments</div>
        <div style="font-size:.6rem;color:#818cf8">Test your knowledge</div></div>
      </div></a>
    <a href="/Certificates" target="_self" style="text-decoration:none">
      <div style="background:#1e2540;border:1px solid rgba(99,102,241,0.25);border-radius:10px;padding:8px 12px;display:flex;align-items:center;gap:7px">
        <span style="font-size:1rem">🎓</span>
        <div><div style="font-size:.72rem;font-weight:700;color:#e0e7ff">Certificates</div>
        <div style="font-size:.6rem;color:#818cf8">Download certificates</div></div>
      </div></a>
    <a href="/Analytics" target="_self" style="text-decoration:none">
      <div style="background:#1e2540;border:1px solid rgba(99,102,241,0.25);border-radius:10px;padding:8px 12px;display:flex;align-items:center;gap:7px">
        <span style="font-size:1rem">📊</span>
        <div><div style="font-size:.72rem;font-weight:700;color:#e0e7ff">Analytics</div>
        <div style="font-size:.6rem;color:#818cf8">Streaks &amp; charts</div></div>
      </div></a>
    <a href="/Settings" target="_self" style="text-decoration:none">
      <div style="background:#1e2540;border:1px solid rgba(99,102,241,0.25);border-radius:10px;padding:8px 12px;display:flex;align-items:center;gap:7px">
        <span style="font-size:1rem">⚙️</span>
        <div><div style="font-size:.72rem;font-weight:700;color:#e0e7ff">Settings</div>
        <div style="font-size:.6rem;color:#818cf8">Profile &amp; preferences</div></div>
      </div></a>
  </div>
</div>
""", unsafe_allow_html=True)


# ── AI COACH LAYOUT: Chat (left) + Playlist Suggestions (right) ──
col1, col2 = st.columns([2, 1])

with col1:
    # ── Compact goal reminder (aligned inside this card) ────────
    if not goal_is_set:
        st.markdown(f"""
        <div style="background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.35);
                    border-radius:12px;padding:11px 14px;margin-bottom:14px;
                    position:relative;overflow:hidden">
          <div style="position:absolute;top:0;left:0;right:0;height:2px;
                      background:linear-gradient(90deg,#4f46e5,#818cf8,#4f46e5);
                      background-size:200%;animation:shimmer 2s infinite"></div>
          <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
            <div style="font-size:1.3rem">🎯</div>
            <div style="flex:1;min-width:160px">
              <div style="font-size:.8rem;font-weight:700;color:#e0e7ff;margin-bottom:2px">
                Hi {user_name}! Set your goal for personalized Buddy responses
              </div>
              <div style="font-size:.68rem;color:#a5b4fc">
                Unlock tailored suggestions, playlists &amp; milestone tracking
              </div>
            </div>
            <a href="/" target="_self"
               style="display:inline-block;background:linear-gradient(135deg,#4f46e5,#6366f1);
                      color:white;padding:6px 14px;border-radius:8px;text-decoration:none;
                      font-weight:700;font-size:.72rem;white-space:nowrap;
                      box-shadow:0 3px 10px rgba(99,102,241,.4)">
              🎯 Set Goal →
            </a>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── First-time onboarding ────────────────────────────────────
    if st.session_state.first_visit and goal_is_set:
        st.markdown(f"""
        <div class="onboard-box">
          <div class="onboard-title">👋 Hey! I'm your Buddy!</div>
          <div class="onboard-desc">
            I'm here to help you achieve your goal of <strong>{user_goal}</strong>. Ask me anything! 🚀
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state.first_visit = False

    st.markdown('<div style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:.95rem;font-weight:800;color:#e0e7ff;margin-bottom:2px">💬 Chat with your Buddy</div><div style="font-size:.74rem;color:#818cf8;margin-bottom:12px">Ask me anything — I\'ll answer every question! Press Enter or click Send 🚀</div>', unsafe_allow_html=True)

    # Build entire chat HTML in one block to avoid orphaned div elements
    if not st.session_state.chat_history:
        chat_html = '<div class="chat-wrap" style="min-height:100px;text-align:center;padding:18px">'
        chat_html += '<div style="font-size:1.8rem;margin-bottom:6px">🤖</div>'
        chat_html += '<div style="font-size:.9rem;font-weight:700;color:#e0e7ff">Hey! I\'m your Buddy!</div>'
        chat_html += '<div style="font-size:.74rem;color:#a5b4fc;margin-top:4px">Type below and press <b>Enter</b> or click <b>Send</b> 👇</div>'
        chat_html += '</div>'
    else:
        chat_html = '<div class="chat-wrap">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f'<div class="chat-bubble-wrap-user"><div class="bubble-user">{msg["content"]}</div><div class="avatar avatar-user">👤</div></div>'
            else:
                chat_html += f'<div class="chat-bubble-wrap-ai"><div class="avatar avatar-ai">🤖</div><div class="bubble-ai">{msg["content"]}</div></div>'
        chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    # ── Handle pending message (sent via Enter key) ──────────────
    if st.session_state.pending_msg:
        msg_to_send = st.session_state.pending_msg
        st.session_state.pending_msg = ""
        st.session_state.chat_history.append({"role": "user", "content": msg_to_send})
        with st.spinner("🤖 Buddy is thinking..."):
            ai_response = generate_coach_response(msg_to_send, user_name, user_goal, user_skill, user_data, gemini_api_key)
        st.session_state.chat_history.append({"role": "ai", "content": ai_response})
        st.rerun()

    # Input box — on_change fires when Enter is pressed
    user_input = st.text_input(
        "Your message",
        placeholder="💬 Type your message and press Enter to send...",
        key=f"chat_input_{st.session_state.input_key}",
        label_visibility="collapsed",
        on_change=on_enter
    )

    # Send + Clear — equal width so Clear never wraps
    col_send, col_clear = st.columns([3, 1])
    with col_send:
        send_clicked = st.button("🚀 Send Message", use_container_width=True, key="send_btn")
        if send_clicked and user_input.strip():
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner("🤖 Thinking..."):
                ai_response = generate_coach_response(user_input, user_name, user_goal, user_skill, user_data, gemini_api_key)
            st.session_state.chat_history.append({"role": "ai", "content": ai_response})
            st.session_state.input_key += 1
            st.rerun()
    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_btn"):
            st.session_state.chat_history = []
            st.session_state.input_key += 1
            st.rerun()

# ── AGE-BASED PLAYLIST SUGGESTIONS (right column) ────────────
with col2:
    st.markdown("""
    <div class="card-title">🎧 Playlist Suggestions by Category</div>
    <div class="card-sub">Personalized playlists for your age group &amp; interests</div>
    """, unsafe_allow_html=True)

    def get_categorized_playlists(age, goal, skill):
        """Generate age-appropriate playlists across health, gardening, and education categories."""
        if age < 18:
            return {
                "🌱 Gardening & Nature": [
                    {"label": "Urban Gardening for Teens", "icon": "🌿", "url": "https://www.youtube.com/results?search_query=urban+gardening+for+teenagers"},
                    {"label": "Plant Care Basics", "icon": "🌻", "url": "https://www.youtube.com/results?search_query=indoor+plants+care+beginner"},
                    {"label": "Gardening Challenges", "icon": "🥕", "url": "https://www.youtube.com/results?search_query=gardening+challenges+teens"},
                ],
                "💪 Health & Fitness": [
                    {"label": "Teen Fitness Routines", "icon": "🏃", "url": "https://www.youtube.com/results?search_query=teen+fitness+workout+routine"},
                    {"label": "Mental Health Tips", "icon": "🧠", "url": "https://www.youtube.com/results?search_query=teen+mental+health+tips"},
                    {"label": "Healthy Eating for Teens", "icon": "🥗", "url": "https://www.youtube.com/results?search_query=healthy+eating+teenagers"},
                ],
                "📚 Education & Skills": [
                    {"label": "YouTube Educational", "icon": "▶️", "url": f"https://www.youtube.com/results?search_query={goal.replace(' ','+')}+tutorial"},
                    {"label": "Khan Academy", "icon": "🎓", "url": f"https://www.khanacademy.org/search?page_search_query={goal.replace(' ','+')}"},
                    {"label": "Crash Course Videos", "icon": "⚡", "url": "https://www.youtube.com/results?search_query=crash+course+learning"},
                ],
            }
        elif age < 25:
            return {
                "🌱 Gardening & Sustainability": [
                    {"label": "Sustainable Gardening", "icon": "🌍", "url": "https://www.youtube.com/results?search_query=sustainable+gardening+tutorial"},
                    {"label": "Balcony Farming Guide", "icon": "🌱", "url": "https://www.youtube.com/results?search_query=balcony+farming+complete+guide"},
                    {"label": "Organic Growing Methods", "icon": "🍃", "url": "https://www.youtube.com/results?search_query=organic+gardening+full+course"},
                ],
                "💪 Health & Wellness": [
                    {"label": "Fitness & Nutrition", "icon": "💪", "url": "https://www.udemy.com/courses/search/?q=fitness+nutrition"},
                    {"label": "Mental Wellness", "icon": "🧘", "url": "https://www.youtube.com/results?search_query=mental+wellness+young+adults"},
                    {"label": "Healthy Lifestyle", "icon": "❤️", "url": "https://www.coursera.org/search?query=health+wellness"},
                ],
                "📚 Career & Education": [
                    {"label": "freeCodeCamp Courses", "icon": "💻", "url": "https://www.freecodecamp.org"},
                    {"label": "Coursera Programs", "icon": "🎓", "url": f"https://www.coursera.org/search?query={goal.replace(' ','+')}"},
                    {"label": "Skill Development", "icon": "🚀", "url": f"https://www.udemy.com/courses/search/?q={goal.replace(' ','+')}"},
                ],
            }
        elif age < 40:
            return {
                "🌱 Gardening & Home": [
                    {"label": "Home Garden Design", "icon": "🏡", "url": "https://www.youtube.com/results?search_query=home+garden+design+ideas"},
                    {"label": "Vegetable Gardening", "icon": "🥦", "url": "https://www.youtube.com/results?search_query=vegetable+gardening+guide"},
                    {"label": "Landscape Architecture", "icon": "🌳", "url": "https://www.coursera.org/search?query=landscape+design"},
                ],
                "💪 Health & Work-Life Balance": [
                    {"label": "Executive Fitness", "icon": "🏋️", "url": "https://www.linkedin.com/learning/search?keywords=fitness"},
                    {"label": "Stress Management", "icon": "🧘", "url": "https://www.udemy.com/courses/search/?q=stress+management"},
                    {"label": "Nutrition Planning", "icon": "🥗", "url": "https://www.masterclass.com/search?q=nutrition"},
                ],
                "📚 Professional Development": [
                    {"label": "LinkedIn Learning", "icon": "💼", "url": f"https://www.linkedin.com/learning/search?keywords={goal.replace(' ','+')}"},
                    {"label": "Advanced Udemy", "icon": "🎯", "url": f"https://www.udemy.com/courses/search/?q={goal.replace(' ','+')}"},
                    {"label": "Industry Certifications", "icon": "🏆", "url": "https://www.coursera.org/search?query=professional+certificate"},
                ],
            }
        else:
            return {
                "🌱 Gardening & Relaxation": [
                    {"label": "Therapeutic Gardening", "icon": "🌸", "url": "https://www.youtube.com/results?search_query=therapeutic+gardening+seniors"},
                    {"label": "Flower Arrangement", "icon": "💐", "url": "https://www.youtube.com/results?search_query=flower+arrangement+tutorial"},
                    {"label": "Growing Herbs", "icon": "🌿", "url": "https://www.youtube.com/results?search_query=herbs+gardening+guide"},
                ],
                "💪 Health & Wellness": [
                    {"label": "Low-Impact Exercise", "icon": "🚴", "url": "https://www.youtube.com/results?search_query=low+impact+exercise+adults"},
                    {"label": "Senior Health", "icon": "❤️", "url": "https://www.coursera.org/search?query=senior+health"},
                    {"label": "Nutrition for 40+", "icon": "🥗", "url": "https://www.masterclass.com/search?q=nutrition"},
                ],
                "📚 Lifelong Learning": [
                    {"label": "MasterClass", "icon": "🌟", "url": "https://www.masterclass.com"},
                    {"label": "Skillshare Classes", "icon": "🎨", "url": f"https://www.skillshare.com/en/search?query={goal.replace(' ','+')}"},
                    {"label": "YouTube Tutorials", "icon": "▶️", "url": f"https://www.youtube.com/results?search_query={goal.replace(' ','+')}+step+by+step"},
                ],
            }

    playlists_by_category = get_categorized_playlists(user_age, user_goal, user_skill)

    for category, playlists in playlists_by_category.items():
        st.markdown(f"""
        <div style="margin-bottom:16px;">
          <div style="font-size:.85rem;font-weight:700;color:#a5b4fc;margin-bottom:8px;letter-spacing:.3px">{category}</div>
        </div>
        """, unsafe_allow_html=True)
        for pl in playlists:
            st.markdown(f"""
            <a href="{pl['url']}" target="_blank" style="text-decoration:none;display:block;margin-bottom:8px;">
              <div style="display:flex;align-items:center;gap:10px;background:#1e2540;
                          border:1px solid rgba(99,102,241,0.2);
                          border-radius:10px;padding:12px 14px;cursor:pointer;">
                <div style="font-size:1.1rem;">{pl['icon']}</div>
                <div style="flex:1;">
                  <div style="font-size:.8rem;font-weight:700;color:#e0e7ff;">{pl['label']}</div>
                </div>
                <div style="color:#818cf8;font-size:.85rem;font-weight:600;">→</div>
              </div>
            </a>
            """, unsafe_allow_html=True)


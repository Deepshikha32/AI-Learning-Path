"""
AI Coach — Gemini-first architecture.
Injects full user profile + roadmap into every Gemini call so responses are
truly personalised. Falls back to a structured local engine when the API is
unavailable.
"""
import os
import random
import textwrap
import urllib.parse

import streamlit as st
import google.generativeai as genai

from core.sidebar import render_sidebar

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Coach",
    page_icon="🎓",
    initial_sidebar_state="expanded",
    layout="wide",
)
render_sidebar()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #f5f3ff !important; }
.block-container { padding-top: 1.8rem !important; }
#MainMenu, footer { visibility: hidden; }

/* ── Header ── */
.coach-header {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
    padding: 32px 40px; border-radius: 20px; color: white;
    margin-bottom: 22px; text-align: center;
    box-shadow: 0 8px 32px rgba(124,58,237,.28);
}
.coach-header h1 {
    margin: 0; font-size: 2.2em;
    font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: -0.5px;
}
.coach-header p { margin: 8px 0 0; opacity: .88; font-size: .95rem; }

/* ── Context ribbon ── */
.ctx-bar {
    background: white; border: 1.5px solid #ede9fe;
    border-radius: 16px; padding: 12px 18px; margin-bottom: 16px;
    display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
    box-shadow: 0 2px 12px rgba(124,58,237,.07);
}
.ctx-chip {
    background: #f5f3ff; border: 1.5px solid #ddd6fe; border-radius: 20px;
    padding: 4px 13px; font-size: .76rem; font-weight: 600; color: #5b21b6;
    display: inline-flex; align-items: center; gap: 4px; transition: all .18s;
}
.ctx-chip:hover { background: #ede9fe; border-color: #a78bfa; }
.ctx-chip b { color: #7c3aed; }

/* ── Mini progress bar ── */
.mini-bar {
    display: inline-block; width: 64px; height: 6px;
    background: #ede9fe; border-radius: 9px; overflow: hidden;
    vertical-align: middle; margin-left: 5px;
}
.mini-bar-fill {
    height: 100%; border-radius: 9px;
    background: linear-gradient(90deg, #7c3aed, #a855f7);
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #ede9fe !important; border-radius: 14px !important;
    padding: 4px !important; gap: 3px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border-radius: 10px !important;
    color: #7c3aed !important; font-weight: 600 !important;
    padding: 8px 20px !important; font-size: .84rem !important;
    transition: all .18s !important;
}
.stTabs [aria-selected="true"] {
    background: white !important; color: #6d28d9 !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 10px rgba(124,58,237,.15) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: white !important; border: 1.5px solid #ddd6fe !important;
    border-radius: 22px !important; color: #6d28d9 !important;
    font-size: .81rem !important; font-weight: 700 !important;
    padding: 6px 16px !important; transition: all .18s !important;
}
.stButton > button:hover {
    background: #7c3aed !important; border-color: #7c3aed !important;
    color: white !important; box-shadow: 0 4px 16px rgba(124,58,237,.28) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Chat wrapper ── */
.chat-wrap {
    background: white; border: 1.5px solid #ede9fe;
    border-radius: 16px; padding: 16px; margin: 10px 0; min-height: 200px;
    box-shadow: 0 2px 14px rgba(124,58,237,.07);
}

/* ── Chat input ── */
[data-testid="stChatInput"] > div {
    background: white !important; border: 1.5px solid #ddd6fe !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 10px rgba(124,58,237,.09) !important;
    transition: all .18s !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,.14) !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    background: #f5f3ff !important; border: 1.5px solid #ede9fe !important;
    border-radius: 12px !important; color: #5b21b6 !important;
    font-weight: 700 !important; transition: background .18s !important;
}
.streamlit-expanderHeader:hover { background: #ede9fe !important; }
.streamlit-expanderContent {
    background: #faf9ff !important; border: 1.5px solid #ede9fe !important;
    border-top: none !important; border-radius: 0 0 12px 12px !important;
}
.streamlit-expanderContent a {
    color: #7c3aed !important; font-weight: 600 !important;
    text-decoration: none !important; transition: color .15s !important;
}
.streamlit-expanderContent a:hover {
    color: #5b21b6 !important; text-decoration: underline !important;
}

/* ── Alerts / info ── */
.stAlert {
    background: #f5f3ff !important; border: 1.5px solid #ddd6fe !important;
    border-radius: 14px !important; color: #4c1d95 !important;
}

/* ── Dividers ── */
hr {
    border: none !important; height: 1px !important; margin: 14px 0 !important;
    background: linear-gradient(90deg, transparent, #ddd6fe, transparent) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #f5f3ff; border-radius: 9px; }
::-webkit-scrollbar-thumb { background: #c4b5fd; border-radius: 9px; }
::-webkit-scrollbar-thumb:hover { background: #7c3aed; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #7c3aed !important; }
</style>
""", unsafe_allow_html=True)



# ═══════════════════════════════════════════════════════════════════════════════
#  USER CONTEXT  — reads everything set by the dashboard into session_state
# ═══════════════════════════════════════════════════════════════════════════════

def get_user_context() -> dict:
    """Snapshot current user data from dashboard session state."""
    ctx = {
        "name"     : st.session_state.get("name",   "") or "Learner",
        "goal"     : st.session_state.get("goal",   "") or "",
        "domain"   : st.session_state.get("domain", "") or "",
        "skill"    : st.session_state.get("skill",  "") or "Beginner",
        "hrs"      : float(st.session_state.get("hrs", 1.5)),
        "health"   : st.session_state.get("health", "") or "",
        "age"      : int(st.session_state.get("age", 22)),
        "generated": st.session_state.get("generated", False),
        "result"   : st.session_state.get("result",  None),
    }
    if ctx["generated"] and ctx["result"]:
        roadmap = ctx["result"].get("roadmap", [])
        done: list = []
        try:
            from core.engine import get_user
            udata = get_user(ctx["name"], ctx["age"]) or {}
            done  = udata.get("completed", [])
        except Exception:
            pass
        done_count     = len([t for t in roadmap if t["topic"] in done])
        total          = len(roadmap)
        ctx.update({
            "roadmap"     : roadmap,
            "done"        : done,
            "total_topics": total,
            "done_count"  : done_count,
            "progress_pct": round(done_count / max(total, 1) * 100),
            "next_topic"  : roadmap[done_count]["topic"] if done_count < total else None,
            "total_weeks" : ctx["result"].get("total_w", 0),
            "total_hours" : ctx["result"].get("total_h", 0),
        })
    else:
        ctx.update({
            "roadmap": [], "done": [], "total_topics": 0,
            "done_count": 0, "progress_pct": 0,
            "next_topic": None, "total_weeks": 0, "total_hours": 0,
        })
    return ctx


# ═══════════════════════════════════════════════════════════════════════════════
#  PLAYLIST DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

def _yt(q: str) -> str:
    return "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(q)

PLAYLISTS: dict[str, dict] = {
    "Health & Wellness": {
        "emoji": "🏥",
        "items": [
            ("Healthy Eating Tips",     _yt("healthy eating tips")),
            ("Nutrition Guide",         _yt("nutrition guide")),
            ("Daily Wellness Routine",  _yt("daily wellness routine")),
            ("Health Hacks",            _yt("health hacks")),
        ],
    },
    "Fitness & Exercise": {
        "emoji": "💪",
        "items": [
            ("Home Workout",            _yt("home workout")),
            ("Cardio Training",         _yt("cardio training")),
            ("Strength Building",       _yt("strength training")),
            ("Yoga & Stretching",       _yt("yoga stretching")),
        ],
    },
    "Dancing & Arts": {
        "emoji": "💃",
        "items": [
            ("Beginner Dance Tutorial", _yt("beginner dance tutorial")),
            ("Choreography",            _yt("dance choreography")),
            ("Music & Rhythm",          _yt("music rhythm training")),
            ("Dance Styles",            _yt("different dance styles")),
        ],
    },
    "Gardening & Nature": {
        "emoji": "🌱",
        "items": [
            ("Indoor Gardening",        _yt("indoor plant care")),
            ("Organic Farming",         _yt("organic farming basics")),
            ("Vegetable Garden",        _yt("home vegetable garden")),
            ("Plant Care Tips",         _yt("plant care guide")),
        ],
    },
    "Career Development": {
        "emoji": "💼",
        "items": [
            ("Resume Writing Tips",     _yt("resume writing tips")),
            ("Interview Skills",        _yt("job interview tips")),
            ("Career Growth",           _yt("career growth tips")),
            ("Professional Skills",     _yt("professional skills")),
        ],
    },
    "Mental & Emotional": {
        "emoji": "🧠",
        "items": [
            ("Beginner Meditation",     _yt("beginner meditation")),
            ("Stress Relief Techniques",_yt("stress relief techniques")),
            ("Mindfulness Exercises",   _yt("mindfulness exercises")),
            ("Motivation & Inspiration",_yt("motivation and inspiration")),
        ],
    },
    "Learning & Skills": {
        "emoji": "📚",
        "items": [
            ("Programming Tutorial",    _yt("programming tutorial")),
            ("Data Science",            _yt("data science tutorial")),
            ("Web Development",         _yt("web development tutorial")),
            ("AI & Machine Learning",   _yt("machine learning tutorial")),
        ],
    },
    "Finance & Payments": {
        "emoji": "💰",
        "items": [
            ("Personal Finance Basics", _yt("personal finance basics")),
            ("Online Payments Guide",   _yt("online payment methods guide")),
            ("Paytm Tutorial",          _yt("paytm tutorial hindi")),
            ("UPI & Digital Wallet",    _yt("UPI payment tutorial")),
            ("Budgeting Tips",          _yt("budgeting tips for beginners")),
            ("Investing Basics",        _yt("investing for beginners india")),
        ],
    },
    "Cooking & Food": {
        "emoji": "🍳",
        "items": [
            ("Quick Easy Recipes",      _yt("quick easy recipes")),
            ("Healthy Cooking Tips",    _yt("healthy cooking tips")),
            ("Indian Recipes",          _yt("indian recipes for beginners")),
            ("Baking for Beginners",    _yt("baking for beginners")),
        ],
    },
    "Business & Entrepreneurship": {
        "emoji": "🚀",
        "items": [
            ("Start a Business",        _yt("how to start a business")),
            ("Digital Marketing",       _yt("digital marketing for beginners")),
            ("Freelancing Guide",       _yt("freelancing tips for beginners")),
            ("Startup Ideas 2024",      _yt("startup ideas 2024")),
        ],
    },
    "Language Learning": {
        "emoji": "🗣️",
        "items": [
            ("English Speaking Practice",_yt("english speaking practice")),
            ("Spoken English Tips",     _yt("spoken english tips")),
            ("Vocabulary Building",     _yt("vocabulary building english")),
            ("English Grammar Guide",   _yt("english grammar for beginners")),
        ],
    },
    "Science & Technology": {
        "emoji": "🔬",
        "items": [
            ("Science Explained",       _yt("science explained simply")),
            ("Space & Universe",        _yt("space universe documentary")),
            ("Technology Trends 2024",  _yt("technology trends 2024")),
            ("Physics Basics",          _yt("physics basics explained")),
        ],
    },
    "Photography & Video": {
        "emoji": "📸",
        "items": [
            ("Phone Photography Tips",  _yt("phone photography tips")),
            ("Video Editing Tutorial",  _yt("video editing tutorial")),
            ("Camera Basics",           _yt("camera basics beginners")),
            ("Grow YouTube Channel",    _yt("how to grow youtube channel")),
        ],
    },
}

# Domain → playlist name
DOMAIN_PLAYLIST: dict[str, str] = {
    "Education":        "Learning & Skills",
    "Entrepreneurship": "Business & Entrepreneurship",
    "Health":           "Health & Wellness",
    "Hobbies":          "Dancing & Arts",
    "Gardening":        "Gardening & Nature",
    "Programming":      "Learning & Skills",
    "Fitness":          "Fitness & Exercise",
    "Cooking":          "Cooking & Food",
    "Music":            "Dancing & Arts",
    "Art":              "Photography & Video",
    "Business":         "Business & Entrepreneurship",
    "Language Learning":"Language Learning",
    "Personal Finance": "Finance & Payments",
    "Mental Wellness":  "Mental & Emotional",
    "Design":           "Photography & Video",
    "Photography":      "Photography & Video",
}

# Keyword → playlist name (substring match — no word-boundary restriction)
_KW_MAP: list[tuple[list[str], str]] = [
    (["health", "wellness", "nutrition", "diet", "medical", "sick", "disease",
      "doctor", "vitamin", "cholesterol", "diabetes", "blood pressure", "immune"],
     "Health & Wellness"),
    (["workout", "exercise", "fitness", "gym", "cardio", "strength", "muscle",
      "weight loss", "abs", "running", "yoga", "home workout", "jogging"],
     "Fitness & Exercise"),
    (["dance", "dancing", "choreograph", "ballet", "salsa", "hip hop", "groove",
      "bhangra", "zumba", "bollywood dance"],
     "Dancing & Arts"),
    (["garden", "gardening", "plant", "plants", "flower", "vegetable", "farming",
      "organic", "soil", "seeds", "herbs", "compost", "grow", "harvest"],
     "Gardening & Nature"),
    (["career", "resume", "interview", "job", "employment", "linkedin",
      "salary", "professional", "placement", "promotion", "switch job"],
     "Career Development"),
    (["meditation", "stress", "anxiety", "mindful", "mental health",
      "depression", "motivation", "calm", "peace", "burnout", "overthink",
      "sleep better", "mindfulness"],
     "Mental & Emotional"),
    (["python", "javascript", "coding", "programming", "data science",
      "web development", "web dev", "machine learning", "artificial intelligence",
      "html", "css", "sql", "software", "flask", "django", "react", "deep learning"],
     "Learning & Skills"),
    (["payment", "paytm", "upi", "gpay", "phonepe", "google pay", "neft",
      "imps", "rtgs", "digital wallet", "net banking", "invest", "investing",
      "budget", "budgeting", "finance", "money", "saving", "loan", "emi",
      "credit card", "debit card", "sip", "mutual fund", "stock", "share market"],
     "Finance & Payments"),
    (["cook", "cooking", "recipe", "kitchen", "baking", "bake", "chef",
      "cuisine", "meal", "food", "dinner", "breakfast", "lunch"],
     "Cooking & Food"),
    (["business", "startup", "entrepreneur", "entrepreneurship", "marketing",
      "freelance", "freelancing", "brand", "sales", "ecommerce", "online business"],
     "Business & Entrepreneurship"),
    (["english", "language", "grammar", "vocabulary", "pronunciation",
      "fluent", "fluency", "speaking", "spoken english", "communication"],
     "Language Learning"),
    (["science", "physics", "chemistry", "biology", "space", "universe",
      "astronomy", "technology", "tech", "quantum", "renewable energy"],
     "Science & Technology"),
    (["photography", "camera", "photo", "video editing", "vlog",
      "youtube channel", "reel", "content creator", "film"],
     "Photography & Video"),
]


def _topic_from_query(query: str) -> str | None:
    """Substring match — handles 'gardening' matching 'garden', 'cooking' matching 'cook', etc."""
    q = query.lower()
    for keywords, playlist in _KW_MAP:
        for kw in keywords:
            if kw in q:   # simple substring, not word-boundary
                return playlist
    return None


def _wants_playlist(query: str) -> bool:
    signals = ["playlist", "video", "videos", "watch", "youtube", "show me", "give me",
               "suggest", "recommend", "resource", "tutorial", "for the same", "for same",
               "for it", "related to", "link", "channel"]
    q = query.lower()
    return any(s in q for s in signals)


def _dynamic_playlist(topic: str) -> dict:
    s = urllib.parse.quote_plus(topic)
    return {
        "emoji": "📺",
        "items": [
            (f"{topic} – Full Tutorial",    f"https://www.youtube.com/results?search_query={s}+tutorial"),
            (f"{topic} for Beginners",      f"https://www.youtube.com/results?search_query={s}+beginners"),
            (f"{topic} – Tips & Tricks",    f"https://www.youtube.com/results?search_query={s}+tips"),
            (f"{topic} – Explained Simply", f"https://www.youtube.com/results?search_query={s}+explained"),
            (f"{topic} – Step by Step",     f"https://www.youtube.com/results?search_query={s}+step+by+step"),
        ],
    }


def resolve_playlists(query: str, ctx: dict) -> list[tuple[str, dict]]:
    """
    ALWAYS returns at least one playlist.
    Priority: topic keyword match → wants-playlist signal → domain default → dynamic fallback.
    """
    q = query.lower().strip()

    # 1. Topic detected from keywords (substring match)
    topic_name = _topic_from_query(query)
    if topic_name and topic_name in PLAYLISTS:
        st.session_state.last_topic = topic_name
        return [(topic_name, PLAYLISTS[topic_name])]

    # 2. User explicitly asked for a playlist/video
    if _wants_playlist(query):
        # Use roadmap next topic first
        if ctx.get("next_topic"):
            nxt = ctx["next_topic"]
            st.session_state.last_topic = nxt
            return [(f"📖 {nxt} Videos", _dynamic_playlist(nxt))]
        # Use remembered last topic
        lt = st.session_state.get("last_topic")
        if lt:
            if lt in PLAYLISTS:
                return [(lt, PLAYLISTS[lt])]
            return [(f"📺 {lt}", _dynamic_playlist(lt))]

    # 3. Domain playlist suggestion
    domain  = ctx.get("domain", "")
    pl_name = DOMAIN_PLAYLIST.get(domain)
    if pl_name and pl_name in PLAYLISTS:
        return [(pl_name, PLAYLISTS[pl_name])]

    # 4. ALWAYS show something — generate a dynamic YouTube search for this exact query
    if q and len(q) > 3 and not _is_greeting(query):
        # Extract the meaningful part of the query (strip question words)
        clean = q
        for strip_word in ["how to ", "how do i ", "what is ", "tell me about ",
                           "explain ", "can you ", "please ", "show me "]:
            clean = clean.replace(strip_word, "")
        clean = clean.strip("?!.,").strip()
        if clean and len(clean) > 2:
            return [(f"📺 Videos: {clean.title()}", _dynamic_playlist(clean))]

    return []


# ═══════════════════════════════════════════════════════════════════════════════
#  SYSTEM PROMPT  — rich user context injected into every Gemini call
# ═══════════════════════════════════════════════════════════════════════════════

def build_system_prompt(ctx: dict) -> str:
    roadmap_preview = ""
    if ctx["roadmap"]:
        done_set = set(ctx["done"])
        lines = []
        for t in ctx["roadmap"][:20]:         # first 20 topics max
            mark = "✅" if t["topic"] in done_set else "⬜"
            lines.append(f"  {mark} Week {t['week']}: {t['topic']} ({t['duration']}h)")
        if len(ctx["roadmap"]) > 20:
            lines.append(f"  … and {len(ctx['roadmap'])-20} more topics")
        roadmap_preview = "\n".join(lines)

    health_note = f"\nHealth condition: {ctx['health']}" if ctx["health"] else ""

    prompt = textwrap.dedent(f"""
    You are an expert AI Learning Coach — energetic, warm, and deeply knowledgeable.
    You have direct access to this user's live dashboard data. Always use it!

    ══ USER PROFILE ══
    Name          : {ctx['name']}
    Age           : {ctx['age']}
    Domain        : {ctx['domain'] or 'Not set'}
    Learning Goal : {ctx['goal'] or 'Not set yet'}
    Skill Level   : {ctx['skill']}
    Study Time    : {ctx['hrs']} hours/day{health_note}

    ══ LEARNING PROGRESS ══
    Has Roadmap   : {'Yes' if ctx['generated'] else 'No — ask them to visit Dashboard first'}
    Total Topics  : {ctx['total_topics']}
    Completed     : {ctx['done_count']} ({ctx['progress_pct']}%)
    Remaining     : {ctx['total_topics'] - ctx['done_count']}
    Total Weeks   : {ctx['total_weeks']}
    Next Topic    : {ctx['next_topic'] or 'All done! 🎉'}

    ══ ROADMAP (first 20 topics) ══
    {roadmap_preview or 'No roadmap generated yet.'}

    ══ YOUR ROLE ══
    - Answer EVERY question in a personalized, encouraging, and actionable way.
    - When the user asks about THEIR roadmap, learning path, plan, or progress →
      show their ACTUAL data from above (not generic advice).
    - When the user asks "what should I learn next?" → tell them exactly:
      "{ctx['next_topic'] or 'All topics are done!'}"
    - When they ask about progress → give the real numbers above.
    - When they ask about playlists / videos → tell them you're showing YouTube
      resources below (the UI attaches them automatically).
    - Keep answers concise, use emojis, use markdown tables when data helps.
    - NEVER give generic "here are 7 steps to master anything" responses when
      you have real user data. Use the data above!
    - If they haven't generated a roadmap yet, encourage them to visit the
      Dashboard first, then answer their general question fully.
    """).strip()

    return prompt


# ═══════════════════════════════════════════════════════════════════════════════
#  LOCAL FALLBACK ENGINE  — used when Gemini API is unavailable
# ═══════════════════════════════════════════════════════════════════════════════

_GREETING_WDS = {"hlo","hello","hi","hey","howdy","greetings","sup","heya",
                 "hiya","namaste","hii","hlw","helo","hai","good morning",
                 "good afternoon","good evening"}

def _is_greeting(query: str) -> bool:
    q = query.lower().strip("!?.,:;")
    # Pure greeting if the whole message is a greeting word/phrase
    return q in _GREETING_WDS or all(w in _GREETING_WDS for w in q.split())

def _local_answer(query: str, ctx: dict) -> str:
    q     = query.lower()
    name  = ctx["name"]
    goal  = ctx["goal"]  or "your goal"
    domain= ctx["domain"] or "your domain"
    skill = ctx["skill"]
    pct   = ctx["progress_pct"]
    done  = ctx["done_count"]
    total = ctx["total_topics"]
    nxt   = ctx["next_topic"] or "All done! 🎉"
    hrs   = ctx["hrs"]
    weeks = ctx["total_weeks"]

    # ── Greeting ──────────────────────────────────────────────────────────────
    if _is_greeting(query):
        if ctx["generated"]:
            bar_pct = pct
            return textwrap.dedent(f"""
            🌟 **Welcome back, {name}!** Your AI Coach is live & synced! 🚀

            📊 **Your Dashboard Snapshot:**
            | | |
            |---|---|
            | 🎯 Goal | **{goal}** |
            | 🌐 Domain | {domain} |
            | 🏅 Skill | {skill} |
            | ✅ Progress | **{done}/{total} topics ({pct}%)** |
            | 📅 Duration | {weeks} weeks |
            | 🔜 Next | **{nxt}** |

            **What can I help you with today?**
            - *"What should I learn next?"*
            - *"Show me videos for {nxt}"*
            - *"How do I master {goal}?"*
            - *"Show me my progress"*
            - Or ask me **anything!** 😊
            """).strip()
        else:
            return textwrap.dedent(f"""
            🌟 **Hey {name}, welcome to your AI Coach!** 🎓

            I see you haven't generated your Learning Path yet.
            👉 Head to the **Dashboard**, fill your profile and click
            **"Generate My Learning Path"** — then I'll coach you with
            fully personalised advice!

            **Meanwhile, ask me anything:**
            - Finance, coding, health, fitness, career…
            - I'll suggest YouTube playlists for any topic!
            """).strip()

    # ── Progress / dashboard summary ──────────────────────────────────────────
    if any(kw in q for kw in ["progress", "how am i doing", "how far", "percent", "dashboard", "stats"]):
        if ctx["generated"]:
            emoji = "🔥" if pct >= 70 else ("💪" if pct >= 30 else "🌱")
            return textwrap.dedent(f"""
            📊 **Your Progress Report, {name}!**

            | Metric | Value |
            |--------|-------|
            | ✅ Completed | {done} topics |
            | 📚 Remaining | {total - done} topics |
            | 📈 Progress | **{pct}%** |
            | 🎯 Goal | {goal} |
            | 🔜 Up Next | {nxt} |
            | ⏱ Study | {hrs}h/day |

            {emoji} {"Great momentum — top half of your journey!" if pct >= 50 else "Stay consistent — big things take time!"}

            Type *"what should I learn next"* to get your next step! 🚀
            """).strip()
        return "📊 No roadmap yet — visit the **Dashboard** to generate your Learning Path first!"

    # ── Next topic ────────────────────────────────────────────────────────────
    if any(kw in q for kw in ["next topic", "what next", "what should i", "learn next",
                               "next step", "what to study", "what do i study"]):
        if ctx["generated"] and ctx["next_topic"]:
            return textwrap.dedent(f"""
            🎯 **Your next topic: *{nxt}***

            Based on your **{goal}** goal at **{skill}** level.

            How to tackle it:
            1. 🎬 Watch 1-2 intro videos (playlist below!)
            2. 📝 Take quick notes on key concepts
            3. ✍️ Do a small practice exercise immediately
            4. 🔁 Revisit after 2 days to reinforce memory
            5. ✅ Mark it done on the Dashboard

            Estimated time: check your roadmap for duration.
            I'm attaching YouTube resources below! 🚀
            """).strip()
        return "🗺️ Generate your **Learning Path** on the Dashboard and I'll tell you exactly what to study next!"

    # ── Roadmap / learning path ───────────────────────────────────────────────
    if any(kw in q for kw in ["roadmap", "learning path", "my plan", "syllabus",
                               "my course", "all topics", "show me my", "see my"]):
        if ctx["generated"]:
            done_set = set(ctx["done"])
            rows = "\n".join(
                f"| {'✅' if t['topic'] in done_set else '⬜'} | Week {t['week']} "
                f"| **{t['topic']}** | {t['duration']}h |"
                for t in ctx["roadmap"][:15]
            )
            more = f"\n*…and {len(ctx['roadmap'])-15} more topics — see the Roadmap page.*" \
                   if len(ctx["roadmap"]) > 15 else ""
            return textwrap.dedent(f"""
            🗺️ **Your Learning Roadmap for: *{goal}***

            | | Week | Topic | Hours |
            |--|------|-------|-------|
            {rows}
            {more}

            📅 **Total:** {weeks} weeks  |  ✅ **Done:** {done}/{total} ({pct}%)

            Visit the **Roadmap** page to tick off topics as you finish them! 🚀
            """).strip()
        return "🗺️ No roadmap yet — visit the **Dashboard** to generate your personalised Learning Path!"

    # ── Motivation ────────────────────────────────────────────────────────────
    if any(kw in q for kw in ["motivat", "stuck", "bored", "give up", "hard",
                               "difficult", "struggling", "can't", "lazy"]):
        return textwrap.dedent(f"""
        💪 **You've got this, {name}!** 🔥

        You're **{pct}%** through your journey toward *{goal}*.
        That's not nothing — that's real, earned progress.

        **Quick reset:**
        1. 🎯 Focus on ONE topic for the next 25 mins (Pomodoro)
        2. ✅ Look at your completed list — you've done a lot already!
        3. 🧘 5-min walk → come back fresh
        4. 📅 Even 15 mins of study today > 0 mins

        *"Consistency beats intensity every single time."* 🌟

        What's stopping you right now? Let's talk through it! 😊
        """).strip()

    # ── Health-aware ─────────────────────────────────────────────────────────
    if ctx["health"] and any(kw in q for kw in ["health", "condition", "pain", "injury", "exercise"]):
        return textwrap.dedent(f"""
        💙 **Health-Aware Coaching for You** ({ctx['health']})

        - ✅ Always consult your doctor before new exercises
        - 🧘 Low-impact options: yoga, stretching, chair exercises
        - 💧 Stay hydrated and listen to your body
        - 🛑 Stop if you feel sharp pain (muscle burn is OK)
        - 📱 Check YouTube for "{ctx['health']} friendly exercises"

        I'll attach adapted workout playlists below! 💪
        """).strip()

    # ── Comprehensive topic knowledge base ───────────────────────────────────
    # Each entry: ([keywords], rich_answer)
    _KB: list[tuple[list[str], str]] = [

        # ── Gardening ──
        (["garden", "gardening", "plant", "plants", "flower", "vegetable",
          "farming", "grow", "soil", "seeds", "herbs", "organic", "compost"],
         textwrap.dedent("""
         🌱 **Complete Gardening Guide**

         **Getting Started:**
         1. 🌍 **Know your soil** — test pH (6.0–7.0 is ideal for most plants)
         2. ☀️ **Sunlight** — most veggies need 6–8 hours of direct sun
         3. 💧 **Water at the base**, not the leaves; morning is best
         4. 🧪 **Use compost** or organic fertiliser every 2–4 weeks
         5. 🌿 **Start small** — 3-4 plants, then expand as you learn

         **Best Beginner Plants:**
         | Indoor | Outdoor |
         |--------|--------|
         | Aloe Vera | Tomatoes |
         | Pothos | Mint & Basil |
         | Peace Lily | Marigolds |
         | Spider Plant | Chillies |

         **Common Mistakes:**
         - ❌ Overwatering (most common plant killer!)
         - ❌ No drainage holes in pots
         - ❌ Wrong sunlight placement
         - ❌ Planting at the wrong season

         **Tools you need:** Trowel, watering can, gloves, pot with drainage, quality soil mix.

         📺 Playlist below for step-by-step video guides! 🌿
         """)),

        # ── Health & Wellness ──
        (["health", "wellness", "healthy", "nutrition", "diet", "immune",
          "vitamin", "weight", "cholesterol", "diabetes", "blood pressure"],
         textwrap.dedent("""
         🏥 **Health & Wellness Guide**

         **Daily Non-Negotiables:**
         | Habit | Target |
         |-------|--------|
         | 💧 Water | 8–10 glasses/day |
         | 🥗 Vegetables | 5 colours daily |
         | 🚶 Walking | 8,000–10,000 steps |
         | 😴 Sleep | 7–9 hours |
         | 🧘 Mindfulness | 5–10 mins/day |

         **Nutrition Basics:**
         - Protein: Dal, eggs, paneer, nuts, chicken
         - Complex Carbs: Brown rice, oats, sweet potato
         - Good Fats: Ghee, avocado, nuts, olive oil
         - Fibre: Vegetables, fruits, legumes

         **Avoid:** Processed food, excess sugar, refined flour, packaged snacks.

         **Quick Tips:**
         - Eat slowly — it takes 20 mins for your brain to register fullness
         - Meal prep on Sundays to stay on track all week
         - Replace cold drinks with nimbu pani or plain water

         📺 Playlist below for expert health guides! 🏃
         """)),

        # ── Fitness & Exercise ──
        (["fitness", "exercise", "workout", "gym", "cardio", "strength",
          "muscle", "weight loss", "abs", "running", "yoga", "home workout"],
         textwrap.dedent("""
         💪 **Fitness & Exercise Guide**

         **Beginner Weekly Plan:**
         | Day | Activity |
         |-----|----------|
         | Mon | 30 min walk + stretching |
         | Tue | Bodyweight exercises (squats, pushups, planks) |
         | Wed | Rest or yoga |
         | Thu | Cardio (jogging, cycling, skipping) |
         | Fri | Strength (resistance bands or weights) |
         | Sat | Active fun (sport, dance, hiking) |
         | Sun | Rest & recovery |

         **The 3 Pillars:**
         1. 🏃 **Cardio** — heart health, burns calories
         2. 💪 **Strength** — builds muscle, boosts metabolism
         3. 🧘 **Flexibility** — prevents injury, improves posture

         **Home Workout Essentials (No Equipment):**
         - Push-ups, Squats, Lunges, Planks, Burpees
         - 20 mins × 4 days/week = massive results over 3 months!

         **Golden Rule:** Consistency > Intensity. Show up every day.

         📺 Playlist below for guided workout videos! 🏋️
         """)),

        # ── Cooking ──
        (["cook", "cooking", "recipe", "food", "meal", "kitchen",
          "baking", "bake", "chef", "cuisine", "dinner", "breakfast"],
         textwrap.dedent("""
         🍳 **Cooking for Beginners**

         **5 Essential Techniques to Master First:**
         1. 🔥 **Sauté** — cook quickly in hot oil (onions, garlic base)
         2. 💧 **Boil/Simmer** — dal, pasta, rice, soups
         3. 🍳 **Fry** — shallow/deep fry for crispy textures
         4. ♨️ **Steam** — vegetables, idli, momos (healthiest method)
         5. 🫕 **Pressure cook** — dal makhani, biryani, curries fast!

         **Must-Have Pantry Staples:**
         Onions, garlic, ginger, tomatoes, oil, salt, turmeric, cumin, mustard seeds, dal, rice, atta

         **Beginner Recipes to Start With:**
         - Dal tadka (protein + easy)
         - Aloo sabzi (comfort + simple)
         - Egg bhurji (fast + nutritious)
         - Poha (healthy breakfast)
         - Omelette (5 mins!)

         **Kitchen Safety:**
         - Knife away from body when cutting
         - Turn pan handles inward
         - Never leave oil on high heat unattended

         📺 Playlist below for step-by-step cooking videos! 👨‍🍳
         """)),

        # ── Dancing & Arts ──
        (["dance", "dancing", "choreography", "ballet", "salsa",
          "hip hop", "art", "drawing", "painting", "music", "sing"],
         textwrap.dedent("""
         💃 **Dance & Arts Guide**

         **Learning Dance — Step by Step:**
         1. 👁️ Watch & absorb — study your style (Bollywood, Hip-hop, Classical)
         2. 🎵 Feel the beat — clap to music before moving your feet
         3. 🪞 Practice in front of mirror — watch your own form
         4. 📱 Record yourself — biggest learning tool
         5. 🔁 Repeat 8-count combinations until muscle memory builds
         6. 💃 Add expression — dance is storytelling!

         **Best Styles for Beginners:**
         - Bollywood (fun, expressive, no strict rules)
         - Basic Zumba (cardio + dance)
         - Hip-Hop basics (freestyling encouraged)

         **For Art & Drawing:**
         - Start with basic shapes (circle, square, triangle)
         - Sketch daily for 15 mins — just observe and draw what you see
         - Try Procreate (digital) or basic pencil sketching

         📺 Playlist below for tutorials! 🎨
         """)),

        # ── Business & Entrepreneurship ──
        (["business", "startup", "entrepreneur", "entrepreneurship",
          "marketing", "digital marketing", "freelance", "freelancing",
          "brand", "sales", "ecommerce", "online business"],
         textwrap.dedent("""
         🚀 **Business & Entrepreneurship Guide**

         **Starting a Business — The Right Order:**
         1. 💡 **Idea Validation** — is there a real problem? Will people pay?
         2. 📋 **Simple Business Plan** — 1 page is enough to start
         3. 🎯 **Target Audience** — define your ideal customer clearly
         4. 🏗️ **MVP First** — build minimum viable product, get feedback
         5. 📢 **Market It** — Instagram, WhatsApp, Google, Word of mouth
         6. 💰 **Monetise** — pricing, payment, cash flow management
         7. 📈 **Scale** — only after validating that it works!

         **Free Tools for Entrepreneurs:**
         - Canva (design), Notion (planning), Google Analytics
         - Razorpay/Instamojo (payments), Mailchimp (email)
         - Instagram & YouTube (free marketing!)

         **Best Business Books:** Zero to One, E-Myth Revisited, Rich Dad Poor Dad

         📺 Playlist below for startup guidance! 💼
         """)),

        # ── Language & English ──
        (["english", "language", "speak", "speaking", "grammar", "vocabulary",
          "pronunciation", "fluent", "fluency", "hindi", "communication"],
         textwrap.dedent("""
         🗣️ **English Speaking & Language Guide**

         **The 4 Skills to Build (in order):**
         1. 👂 **Listening** — watch English movies/YouTube with subtitles daily
         2. 📖 **Reading** — start with simple news (BBC Learning English)
         3. ✍️ **Writing** — journal 5 sentences in English every day
         4. 🗣️ **Speaking** — speak to yourself, record yourself, find a partner

         **Daily 30-Min Routine:**
         - 10 mins: Watch an English video
         - 10 mins: Repeat new words/phrases out loud
         - 10 mins: Write or speak about anything

         **Best Free Resources:**
         - BBC Learning English (YouTube)
         - Duolingo app (fun + consistent)
         - ELSA Speak app (pronunciation)
         - Speak English with Mr. Duncan (YouTube)

         **Common Mistakes:**
         - Translating from your mother tongue (think in English!)
         - Fear of making mistakes (mistakes = fastest learning)
         - Learning grammar rules instead of speaking

         📺 Playlist below for spoken English practice! 🌍
         """)),

        # ── Science & Technology ──
        (["science", "physics", "chemistry", "biology", "space", "universe",
          "astronomy", "technology", "tech", "gadget", "artificial intelligence",
          "quantum", "renewable energy", "ev", "electric vehicle"],
         textwrap.dedent("""
         🔬 **Science & Technology Guide**

         **Getting Into Science:**
         1. 🎥 Start with YouTube — Veritasium, SciShow, Kurzgesagt, 3Blue1Brown
         2. 📰 Follow: NASA, ISRO, Nature on social media
         3. 📚 Khan Academy — free world-class science courses
         4. 🧪 Do simple experiments at home to understand concepts
         5. 🤯 Ask "why" and "how" about everyday things

         **Trending Tech Areas (2024–2025):**
         | Topic | Why It Matters |
         |-------|----------------|
         | AI & LLMs | Transforming every industry |
         | Quantum Computing | Next computing revolution |
         | Renewable Energy | Solar, wind, EVs growing fast |
         | Biotechnology | Gene editing, health breakthroughs |
         | Space Tech | ISRO, SpaceX expanding rapidly |

         **Best Free Learning:** MIT OpenCourseWare, Coursera, NPTEL

         📺 Playlist below for fascinating science content! 🚀
         """)),

        # ── Photography & Video ──
        (["photography", "photo", "camera", "video", "vlog", "youtube channel",
          "editing", "film", "reel", "instagram", "content creator"],
         textwrap.dedent("""
         📸 **Photography & Video Creation Guide**

         **Photography Basics — The Exposure Triangle:**
         - 📸 **Aperture** (f-stop) — controls depth of field & light
         - ⚡ **Shutter Speed** — freezes or blurs motion
         - 🔆 **ISO** — sensor sensitivity (keep low to avoid grain)

         **Phone Photography Tips:**
         1. Clean your lens before shooting!
         2. Use the grid for composition (Rule of Thirds)
         3. Tap to focus on your subject
         4. Shoot in portrait mode for beautiful background blur
         5. Golden hour (sunrise/sunset) = best natural lighting
         6. Edit with Lightroom Mobile (free)

         **Starting a YouTube Channel:**
         1. Pick ONE clear topic/niche
         2. Consistency > quality at the start — upload weekly
         3. Thumbnail + Title = 80% of clicks
         4. Engage with every comment for the first 6 months
         5. Tools: CapCut (edit), Canva (thumbnails), TubeBuddy (SEO)

         📺 Playlist below for photography & video tutorials! 🎬
         """)),

        # ── Finance & Payments ──
        (["payment", "paytm", "upi", "gpay", "phonepe", "neft", "imps",
          "digital wallet", "net banking", "online payment", "fintech"],
         textwrap.dedent("""
         💰 **Digital Payments Guide**

         | Method | Best For | Limit |
         |--------|----------|-------|
         | UPI (GPay/PhonePe/Paytm) | Instant bank transfers | ₹1 lakh/txn |
         | Debit/Credit Card | Shopping & POS | Varies |
         | Net Banking | Large transfers & bills | No limit |
         | NEFT | Scheduled inter-bank | No limit |
         | IMPS | Instant inter-bank 24/7 | ₹5 lakh |

         **Setting Up UPI (Step by Step):**
         1. Download GPay / PhonePe / Paytm
         2. Register with your mobile number (linked to bank)
         3. Select your bank → set 4-digit UPI PIN
         4. Start sending/receiving with mobile number or QR code

         **Safety Rules — Never Break These:**
         - 🔒 Never share OTP, UPI PIN, or CVV with anyone
         - 🚫 "Receive money" requests NEVER need your PIN
         - ⚠️ Verify the recipient's name before confirming payment
         - 📞 Bank will NEVER call asking for OTP

         📺 Playlist below for payment tutorials! 💳
         """)),

        # ── Investing & Finance ──
        (["invest", "investing", "stock", "mutual fund", "sip", "share market",
          "trading", "saving", "budget", "budgeting", "personal finance",
          "emi", "loan", "credit score"],
         textwrap.dedent("""
         📈 **Personal Finance & Investing Guide**

         **The Financial Pyramid (Build in Order):**
         1. 🏦 Emergency Fund — 3–6 months expenses in FD/savings
         2. 🛡️ Insurance — term life + health insurance first!
         3. 💰 PPF/EPF — safe, tax-free, long-term
         4. 📊 Mutual Fund SIP — even ₹500/month grows massively
         5. 📈 Stocks — only after learning basics
         6. 🪙 Crypto — only with money you can afford to lose

         **SIP Magic (₹5,000/month at 12% for 20 years = ₹50 Lakhs!)**

         **Free Learning Resources:**
         - Zerodha Varsity (best free stock market course)
         - Groww / Kuvera / Paytm Money (start SIP)
         - CA Rachana Ranade YouTube (Hindi finance)
         - Ankur Warikoo YouTube (personal finance)

         **Golden Rule:** Start EARLY, stay CONSISTENT, avoid DEBT.

         📺 Playlist below for finance guidance! 💰
         """)),

        # ── Coding & Tech ──
        (["python", "javascript", "programming", "coding", "software",
          "data science", "machine learning", "web development", "html",
          "css", "sql", "ai", "ml", "deep learning", "react", "django", "flask"],
         textwrap.dedent("""
         💻 **Learning to Code — Full Guide**

         **Choose Your Path:**
         | Path | First Language | Time to Job |
         |------|---------------|-------------|
         | Web Dev | HTML → CSS → JS → React | 6–9 months |
         | Data Science | Python → Pandas → ML | 9–12 months |
         | App Dev | Flutter/React Native | 9–12 months |
         | Backend | Python/Node.js → SQL | 6–9 months |

         **Learning Order (Web Dev):**
         1. HTML & CSS → build 3 static websites
         2. JavaScript → add interactivity
         3. Git & GitHub → version control
         4. React → modern frontend framework
         5. Node.js + Express → backend
         6. SQL/MongoDB → databases
         7. Deploy on Vercel/Netlify → build portfolio

         **Best Free Resources:**
         - freeCodeCamp.org
         - The Odin Project
         - CS50 (Harvard, free on edX)
         - Chai aur Code / Hitesh Choudhary (Hindi)

         **Key Habit:** Code every day — even 30 mins counts!

         📺 Playlist below for coding tutorials! 🚀
         """)),

        # ── Career & Jobs ──
        (["career", "resume", "interview", "job", "linkedin", "placement",
          "salary", "promotion", "switch job", "work", "employment"],
         textwrap.dedent("""
         💼 **Career Development Guide**

         **Job Search Checklist:**
         - ✅ ATS-optimised resume (use keywords from the job description)
         - ✅ LinkedIn: professional photo, headline, 500+ connections
         - ✅ GitHub/Portfolio with 3–5 strong projects
         - ✅ Naukri.com / LinkedIn / Wellfound profiles updated

         **Interview Preparation:**
         1. **STAR Method** — Situation, Task, Action, Result (for HR rounds)
         2. **DSA** — 50 LeetCode easy/medium problems (for tech roles)
         3. **Research the company** — products, culture, recent news
         4. **Prepare 5 questions** to ask the interviewer
         5. **Mock interviews** — practice with a friend or on Pramp

         **Salary Negotiation:**
         - Always give a range, not a single number
         - Let the company make the first offer
         - Compare on Glassdoor / LinkedIn Salary Insights
         - It's okay to ask for 20–30% more — they expect it!

         📺 Playlist below for career guidance! 🎯
         """)),

        # ── Meditation & Mental health ──
        (["meditation", "stress", "anxiety", "mindful", "mindfulness",
          "mental health", "depression", "calm", "peace", "overthink",
          "sleep better", "burnout"],
         textwrap.dedent("""
         🧘 **Mental Wellness & Meditation Guide**

         **5-Minute Starter Meditation:**
         1. Sit comfortably, spine straight
         2. Close eyes, take 3 deep breaths
         3. Focus only on your breath — in & out
         4. When your mind wanders, gently bring it back
         5. End with a moment of gratitude

         **Daily Mental Health Routine:**
         | Time | Practice |
         |------|----------|
         | Morning | 5–10 min meditation or journaling |
         | Afternoon | Short walk, no screen |
         | Evening | Gratitude list (3 things) |
         | Night | No phone 1h before bed |

         **Instant Stress Relief:**
         - **4-7-8 Breathing:** Inhale 4s → Hold 7s → Exhale 8s
         - **Cold water on face** — activates the dive reflex, calms immediately
         - **5-4-3-2-1 method:** Name 5 things you see, 4 hear, 3 touch, 2 smell, 1 taste

         **Apps:** Headspace, Calm, Insight Timer (free)

         📺 Playlist below for guided meditation! 🌿
         """)),
    ]

    # ── Check KB first ────────────────────────────────────────────────────────
    for keywords, answer in _KB:
        if any(kw in q for kw in keywords):
            return answer.strip()

    # ── If query matches a known playlist category, give category-specific tip ─
    detected = _topic_from_query(query)
    if detected:
        return textwrap.dedent(f"""
        ✨ **{detected} — Here's What You Need to Know**

        Great topic choice{f" for your {domain} journey" if ctx['domain'] else ""}!

        **How to get started with *{query}*:**
        1. 🎬 Watch 2–3 intro videos to get the big picture
        2. 📝 Take notes on the key terms and concepts
        3. ✍️ Try a small hands-on exercise the same day
        4. 📅 Dedicate {hrs}h/day consistently — that's all it takes!
        5. 🔁 Review after 2 days — spaced repetition works!
        6. 🤝 Join a community (Reddit, Telegram, Discord) for your topic

        📺 I'm showing you YouTube playlists below for **{query}**!
        """).strip()

    # ── Fully generic fallback ────────────────────────────────────────────────
    goal_note = f" on your way to **{goal}**" if ctx['goal'] else ""
    return textwrap.dedent(f"""
    ✨ **Great question about "{query}"!**{goal_note}

    **Here's a structured approach:**
    1. 🔍 **Research first** — Google + YouTube for an overview
    2. 🎬 **Watch 2–3 tutorials** — visual learning is fastest
    3. ✍️ **Practice within 24h** — apply what you learned immediately
    4. 🔁 **Repeat & review** — revisit after 2 days
    5. 🤝 **Find a community** — Reddit, Discord, or local groups
    6. 🏆 **Build something** — real projects beat passive watching

    📺 I'm attaching YouTube playlists below for **"{query}"**!
    Ask me anything else — I'm here to help! 🚀
    """).strip()


# ═══════════════════════════════════════════════════════════════════════════════
#  GEMINI CALL  — primary responder
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def _get_api_key() -> str | None:
    try:
        k = st.secrets.get("GEMINI_API_KEY")
        if k: return k.strip()
    except Exception:
        pass
    return (os.getenv("GEMINI_API_KEY") or "").strip() or None


def ask_gemini(user_msg: str, ctx: dict, history: list[dict]) -> str | None:
    api_key = _get_api_key()
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            system_instruction=build_system_prompt(ctx),
        )
        # Build Gemini-format history (skip the auto-welcome message)
        gemini_hist = []
        for m in history[1:]:   # skip index-0 (welcome)
            role = "user" if m["role"] == "user" else "model"
            gemini_hist.append({"role": role, "parts": [m["content"]]})

        chat   = model.start_chat(history=gemini_hist)
        result = chat.send_message(user_msg)
        return result.text.strip() if result and result.text else None
    except Exception as e:
        # Surface the error only in debug mode
        if os.getenv("COACH_DEBUG"):
            st.warning(f"Gemini error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
#  QUICK-ACTION SUGGESTIONS  — personalised per user
# ═══════════════════════════════════════════════════════════════════════════════

def get_quick_actions(ctx: dict) -> list[str]:
    actions = []
    if ctx["generated"]:
        if ctx["next_topic"]:
            actions.append(f"What should I learn next?")
            actions.append(f"Show me videos for {ctx['next_topic']}")
        actions.append("Show me my progress")
        actions.append("Show me my roadmap")
        if ctx["goal"]:
            actions.append(f"How do I master {ctx['goal']}?")
    else:
        if ctx["goal"]:
            actions.append(f"How do I start learning {ctx['goal']}?")
    actions.append("How do I stay motivated?")
    if ctx["domain"]:
        actions.append(f"Show me {ctx['domain']} playlists")
    actions.append("Show me payment playlists")
    return actions[:6]


# ═══════════════════════════════════════════════════════════════════════════════
#  UI
# ═══════════════════════════════════════════════════════════════════════════════

# ── Init session state ────────────────────────────────────────────────────────
if "chat_history"   not in st.session_state: st.session_state.chat_history   = []
if "last_topic"     not in st.session_state: st.session_state.last_topic     = None
if "coach_welcomed" not in st.session_state: st.session_state.coach_welcomed = False

ctx = get_user_context()

# ── Render header ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="coach-header">
  <h1>🎓 AI Coach</h1>
  <p>Your personalised guide — powered by Gemini & synced with your dashboard</p>
</div>
""", unsafe_allow_html=True)

# ── Context ribbon ────────────────────────────────────────────────────────────
if ctx["generated"]:
    pct = ctx["progress_pct"]
    bar_color = "#10b981" if pct >= 70 else ("#f59e0b" if pct >= 30 else "#6366f1")
    nxt_chip  = (f"<div class='ctx-chip'>🔜 <b>{ctx['next_topic'][:28]}</b></div>"
                 if ctx["next_topic"] else "")
    st.markdown(f"""
    <div class="ctx-bar">
      <div class="ctx-chip">👤 <b>{ctx['name']}</b></div>
      <div class="ctx-chip">🎯 <b>{ctx['goal']}</b></div>
      <div class="ctx-chip">🌐 <b>{ctx['domain']}</b></div>
      <div class="ctx-chip">🏅 <b>{ctx['skill']}</b></div>
      <div class="ctx-chip">
        ✅ <b>{pct}%</b>
        <span class="mini-bar">
          <span class="mini-bar-fill"
            style="width:{pct}%;background:{bar_color}"></span>
        </span>
      </div>
      <div class="ctx-chip">⏱ <b>{ctx['hrs']}h/day</b></div>
      {nxt_chip}
    </div>
    """, unsafe_allow_html=True)
else:
    st.info(
        "💡 **Tip:** Go to the **Dashboard**, fill your profile and generate your "
        "Learning Path — your AI Coach will become fully personalised!",
        icon="🎓",
    )

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_chat, tab_playlists, tab_tips = st.tabs(
    ["💬 Chat", "📺 Browse Playlists", "💡 Quick Tips"]
)

# ══════════════════════════════════════════════════
#  TAB 1 — CHAT
# ══════════════════════════════════════════════════
with tab_chat:

    # Auto-welcome on first load
    if not st.session_state.coach_welcomed:
        welcome = _local_answer("hi", ctx)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": welcome, "playlists": []}
        )
        st.session_state.coach_welcomed = True


    # ── Quick-action pills ────────────────────────────────────────────────────
    actions = get_quick_actions(ctx)
    if actions:
        st.caption("💡 **Quick actions — click to ask instantly:**")
        btn_cols = st.columns(min(len(actions), 3))
        for i, action in enumerate(actions):
            with btn_cols[i % 3]:
                if st.button(action, key=f"qa_{i}", use_container_width=True):
                    ctx = get_user_context()
                    st.session_state.chat_history.append(
                        {"role": "user", "content": action}
                    )
                    with st.spinner("🤔 Thinking…"):
                        reply = (ask_gemini(action, ctx, st.session_state.chat_history)
                                 or _local_answer(action, ctx))
                        pls   = resolve_playlists(action, ctx)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": reply, "playlists": pls}
                    )
                    st.rerun()

    st.divider()

    # ── Chat history ──────────────────────────────────────────────────────────
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🎓"):
                st.markdown(msg["content"])
                pls = msg.get("playlists", [])
                if pls:
                    st.divider()
                    st.markdown("**📺 Recommended YouTube Resources:**")
                    for pl_name, pl_data in pls:
                        with st.expander(
                            f"{pl_data['emoji']} {pl_name}", expanded=True
                        ):
                            pl_cols = st.columns(2)
                            for idx, (title, link) in enumerate(pl_data["items"]):
                                with pl_cols[idx % 2]:
                                    st.markdown(f"[▶️ {title}]({link})")


    # ── Chat input + Clear button (bottom row) ────────────────────────────────
    _, clear_col = st.columns([8, 2])
    with clear_col:
        if st.button("🔄 Clear Chat", use_container_width=True, key="clear_bottom"):
            st.session_state.chat_history   = []
            st.session_state.coach_welcomed = False
            st.session_state.last_topic     = None
            st.rerun()

    user_msg = st.chat_input(
        "💬 Ask me anything — your coach is personalised for you…"
    )
    if user_msg:
        ctx = get_user_context()
        st.session_state.chat_history.append({"role": "user", "content": user_msg})
        with st.spinner("🤔 Thinking…"):
            reply = (ask_gemini(user_msg, ctx, st.session_state.chat_history)
                     or _local_answer(user_msg, ctx))
            pls   = resolve_playlists(user_msg, ctx)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply, "playlists": pls}
        )
        st.rerun()


# ══════════════════════════════════════════════════
#  TAB 2 — BROWSE PLAYLISTS
# ══════════════════════════════════════════════════
with tab_playlists:
    st.subheader("📺 Playlists — personalised for you")

    # ── Roadmap next-topic playlist ───────────────────────────────────────────
    if ctx["generated"] and ctx["next_topic"]:
        nxt = ctx["next_topic"]
        st.success(f"🔜 **Your next roadmap topic:** *{nxt}*")
        nxt_pl = _dynamic_playlist(nxt)
        with st.expander(f"🗺️ {nxt} — Videos", expanded=True):
            c1, c2 = st.columns(2)
            for i, (t, l) in enumerate(nxt_pl["items"]):
                with (c1 if i % 2 == 0 else c2):
                    st.markdown(f"[▶️ {t}]({l})")
        st.divider()

    # ── Domain-recommended playlist ───────────────────────────────────────────
    domain_pl_name = DOMAIN_PLAYLIST.get(ctx["domain"], "")
    if domain_pl_name and domain_pl_name in PLAYLISTS:
        goal_text = ctx["goal"] or ctx["domain"]
        st.info(f"⭐ **Recommended for your goal: *{goal_text}***")
        dp = PLAYLISTS[domain_pl_name]
        with st.expander(f"{dp['emoji']} {domain_pl_name} ⭐", expanded=True):
            c1, c2 = st.columns(2)
            for i, (t, l) in enumerate(dp["items"]):
                with (c1 if i % 2 == 0 else c2):
                    st.markdown(f"[▶️ {t}]({l})")
        st.divider()

    # ── All playlists ─────────────────────────────────────────────────────────
    st.subheader("📚 All Playlists:")
    for name, data in PLAYLISTS.items():
        with st.expander(f"{data['emoji']} {name}", expanded=False):
            c1, c2 = st.columns(2)
            for i, (t, l) in enumerate(data["items"]):
                with (c1 if i % 2 == 0 else c2):
                    st.markdown(f"[▶️ {t}]({l})")


# ══════════════════════════════════════════════════
#  TAB 3 — QUICK TIPS
# ══════════════════════════════════════════════════
with tab_tips:
    st.subheader("💡 Quick Tips")

    if ctx["generated"]:
        nxt  = ctx["next_topic"] or "your next topic"
        pct  = ctx["progress_pct"]
        goal = ctx["goal"]
        st.success(
            f"🎯 **Personalised tip for {ctx['name']}:** "
            f"You're **{pct}% done** toward *{goal}*! "
            f"Study **{ctx['hrs']}h/day** and focus on **{nxt}** next. "
            + ("🔥 More than halfway there!" if pct >= 50 else "💪 Stay consistent — every topic builds on the last!")
        )
        st.divider()

    tips = [
        ("🏃 Fitness",       "Start with 10-15 minutes of exercise daily and gradually increase"),
        ("📖 Learning",      "Dedicate 30 focused minutes daily — consistency beats marathon sessions"),
        ("🧘 Mental Health", "Practice 5 minutes of meditation or deep breathing every morning"),
        ("🎨 Creativity",    "Spend 20 mins daily on a hobby that brings you joy"),
        ("🎯 Goal Setting",  "Break big goals into weekly milestones and celebrate each one"),
        ("💤 Sleep",         "Maintain a consistent 7-9h sleep schedule — it improves memory"),
        ("💰 Finance",       "Save at least 20% of income; invest the rest wisely over time"),
        ("🗣️ Communication","Practice speaking your target skill out loud for 15 mins daily"),
    ]
    c1, c2 = st.columns(2)
    for i, (title, tip) in enumerate(tips):
        with (c1 if i % 2 == 0 else c2):
            st.info(f"**{title}**\n{tip}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
api_status = "🟢 Gemini AI Active" if _get_api_key() else "🟡 Local Engine (add GEMINI_API_KEY for smarter replies)"
st.markdown(
    f'<p style="text-align:center;color:#94a3b8;font-size:.78rem;">'
    f'✨ AI Coach synced with your dashboard · {api_status}</p>',
    unsafe_allow_html=True,
)


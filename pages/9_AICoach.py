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
import google.generativeai as genai
import random

st.set_page_config(
    page_title="LearnPath AI — AI Coach",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── INJECT CSS ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background: #f0fdf9 !important;
}
.stApp { background: #f0fdf9 !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #042f2e 0%, #134e4a 100%) !important;
    min-width: 240px !important;
}
[data-testid="stSidebar"] * { color: #99f6e4 !important; }
[data-testid="stSidebarContent"] { padding: 1rem 0.8rem !important; }

/* Main */
.block-container { padding: 2rem 2.5rem !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }

/* Cards */
.card {
    background: white; border: 1.5px solid #ccfbf1;
    border-radius: 20px; padding: 24px;
    box-shadow: 0 2px 16px rgba(13,148,136,.08); margin-bottom: 16px;
}
.card-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.1rem; font-weight: 700; color: #134e4a; margin-bottom: 4px;
}
.card-sub { font-size: .78rem; color: #6b7280; margin-bottom: 14px; }

/* Hero */
.hero-header {
    background: linear-gradient(135deg, #0d9488 0%, #059669 50%, #10b981 100%);
    border-radius: 22px; padding: 30px 36px; margin-bottom: 22px;
    box-shadow: 0 10px 40px rgba(13,148,136,0.35);
    position: relative; overflow: hidden;
}
.hero-header::before {
    content: ''; position: absolute; top: -50px; right: -50px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,0.07); border-radius: 50%;
}
.hero-header::after {
    content: ''; position: absolute; bottom: -30px; right: 100px;
    width: 120px; height: 120px;
    background: rgba(255,255,255,0.05); border-radius: 50%;
}
.hero-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2.1rem; font-weight: 800; color: white; margin-bottom: 6px;
}
.hero-sub { font-size: .9rem; color: rgba(255,255,255,0.85); }
.hero-badges { display: flex; gap: 10px; margin-top: 16px; flex-wrap: wrap; }
.hero-badge {
    background: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.35);
    color: white; border-radius: 20px; padding: 5px 16px;
    font-size: .76rem; font-weight: 700; backdrop-filter: blur(4px);
    letter-spacing: .3px;
}

/* Chat Bubbles */
.chat-bubble-wrap-user {
    display: flex; justify-content: flex-end; align-items: flex-end;
    gap: 8px; margin: 12px 0;
}
.chat-bubble-wrap-ai {
    display: flex; justify-content: flex-start; align-items: flex-end;
    gap: 8px; margin: 12px 0;
}
.avatar {
    width: 34px; height: 34px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.05rem; flex-shrink: 0;
}
.avatar-ai { background: linear-gradient(135deg, #0d9488, #059669); }
.avatar-user { background: linear-gradient(135deg, #f59e0b, #d97706); }
.bubble-user {
    background: linear-gradient(135deg, #0d9488, #059669);
    color: white; padding: 13px 20px; border-radius: 20px 20px 4px 20px;
    max-width: 72%; font-size: .88rem; line-height: 1.65;
    box-shadow: 0 4px 16px rgba(13,148,136,0.3);
}
.bubble-ai {
    background: white; color: #1e293b;
    border: 1.5px solid #ccfbf1;
    padding: 13px 20px; border-radius: 20px 20px 20px 4px;
    max-width: 80%; font-size: .88rem; line-height: 1.65;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

/* Chat Wrap */
.chat-wrap {
    background: #f0fdf9;
    border: 1.5px solid #ccfbf1;
    border-radius: 18px; padding: 16px;
    max-height: 420px;
    overflow-y: auto; margin-bottom: 14px;
    scroll-behavior: smooth;
}

/* Typing cursor & input */
.stTextInput > div > div > input {
    background: white !important;
    border: 2px solid #ccfbf1 !important;
    border-radius: 14px !important;
    color: #134e4a !important;
    font-size: .92rem !important;
    padding: 14px 18px !important;
    caret-color: #0d9488 !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input::placeholder { color: #9ca3af !important; }
.stTextInput > div > div > input:focus {
    border-color: #0d9488 !important;
    box-shadow: 0 0 0 4px rgba(13,148,136,0.12) !important;
    outline: none !important;
}

/* Send Button */
[data-testid="stButton"] button[kind="secondary"],
.stButton > button {
    background: linear-gradient(135deg, #0d9488, #059669) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; font-weight: 700 !important;
    font-size: .95rem !important; padding: 0.65rem 1.5rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all .2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(13,148,136,0.38) !important;
}

/* Clear button — red danger style */
.clear-btn > div > button, .clear-btn button {
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    box-shadow: none !important;
}
.clear-btn button:hover {
    box-shadow: 0 6px 18px rgba(239,68,68,0.35) !important;
}

/* Tips & Recommendations */
.rec-box {
    background: white; border-left: 4px solid #0d9488;
    border-radius: 10px; padding: 14px; margin: 8px 0;
    font-size: .83rem; color: #1e293b;
    box-shadow: 0 1px 6px rgba(13,148,136,.06);
}
.onboard-box {
    background: linear-gradient(135deg, #d1fae5, #a7f3d0);
    border: 1.5px solid #6ee7b7; border-radius: 14px;
    padding: 20px; margin-bottom: 20px;
}
.onboard-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.15rem; font-weight: 700; color: #064e3b; margin-bottom: 6px;
}
.onboard-desc { font-size: .86rem; color: #065f46; }

</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ───────────────────────────────────────────
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
    Generate personalized AI Coach responses using Google Gemini API.
    Falls back to comprehensive mock logic if no API key is provided.
    """
    if api_key:
        try:
            genai.configure(api_key=api_key)
            
            system_instruction = f"""
You are a friendly, enthusiastic, and highly encouraging AI Learning Coach. 
You are talking to {name}, who is currently at a {skill_level} skill level. 
Their main learning goal is: {goal}.

**YOUR JOB: ANSWER ANY QUESTION WITH FULL ABILITY**

You can answer questions about:
✅ Learning tips and study strategies
✅ Health, fitness, nutrition, and wellness advice
✅ Sleep habits, productivity, and time management
✅ Motivation and personal development
✅ Career and professional advice
✅ Mental health and stress management
✅ Gardening, cooking, music, and hobbies
✅ Technical questions related to their learning goal
✅ YouTube playlists and learning resources
✅ ANY question they ask with practical, helpful answers

**FOR PLAYLIST REQUESTS:**
When asked for playlists, videos, courses, or YouTube recommendations:
1. Provide ONLY YouTube links (no Udemy, Coursera, etc.)
2. Give 4-5 specific recommendations with direct URLs
3. Use format: • 🎬 **Name** - https://...

**FOR ALL OTHER QUESTIONS:**
1. Answer directly and comprehensively
2. Provide practical advice and actionable tips
3. Be encouraging and supportive
4. Format with emojis, bullet points, and bold text
5. Keep responses engaging but concise
6. Suggest playlists if relevant to their question

**TONE & STYLE:**
- Be very friendly, warm, and encouraging
- Use emojis liberally (🎯 🚀 💪 ✨ etc.)
- Make content actionable and practical
- Show enthusiasm and positivity
- Praise their efforts and dedication
- Ask follow-up questions if helpful

You are an expert in learning, health, productivity, and personal growth!
"""
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_instruction
            )
            
            # Build chat history for context
            history_str = ""
            for msg in st.session_state.chat_history[:-1]: 
                role = "Coach" if msg["role"] == "ai" else "User"
                history_str += f"{role}: {msg['content']}\n"
                
            prompt = f"Previous Chat History:\n{history_str}\n\nUser: {user_message}\nCoach:"
            
            response = model.generate_content(prompt)
            return response.text
            
        except Exception:
            pass # Fall through to basic logic

    # ── FALLBACK MOCK LOGIC ────────────────────────────
    msg_lower = user_message.lower()
    
    if any(word in msg_lower for word in ["hi", "hello", "hey", "hlo", "helo", "start", "begin", "sup", "yo"]):
        greetings = [
            f"🔥 YOOOO {name}!! You just made my day by showing up! Let's turn your goal of **'{goal}'** into REALITY! What are we crushing today? 🚀💪",
            f"⚡ {name}! You absolute LEGEND! Every single day you show up is another day closer to mastering **'{goal}'**! The grind is REAL and so are YOU! What can I help you with? 🌟",
            f"🎉 HEYYY {name}!! Welcome back, champion! People who show up like you are exactly the ones who WIN! Ready to level up your **{skill_level}** skills? Let's GO! 🎯",
            f"🥳 OH WOW, {name} is in the house!! Your commitment to **'{goal}'** is honestly INSPIRING! Let's make today count — what's on your mind? 💬",
            f"💫 {name}! I've been waiting for you! Champions don't wait for motivation, they CREATE it — and here you are! Let's talk about your **'{goal}'** journey! 🚀",
            f"🌞 RISE AND THRIVE, {name}! You picked **'{goal}'** as your mission and that's already HALF the battle won! Ask me anything — let's build something AMAZING today! 💪",
            f"💪 {name}!! Every expert was once a beginner, and every beginner who keeps showing up becomes an EXPERT — that's YOU right now! What shall we conquer today? 🔥",
            f"🤩 Oh my GOODNESS, {name}!! You're here and that alone puts you ahead of 90% of people! Your goal of **'{goal}'** is waiting for you — let's chase it! 🎯",
            f"🏆 {name}, you ABSOLUTE ROCKSTAR!! Showing up consistently is the #1 habit of successful people, and HERE YOU ARE! Tell me what's on your mind! 🤖",
            f"🚀 BLAST OFF, {name}! Another day, another step closer to **'{goal}'**! The version of you six months from now will THANK you for today! What do you need? ⚡",
        ]
        return random.choice(greetings)
    
    if any(word in msg_lower for word in ["motiv", "encourage", "inspire", "boost", "confidence"]):
        completed = len(user_data.get("completed", []))
        return f"You're absolutely killing it, {name}! 💪 You've already completed **{completed} topics** — that shows real commitment and discipline! Remember:\n\n• Progress over perfection 🎯\n• Every small step counts ✨\n• Consistency beats intensity every time!\n\nKeep that momentum going! 🚀"
    
    # ────────────────────────────────────────────────────────────
    # CHECK COMPREHENSIVE QUESTIONS FIRST (BEFORE GENERIC ONES!)
    # ────────────────────────────────────────────────────────────
    
    # Check for sleep/tiredness questions (MUST BE BEFORE "WHEN" CHECK!)
    if any(word in msg_lower for word in ["sleep", "sleepy", "tired", "energy", "fatigue", "rest", "insomnia", "awake", "fatigue"]):
        return f"""🌙 **EXCELLENT QUESTION, {name}!** Here's my advice for sleep & energy:

**IMMEDIATE SOLUTIONS:**
• ⏰ Keep a consistent sleep schedule (sleep & wake same time daily)
• 📵 No screens 30mins before bed (blue light ruins sleep)
• 🏃 Exercise in morning/afternoon (NOT before bed!)
• ☕ Cut caffeine after 2 PM
• 🛏️ Make bedroom cool, dark, and quiet

**DURING LOW-ENERGY TIMES:**
• 💪 Do 5-10 min stretching/exercise to boost alertness
• 🚶 Take a 10-min walk in sunlight
• 💧 Drink water (dehydration causes fatigue!)
• 🥗 Eat protein-rich snack (banana, yogurt, nuts)

**FOR YOUR {skill_level.upper()} LEVEL:**
• Study during HIGH-energy hours (usually morning)
• Take 5-min breaks every 25mins (Pomodoro method!)
• Mix subjects to keep brain engaged

You've got this! 🚀 Sleep is crucial for learning! 💤✨"""
    
    # Check for focus/distraction questions
    if any(word in msg_lower for word in ["focus", "distraction", "concentrate", "attention", "overwhelm"]):
        return f"""🎯 **FOCUS HACK FOR {name}!** Here's how to crush it:

**THE 4-STEP FOCUS FORMULA:**
1. 🚫 Remove ALL distractions (phone, notifications, tabs)
2. ⏱️ Use Pomodoro: 25min focus + 5min break
3. 🎧 Try lo-fi/ambient background music
4. 📊 Track your progress (motivates you!)

**WHEN OVERWHELMED:**
• ✏️ Write down EVERYTHING
• 🎯 Pick just ONE thing to focus on
• 🔢 Break it into micro-tasks (smaller = less scary!)
• 🚀 Start with 10 minutes only

**FOR YOUR GOAL: {goal}**
• Focus on ONE concept at a time
• Don't compare to others (your journey is unique!)
• Celebrate small wins

Pro tip: Your brain learns best with focused attention! 🧠⚡"""
    
    # Check for health/wellness questions
    if any(word in msg_lower for word in ["health", "pain", "exercise", "diet", "wellness", "body", "strength", "weight", "fitness"]):
        return f"""💪 **WELLNESS ADVICE FOR {name}!** Let's help:

**EXERCISE TIPS:**
• 🏃 Start small (10-15 min daily)
• ✅ Consistency > intensity
• 🧘 Mix cardio + strength + flexibility
• 📱 Try YouTube workout channels (free!)

**NUTRITION BASICS:**
• 🥗 Eat real food (vegetables, protein, whole grains)
• 💧 Drink 2-3L water daily
• ⚖️ 80/20 rule (healthy 80% of time, treats 20%)
• 🍎 Fuel your brain during study!

**MENTAL WELLNESS:**
• 🧘 Meditation (5 mins daily helps!)
• 🌳 Time in nature (amazing for mood)
• 😴 Sleep is NON-NEGOTIABLE
• 🤝 Connect with people

**LEARNING + HEALTH:**
• Study in morning when body is fresh
• Move frequently during study sessions
• Eat brain food (nuts, berries, dark chocolate!)

You're investing in your HEALTH AND YOUR MIND! 🎯💚"""
    
    # Check for goal/direction questions
    if any(word in msg_lower for word in ["goal", "direction", "path", "career", "future", "what should i", "plan", "strategy"]):
        return f"""🎯 **LET'S MAP YOUR FUTURE, {name}!** Here's what I think:

**YOUR CURRENT GOAL: {goal}**
**Your Skill Level: {skill_level}**
**Daily Commitment: {st.session_state.get("hrs", 1.5)}h**

**NEXT 30 DAYS:**
📌 Master ONE core concept
📌 Build a small project/practice
📌 Join a community in your field
📌 Track your progress

**YOUR PATH:**
1️⃣ Get BASICS solid (current phase!)
2️⃣ Build something real (apply learning)
3️⃣ Help others (teach = learn!)
4️⃣ Specialize deeper (advanced topics)

**SUCCESS FACTORS:**
✅ Consistency (15 min daily > 2hr once/week!)
✅ Practice (not just watching!)
✅ Community (find your tribe!)
✅ Patience (mastery takes time!)

You're already on the right path by asking questions! 🚀🌟"""
    
    # Check for payment/finance/transaction questions
    if any(word in msg_lower for word in ["payment", "paytm", "gpay", "phonepe", "transaction", "pay", "bill", "money", "transfer", "upi", "wallet", "bank", "card"]):
        return f"""💳 **PAYMENT & TRANSACTION GUIDE FOR {name}!** Let me help:

**POPULAR PAYMENT METHODS IN INDIA:**

🏦 **UPI (Unified Payments Interface):**
• Google Pay, PhonePe, BHIM, Paytm, WhatsApp Pay
• Transfer directly using phone number or UPI ID
• Quick, safe, and FREE
• Works on all smartphones

📱 **Paytm Specifically:**
• Download Paytm app or use website
• Link your bank account or add money
• Send money to other Paytm users (instant!)
• Pay bills, recharge, shop online
• Very reliable and widely accepted

🔐 **PAYMENT SAFETY TIPS:**
• ✅ NEVER share OTP (One Time Password)
• ✅ NEVER share credit card details via link/email
• ✅ Only use official payment apps
• ✅ Check HTTPS security before entering bank details
• ✅ Turn ON 2-Factor Authentication always

💰 **COMMON PAYMENT OPTIONS:**
• **Direct Bank Transfer**: Traditional but slower
• **Credit/Debit Card**: Fast online transactions
• **Digital Wallets**: Google Pay, PhonePe, Paytm
• **NEFT/RTGS**: For large amounts (takes time)

**FOR YOUR PAYTM QUESTION:**
1. Open Paytm app
2. Tap "Send Money"
3. Enter recipient's phone number or Paytm ID
4. Enter amount
5. Verify and confirm
6. Done! Instant transfer! ✅

Need help with a specific payment method? Just ask! 🚀💪"""
    
    if any(word in msg_lower for word in ["tip", "suggest", "recommend", "advice", "help", "how"]):
        # When asking for help/tips/advice, suggest playlists from their goal or all playlists
        youtube_playlists = {
            "health": [
                "🏃 **7-Minute Workout** - https://www.youtube.com/playlist?list=PLz6sWmhA_TqDEUGGqN_tVZt0w0Lpc5r-O",
                "💪 **Complete Fitness Training** - https://www.youtube.com/playlist?list=PLz6sWmhA_TqDEUGGqN_tVZt0w0Lpc5r-O",
                "🧘 **Yoga for Beginners** - https://www.youtube.com/playlist?list=PLui6Eyny-UzwxZeUzhGk-A440ir4WN5Ry",
                "❤️ **Health Tips & Wellness** - https://www.youtube.com/results?search_query=health+wellness+full+course",
            ],
            "gardening": [
                "🌱 **Complete Gardening Guide** - https://www.youtube.com/playlist?list=PLB1C7E27C4D1E15F5",
                "🌿 **Urban Gardening** - https://www.youtube.com/playlist?list=PL9C3E0A05FDEDC2D0",
                "🥕 **Vegetable Gardening** - https://www.youtube.com/playlist?list=PLgJlrKCJR8YawdX9K2G8h3DfEhJOlGdBC",
                "🌻 **Indoor Plants Care** - https://www.youtube.com/results?search_query=indoor+plants+gardening+tutorial",
            ],
            "python": [
                "💻 **Complete Python Course** - https://www.youtube.com/playlist?list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU",
                "🐍 **Python for Beginners** - https://www.youtube.com/watch?v=rfscVS0vtik",
                "🎯 **Python Data Science** - https://www.youtube.com/results?search_query=python+data+science+complete+course",
                "🔧 **Python Projects** - https://www.youtube.com/results?search_query=python+projects+tutorial",
            ],
        }
        
        # Check if their goal matches any category
        goal_lower = goal.lower()
        response = f"🎬 **PERFECT, {name}!** 🌟 Here are some GREAT resources for you:\n\n"
        found_match = False
        
        for keyword in youtube_playlists.keys():
            if keyword in goal_lower or keyword in msg_lower:
                response += f"**📺 {keyword.upper()} PLAYLISTS:\n\n**"
                for playlist in youtube_playlists[keyword]:
                    response += f"{playlist}\n"
                response += "\n✨ **Great study materials!** Click and start learning! 🚀"
                found_match = True
                break
        
        if not found_match:
            # If no match, show all available playlists
            response += "**📺 Here are ALL our playlists to choose from:\n\n**"
            for category, playlists in youtube_playlists.items():
                response += f"**{category.upper()}:**\n"
                for playlist in playlists:
                    response += f"{playlist}\n"
                response += "\n"
            response += "✨ **Pick what interests you and start TODAY!** 🚀💪"
        
        return response
    
    if any(word in msg_lower for word in ["playlist", "video", "course", "youtube", "resource"]):
        # YouTube only playlists for specific topics
        youtube_playlists = {
            # Health & Fitness
            "health": [
                "🏃 **7-Minute Workout** - https://www.youtube.com/playlist?list=PLz6sWmhA_TqDEUGGqN_tVZt0w0Lpc5r-O",
                "💪 **Complete Fitness Training** - https://www.youtube.com/playlist?list=PLz6sWmhA_TqDEUGGqN_tVZt0w0Lpc5r-O",
                "🧘 **Yoga for Beginners** - https://www.youtube.com/playlist?list=PLui6Eyny-UzwxZeUzhGk-A440ir4WN5Ry",
                "❤️ **Health Tips & Wellness** - https://www.youtube.com/results?search_query=health+wellness+full+course",
            ],
            "fitness": [
                "🏋️ **Strength Training** - https://www.youtube.com/playlist?list=PLgJlrKCJR8YZzcBcHIcM3F_RGE-rRVFKr",
                "🤸 **HIIT Workouts** - https://www.youtube.com/playlist?list=PLgJlrKCJR8YawdX9K2G8h3DfEhJOlGdBC",
                "🧘 **Full Body Fitness** - https://www.youtube.com/results?search_query=full+body+workout+complete+course",
                "💪 **Home Workouts** - https://www.youtube.com/results?search_query=home+workout+routine+beginner",
            ],
            "nutrition": [
                "🥗 **Healthy Eating Habits** - https://www.youtube.com/playlist?list=PLZ0d9rVSo90cWJCfS4yf9vSgGzNwlLMmK",
                "🍎 **Nutrition Guide** - https://www.youtube.com/results?search_query=nutrition+guide+complete+course",
                "🥤 **Meal Prep & Planning** - https://www.youtube.com/results?search_query=meal+prep+planning+tutorial",
                "🥙 **Healthy Recipes** - https://www.youtube.com/results?search_query=healthy+recipes+cooking+full+course",
            ],
            "mental wellness": [
                "🧘 **Mindfulness & Meditation** - https://www.youtube.com/playlist?list=PLZjMM19sNY82ADvkgNuWkkqmQkQC8-Vgv",
                "💫 **Stress Management** - https://www.youtube.com/results?search_query=stress+management+techniques+tutorial",
                "🧠 **Mental Health Tips** - https://www.youtube.com/results?search_query=mental+health+wellness+course",
                "😌 **Anxiety Relief** - https://www.youtube.com/results?search_query=anxiety+relief+meditation+playlist",
            ],
            
            # Gardening
            "gardening": [
                "🌱 **Complete Gardening Guide** - https://www.youtube.com/playlist?list=PLB1C7E27C4D1E15F5",
                "🌿 **Urban Gardening** - https://www.youtube.com/playlist?list=PL9C3E0A05FDEDC2D0",
                "🥕 **Vegetable Gardening** - https://www.youtube.com/playlist?list=PLgJlrKCJR8YawdX9K2G8h3DfEhJOlGdBC",
                "🌻 **Indoor Plants Care** - https://www.youtube.com/results?search_query=indoor+plants+gardening+tutorial",
            ],
            "farming": [
                "🌾 **Organic Farming Guide** - https://www.youtube.com/playlist?list=PLVzND6S6bDXJ4KrZcEV6xJ4F1b-Z8c0Q2",
                "🌱 **Home Farming** - https://www.youtube.com/playlist?list=PLZ3BXgsvEQSjhVa6M5bhVjqVKNl4h_1w0",
                "🥬 **Sustainable Gardening** - https://www.youtube.com/results?search_query=sustainable+gardening+complete+guide",
                "🌳 **Terrace Gardening** - https://www.youtube.com/results?search_query=terrace+gardening+tutorial+full+course",
            ],
            
            # Education & Skills
            "programming": [
                "💻 **Complete Python Course** - https://www.youtube.com/playlist?list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU",
                "🐍 **Python for Beginners** - https://www.youtube.com/watch?v=rfscVS0vtik",
                "⌨️ **Web Development** - https://www.youtube.com/playlist?list=PLillGF-RfqbYeckUaLj3f_LSIuuJPQ05c",
                "🚀 **JavaScript Tutorial** - https://www.youtube.com/results?search_query=javascript+complete+course+beginners",
            ],
            "python": [
                "💻 **Complete Python Course** - https://www.youtube.com/playlist?list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU",
                "🐍 **Python for Beginners** - https://www.youtube.com/watch?v=rfscVS0vtik",
                "🎯 **Python Data Science** - https://www.youtube.com/results?search_query=python+data+science+complete+course",
                "🔧 **Python Projects** - https://www.youtube.com/results?search_query=python+projects+tutorial",
            ],
            "data science": [
                "📊 **Data Science 101** - https://www.youtube.com/playlist?list=PLvKTlZyNTAQQyqnM1kkXEpzaPnMvYe8oZ",
                "🤖 **Machine Learning** - https://www.youtube.com/results?search_query=machine+learning+complete+course+beginner",
                "📈 **Data Analysis** - https://www.youtube.com/results?search_query=data+analysis+tutorial+complete",
                "🐼 **Pandas Tutorial** - https://www.youtube.com/results?search_query=pandas+python+data+analysis+full+course",
            ],
            "language": [
                "🌍 **English Speaking** - https://www.youtube.com/playlist?list=PLKAJfWzMyVMrWmw6s_H2D3h6t19DXjPHa",
                "📚 **Spoken English** - https://www.youtube.com/playlist?list=PL7zKLbKi1yV30kWv0qJLOPw8EsvCYVmR-",
                "🗣️ **Communication Skills** - https://www.youtube.com/results?search_query=communication+skills+tutorial+complete",
                "👂 **Listening Practice** - https://www.youtube.com/results?search_query=english+listening+practice+course",
            ],
            "business": [
                "💼 **Entrepreneurship 101** - https://www.youtube.com/playlist?list=PLKAJfWzMyVMqY37RYjNlBq0wMHVQk1lqH",
                "📊 **Digital Marketing** - https://www.youtube.com/results?search_query=digital+marketing+complete+course",
                "💰 **Personal Finance** - https://www.youtube.com/results?search_query=personal+finance+money+management+tutorial",
                "🎯 **Sales Skills** - https://www.youtube.com/results?search_query=sales+skills+training+course",
            ],
            "design": [
                "🎨 **Graphic Design** - https://www.youtube.com/results?search_query=graphic+design+tutorial+complete",
                "✏️ **UI/UX Design** - https://www.youtube.com/results?search_query=ui+ux+design+course+beginner",
                "🖼️ **Photo Editing** - https://www.youtube.com/results?search_query=photo+editing+tutorial+complete",
                "🎬 **Video Editing** - https://www.youtube.com/results?search_query=video+editing+tutorial+full+course",
            ],
        }
        
        # Extract topic from user message
        topic_found = None
        for keyword in youtube_playlists.keys():
            if keyword in msg_lower:
                topic_found = keyword
                break
        
        # If specific topic found, show those playlists; otherwise show all
        if topic_found:
            response = f"🎬 **AWESOME, {name}!** 🌟 Here are the BEST YouTube playlists for **{topic_found.upper()}**:\n\n"
            response += f"**📺 {topic_found.upper()} PLAYLISTS:**\n"
            for playlist in youtube_playlists[topic_found]:
                response += f"{playlist}\n"
            response += "\n✨ **Click any playlist to start learning NOW!** 🚀💪"
        else:
            # If unknown topic, try to extract it and generate YouTube search links
            words = msg_lower.split()
            requested_topic = None
            
            # Find the topic (words after "playlist", "video", "course", etc.)
            request_words = ["playlist", "video", "course", "youtube", "resource"]
            for i, word in enumerate(words):
                if word in request_words:
                    if i + 1 < len(words):
                        requested_topic = " ".join(words[i+1:i+4])  # Get next 3 words as topic
                    break
            
            if requested_topic and requested_topic.strip():
                # Generate dynamic playlist suggestions for any topic
                topic_clean = requested_topic.replace("playlist", "").replace("video", "").replace("course", "").strip()
                topic_url = topic_clean.replace(" ", "+")
                
                response = f"🎬 **FANTASTIC, {name}!** 🌟 Here are YouTube playlists for **{topic_clean.upper()}**:\n\n"
                response += f"**📺 {topic_clean.upper()} SEARCH RESULTS:**\n"
                response += f"▶️ **Full Courses** - https://www.youtube.com/results?search_query={topic_url}+full+course\n"
                response += f"🎓 **Beginner Tutorials** - https://www.youtube.com/results?search_query={topic_url}+for+beginners\n"
                response += f"📚 **Complete Guide** - https://www.youtube.com/results?search_query={topic_url}+complete+guide+tutorial\n"
                response += f"🚀 **Advanced Topics** - https://www.youtube.com/results?search_query={topic_url}+advanced+tutorial\n"
                response += f"\n✨ **Click the links and pick any playlist!** 🚀💪"
            else:
                # Show ALL playlists as fallback
                response = f"🎬 **AWESOME, {name}!** 🌟 Here are ALL the YouTube playlists available:\n\n"
                for category, playlists in youtube_playlists.items():
                    response += f"**📺 {category.upper()}:**\n"
                    for playlist in playlists:
                        response += f"{playlist}\n"
                    response += "\n"
                response += "✨ **Pick ANY category that interests you!** Click the links and start learning TODAY! 🚀💪"
        
        return response
    
    if any(word in msg_lower for word in ["schedule", "plan", "time", "how long", "when", "week"]):
        hours = st.session_state.get("hrs", 1.5)
        return f"Great timing question! Here's your personalized study plan, {name}:\n\n📅 **Daily**: {hours}h of focused learning\n✅ Consistency > intensity\n⏰ Study when you're most alert\n🔄 Mix theory with hands-on practice\n\nPick a fixed time each day and stick to it! You've got this! 🔥"
    
    # ────────────────────────────────────────────────────────────
    # FALLBACK: USE GEMINI AI TO ANSWER + ALWAYS PROVIDE PLAYLISTS
    # ────────────────────────────────────────────────────────────
    if api_key:
        try:
            genai.configure(api_key=api_key)
            
            comprehensive_system_instruction = f"""You are {name}'s personal AI Coach. Give expert answers to any question."""
            
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=comprehensive_system_instruction
            )
            
            # Build chat history
            history_str = ""
            for msg in st.session_state.chat_history[:-1]:
                role = "Coach" if msg["role"] == "ai" else "User"
                history_str += f"{role}: {msg['content']}\n"
            
            prompt = f"""User asks: {user_message}

Please answer this question comprehensively and helpfully. Keep it concise."""
            
            response = model.generate_content(prompt)
            ai_response = response.text
            
            # ═══════════════════════════════════════════════════════════
            # ALWAYS ADD YOUTUBE PLAYLISTS - NO MATTER WHAT!
            # ═══════════════════════════════════════════════════════════
            
            # Extract topic keywords from user message
            msg_clean = user_message.lower().replace("?", "").replace("!", "")
            
            # Remove common words
            stopwords = ["how", "what", "when", "where", "why", "can", "i", "you", "the", "is", "do", "to", "a", "an", "and", "or", "am"]
            topic_words = [w for w in msg_clean.split() if len(w) > 3 and w not in stopwords]
            
            if not topic_words:
                topic_words = msg_clean.split()[-3:]
            
            # Create search query
            topic = "+".join(topic_words[:2]) if topic_words else "tutorial"
            
            # ALWAYS ADD PLAYLISTS
            ai_response += f"\n\n**📺 YOUTUBE LEARNING RESOURCES FOR THIS TOPIC:**\n"
            ai_response += f"🎬 **Complete Tutorial** - https://www.youtube.com/results?search_query={topic}+tutorial+full+course\n"
            ai_response += f"🎬 **For Beginners** - https://www.youtube.com/results?search_query={topic}+for+beginners\n"
            ai_response += f"🎬 **Complete Guide** - https://www.youtube.com/results?search_query={topic}+complete+guide+step+by+step\n"
            ai_response += f"🎬 **Advanced Tips** - https://www.youtube.com/results?search_query={topic}+advanced+tips+tricks\n"
            ai_response += f"🎬 **How To** - https://www.youtube.com/results?search_query=how+to+{topic}\n"
            ai_response += f"🎬 **Live Class** - https://www.youtube.com/results?search_query={topic}+live+class+tutorial\n"
            
            return ai_response
            
        except Exception as e:
            pass  # Fall through to playlist fallback
    
    # Fallback: suggest playlists for any request
    youtube_playlists = {
        "health": [
            "🏃 **7-Minute Workout** - https://www.youtube.com/playlist?list=PLz6sWmhA_TqDEUGGqN_tVZt0w0Lpc5r-O",
            "💪 **Complete Fitness Training** - https://www.youtube.com/playlist?list=PLz6sWmhA_TqDEUGGqN_tVZt0w0Lpc5r-O",
            "🧘 **Yoga for Beginners** - https://www.youtube.com/playlist?list=PLui6Eyny-UzwxZeUzhGk-A440ir4WN5Ry",
            "❤️ **Health Tips & Wellness** - https://www.youtube.com/results?search_query=health+wellness+full+course",
        ],
        "gardening": [
            "🌱 **Complete Gardening Guide** - https://www.youtube.com/playlist?list=PLB1C7E27C4D1E15F5",
            "🌿 **Urban Gardening** - https://www.youtube.com/playlist?list=PL9C3E0A05FDEDC2D0",
            "🥕 **Vegetable Gardening** - https://www.youtube.com/playlist?list=PLgJlrKCJR8YawdX9K2G8h3DfEhJOlGdBC",
            "🌻 **Indoor Plants Care** - https://www.youtube.com/results?search_query=indoor+plants+gardening+tutorial",
        ],
        "python": [
            "💻 **Complete Python Course** - https://www.youtube.com/playlist?list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU",
            "🐍 **Python for Beginners** - https://www.youtube.com/watch?v=rfscVS0vtik",
            "🎯 **Python Data Science** - https://www.youtube.com/results?search_query=python+data+science+complete+course",
            "🔧 **Python Projects** - https://www.youtube.com/results?search_query=python+projects+tutorial",
        ],
    }
    
    # Check if goal matches any category
    goal_lower = goal.lower()
    response = f"🎬 **GREAT QUESTION, {name}!** 🌟 For your goal of **{goal}**, here are some AWESOME resources:\n\n"
    found_match = False
    
    for keyword in youtube_playlists.keys():
        if keyword in goal_lower:
            response += f"**📺 {keyword.upper()} PLAYLISTS:\n\n**"
            for playlist in youtube_playlists[keyword]:
                response += f"{playlist}\n"
            response += "\n✨ **Start with any playlist today!** 🚀"
            found_match = True
            break
    
    # ── FINAL FALLBACK: Show all available playlists ──────────────────────────
    response = f"🎬 **FANTASTIC QUESTION, {name}!** 🌟 Here are some resources I recommend:\n\n"
    response += "**📺 AWESOME PLAYLISTS TO EXPLORE:**\n\n"
    
    youtube_playlists_final = {
        "health": ["🏃 **7-Minute Workout** - https://www.youtube.com/playlist?list=PLz6sWmhA_TqDEUGGqN_tVZt0w0Lpc5r-O"],
        "gardening": ["🌱 **Complete Gardening** - https://www.youtube.com/playlist?list=PLB1C7E27C4D1E15F5"],
        "python": ["💻 **Complete Python** - https://www.youtube.com/playlist?list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU"],
    }
    
    for category, playlists in youtube_playlists_final.items():
        for playlist in playlists:
            response += f"{playlist}\n"
    
    response += f"\n✨ **Any other questions? I'm ready to help with ANYTHING!** 🚀💪"
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

# ── HERO HEADER ───────────────────────────────────────────
st.markdown(f"""
  <div style="margin-bottom:18px">
    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.7rem;font-weight:800;color:#0f172a">🤖 Your AI Coach</div>
    <div style="color:#64748b;font-size:.86rem">Get personalized guidance, tips, and recommendations for your learning journey</div>
  </div>""", unsafe_allow_html=True)

# ── FIRST-TIME ONBOARDING ────────────────────────────────────
if st.session_state.first_visit and user_goal:
    st.markdown(f"""
    <div class="onboard-box">
      <div class="onboard-title">👋 Welcome to Your AI Coach!</div>
      <div class="onboard-desc">
        I'm here to help you achieve your goal of <strong>{user_goal}</strong>. Ask me anything about your learning journey!
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.first_visit = False

# ── AI COACH TIPS & RECOMMENDATIONS ──────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">💬 Chat with your AI Coach</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-sub">Ask anything — tips, playlists, schedules, motivation! Press Enter or click Send.</div>', unsafe_allow_html=True)

    # Display chat history
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="text-align:center; padding:20px 20px 16px;">
          <div style="font-size:2.2rem; margin-bottom:8px;">🤖</div>
          <div style="font-size:.95rem; font-weight:700; color:#0d9488; margin-bottom:4px;">Hey! I'm your AI Coach!</div>
          <div style="font-size:.78rem; color:#9ca3af;">Type below and press <b>Enter</b> or click <b>Send</b> 👇</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-bubble-wrap-user">
                  <div class="bubble-user">{msg["content"]}</div>
                  <div class="avatar avatar-user">👤</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-bubble-wrap-ai">
                  <div class="avatar avatar-ai">🤖</div>
                  <div class="bubble-ai">{msg["content"]}</div>
                </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Handle pending message (sent via Enter key) ──────────────
    if st.session_state.pending_msg:
        msg_to_send = st.session_state.pending_msg
        st.session_state.pending_msg = ""
        st.session_state.chat_history.append({"role": "user", "content": msg_to_send})
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

    # Send button row + Clear button (red, separate)
    col_send, col_clear = st.columns([5, 1])
    with col_send:
        if st.button("🚀  Send Message", use_container_width=True):
            if user_input.strip():
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                ai_response = generate_coach_response(user_input, user_name, user_goal, user_skill, user_data, gemini_api_key)
                st.session_state.chat_history.append({"role": "ai", "content": ai_response})
                st.session_state.input_key += 1
                st.rerun()

    with col_clear:
        # Wrap in a div so we can target only this button for red styling
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.input_key += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── AGE-BASED PLAYLIST SUGGESTIONS ──────────────────────────
with col2:
    st.markdown('<div class="card" style="height:100%">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🎧 Playlist Suggestions by Category</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-sub">Personalized playlists for your age group & interests</div>', unsafe_allow_html=True)

    # Generate comprehensive age-group specific playlists with categories
    def get_categorized_playlists(age, goal, skill):
        """Generate age-appropriate playlists across health, gardening, and education categories."""
        
        if age < 18:  # Teens (13-17)
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
        elif age < 25:  # Young Adults (18-24)
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
        elif age < 40:  # Working Professionals (25-39)
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
        else:  # 40+ (Mature Learners)
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
          <div style="font-size:.9rem;font-weight:700;color:#134e4a;margin-bottom:10px;">{category}</div>
        </div>
        """, unsafe_allow_html=True)
        
        for pl in playlists:
            st.markdown(f"""
            <a href="{pl['url']}" target="_blank" style="text-decoration:none;display:block;margin-bottom:8px;">
              <div style="display:flex;align-items:center;gap:10px;background:white;border:1.5px solid #ccfbf1;
                          border-radius:10px;padding:12px 14px;
                          transition:all .2s;cursor:pointer;
                          box-shadow:0 1px 4px rgba(13,148,136,.07);
                          hover:box-shadow:0 4px 12px rgba(13,148,136,.15);">
                <div style="font-size:1.1rem;">{pl['icon']}</div>
                <div style="flex:1;">
                  <div style="font-size:.8rem;font-weight:700;color:#134e4a;">{pl['label']}</div>
                </div>
                <div style="color:#0d9488;font-size:.8rem;font-weight:600;">→</div>
              </div>
            </a>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

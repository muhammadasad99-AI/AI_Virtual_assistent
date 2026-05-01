import streamlit as st
from datetime import datetime
import sys
import os


sys.path.append(os.path.dirname(__file__))

from nlp_engine import process_input
from reminder import handle_set_reminder, handle_view_reminders, handle_delete_reminder
from scheduler import handle_add_schedule, handle_view_schedule, handle_delete_schedule
from database import init_db
from voice_engine import speak,listen

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Virtual Assistant",
    page_icon="🤖",
    layout="wide"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #f0f0f0;
    }

    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }

    .main-header h1 {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        font-size: 3rem;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .main-header p {
        color: #a0aec0;
        font-size: 1rem;
        font-family: 'Space Mono', monospace;
    }

    .chat-bubble-user {
        background: linear-gradient(135deg, #6d28d9, #4f46e5);
        color: white;
        padding: 0.9rem 1.2rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
        font-size: 0.95rem;
        box-shadow: 0 4px 15px rgba(109,40,217,0.3);
    }

    .chat-bubble-bot {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.1);
        color: #e2e8f0;
        padding: 0.9rem 1.2rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 0;
        max-width: 80%;
        font-size: 0.95rem;
        backdrop-filter: blur(10px);
    }

    .intent-badge {
        display: inline-block;
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-family: 'Space Mono', monospace;
        margin-bottom: 0.4rem;
    }

    .nlp-debug {
        background: rgba(0,0,0,0.3);
        border: 1px solid rgba(168,85,247,0.3);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        color: #c4b5fd;
    }

    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(167,139,250,0.4) !important;
        border-radius: 12px !important;
        color: black !important;
        font-family: 'Syne', sans-serif !important;
        padding: 0.7rem 1rem !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(124,58,237,0.5) !important;
    }

    .sidebar-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }

    div[data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.95) !important;
    }

    .metric-card {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid rgba(167,139,250,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────
init_db()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "show_nlp_debug" not in st.session_state:
    st.session_state.show_nlp_debug = False

# ─────────────────────────────────────────────
# RESPONSE HANDLER
# ─────────────────────────────────────────────
def generate_response(user_input: str) -> tuple:
    result = process_input(user_input)
    intent = result["intent"]
    entities = result["entities"]

    if intent == "set_reminder":
        response = handle_set_reminder(entities)
    elif intent == "add_schedule":
        response = handle_add_schedule(entities)
    elif intent == "view_schedule":
        response = handle_view_schedule()
    elif intent == "view_reminders":
        response = handle_view_reminders()
    elif intent == "delete_reminder":
        import re
        id_match = re.search(r'\d+', user_input)
        if id_match:
            response = handle_delete_reminder(int(id_match.group()))
        else:
            response = "Please specify a reminder ID. E.g., *'Delete reminder 3'*"
    elif intent == "delete_schedule":
        import re
        id_match = re.search(r'\d+', user_input)
        if id_match:
            response = handle_delete_schedule(int(id_match.group()))
        else:
            response = "Please specify an event ID. E.g., *'Delete event 2'*"
    elif intent == "greet":
        response = (
            "👋 Hello! I'm your **AI Virtual Assistant**.\n\n"
            "I can help you with:\n"
            "- 🔔 Setting reminders\n"
            "- 📅 Managing your schedule\n"
            "- 💬 Answering queries\n\n"
            "Try saying: *'Remind me to call John at 5 PM'*"
        )
    elif intent == "help":
        response = (
            "🆘 **Here's what I can do:**\n\n"
            "🔔 **Reminders:**\n"
            "- *'Remind me to take medicine at 8 AM'*\n"
            "- *'Show my reminders'*\n"
            "- *'Delete reminder 1'*\n\n"
            "📅 **Schedule:**\n"
            "- *'Schedule a meeting at 3 PM tomorrow'*\n"
            "- *'Show my schedule'*\n"
            "- *'Delete event 2'*\n\n"
            "💬 **General:** Just say hi or ask anything!"
        )
    elif intent == "exit":
        response = "👋 Goodbye! Have a productive day! 🌟"
    else:
        response = (
            "🤔 I didn't quite understand that. Try:\n"
            "- *'Remind me to...'*\n"
            "- *'Schedule a meeting...'*\n"
            "- *'Show my reminders'*\n"
            "- Type **help** for all commands"
        )

    return response, result

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Virtual Assistant</h1>
    <p>Powered by NLP · spaCy · NLTK</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────
col1 = st.container()

with col1:
    st.markdown("### 💬 Chat")

    # Chat history display
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div class="chat-bubble-bot">
                👋 Hello! I'm your AI Virtual Assistant powered by NLP.<br><br>
                Try saying: <em>'Remind me to call John at 5 PM'</em> or <em>'Show my schedule'</em>
            </div>
            """, unsafe_allow_html=True)
        else:
            for chat in st.session_state.chat_history:
                st.markdown(f"""
                <div class="chat-bubble-user">👤 {chat['user']}</div>
                """, unsafe_allow_html=True)

                if st.session_state.show_nlp_debug and "nlp_data" in chat:
                    nlp = chat["nlp_data"]
                    st.markdown(f"""
                    <div class="nlp-debug">
                        🧠 Intent: <b>{nlp['intent']}</b> &nbsp;|&nbsp;
                        Entities: {nlp['entities']['raw_entities']} &nbsp;|&nbsp;
                        Tokens: {nlp['preprocessed']['lemmatized'][:5]}
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="chat-bubble-bot">
                    <span class="intent-badge">{chat.get('intent','unknown')}</span><br>
                    🤖 {chat['bot']}
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")


    # Input
    with st.container():
        input_col, btn_col, voice_col = st.columns([5, 1, 1])
        with input_col:
            user_input = st.text_input(
                "Message",
                placeholder="Type or 🎤 speak your message...",
                label_visibility="collapsed",
                key="user_input"
            )
        with btn_col:
            send = st.button("Send 🚀")
        with voice_col:
            voice = st.button("🎤 Speak")

    # Handle voice input
    if voice:
        with st.spinner("🎤 Listening... Speak now!"):
            result = listen()
        if result["success"]:
            st.session_state.voice_text = result["text"]
            st.info(f"🎤 You said: **{result['text']}**")
            response, nlp_result = generate_response(result["text"])
            # Speak the response back
            speak(response)
            st.session_state.chat_history.append({
                "user": f"🎤 {result['text']}",
                "bot": response,
                "intent": nlp_result["intent"],
                "nlp_data": nlp_result
            })
            st.rerun()
        else:
            st.error(result["error"])

    # Handle text input
    if send and user_input.strip():
        response, nlp_result = generate_response(user_input.strip())
        # Speak the response back
        speak(response)
        st.session_state.chat_history.append({
            "user": user_input.strip(),
            "bot": response,
            "intent": nlp_result["intent"],
            "nlp_data": nlp_result
        })
        st.rerun()

# ─────────────────────────────────────────────
# LEFT SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛠️ Controls")

    st.session_state.show_nlp_debug = st.toggle("🧠 Show NLP Debug", value=False)

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Quick Stats")

    from database import get_all_reminders, get_all_schedules
    reminders = get_all_reminders()
    schedules = get_all_schedules()

    # Stats in a table layout
    st.markdown(f"""
    <table style="width:100%; border-collapse:collapse;">
        <tr>
            <td style="padding:0.5rem; text-align:center; background:rgba(255,255,255,0.05);
                border-radius:10px 0 0 10px; border:1px solid rgba(167,139,250,0.2);">
                <h2 style="color:#a78bfa; margin:0">{len(reminders)}</h2>
                <p style="color:#a0aec0; margin:0; font-size:0.75rem">Reminders</p>
            </td>
            <td style="padding:0.5rem; text-align:center; background:rgba(255,255,255,0.05);
                border-radius:0 10px 10px 0; border:1px solid rgba(167,139,250,0.2);">
                <h2 style="color:#60a5fa; margin:0">{len(schedules)}</h2>
                <p style="color:#a0aec0; margin:0; font-size:0.75rem">Events</p>
            </td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📌 Quick Commands")

    # Quick commands in a clean table
    st.markdown("""
    <table style="width:100%; border-collapse:collapse; font-size:0.78rem;">
        <tr style="background:rgba(167,139,250,0.15);">
            <th style="padding:0.4rem 0.6rem; text-align:left; color:#a78bfa;">Action</th>
            <th style="padding:0.4rem 0.6rem; text-align:left; color:#a78bfa;">Example</th>
        </tr>
        <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
            <td style="padding:0.4rem 0.6rem; color:#34d399;">🔔 Set Reminder</td>
            <td style="padding:0.4rem 0.6rem; color:#e2e8f0;"><em>"Remind me to take medicine at 8 AM"</em></td>
        </tr>
        <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
            <td style="padding:0.4rem 0.6rem; color:#60a5fa;">📅 Schedule Event</td>
            <td style="padding:0.4rem 0.6rem; color:#e2e8f0;"><em>"Schedule team meeting at 3 PM tomorrow"</em></td>
        </tr>
        <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
            <td style="padding:0.4rem 0.6rem; color:#f59e0b;">👁️ View Reminders</td>
            <td style="padding:0.4rem 0.6rem; color:#e2e8f0;"><em>"Show my reminders"</em></td>
        </tr>
        <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
            <td style="padding:0.4rem 0.6rem; color:#f59e0b;">👁️ View Schedule</td>
            <td style="padding:0.4rem 0.6rem; color:#e2e8f0;"><em>"Show my schedule"</em></td>
        </tr>
        <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
            <td style="padding:0.4rem 0.6rem; color:#f87171;">🗑️ Delete Reminder</td>
            <td style="padding:0.4rem 0.6rem; color:#e2e8f0;"><em>"Delete reminder 1"</em></td>
        </tr>
        <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
            <td style="padding:0.4rem 0.6rem; color:#f87171;">🗑️ Delete Event</td>
            <td style="padding:0.4rem 0.6rem; color:#e2e8f0;"><em>"Delete event 2"</em></td>
        </tr>
        <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
            <td style="padding:0.4rem 0.6rem; color:#a78bfa;">👋 Greet</td>
            <td style="padding:0.4rem 0.6rem; color:#e2e8f0;"><em>"Hello" / "Hi"</em></td>
        </tr>
        <tr>
            <td style="padding:0.4rem 0.6rem; color:#a78bfa;">🆘 Help</td>
            <td style="padding:0.4rem 0.6rem; color:#e2e8f0;"><em>"Help" / "What can you do?"</em></td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center; color:#4a5568; font-size:0.75rem;
        font-family:'Space Mono',monospace; margin-top:1rem;">
        🕐 {datetime.now().strftime("%d %b %Y · %I:%M %p")}
    </div>
    """, unsafe_allow_html=True)
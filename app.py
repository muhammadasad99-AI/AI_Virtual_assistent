import streamlit as st
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(__file__))

from nlp_engine import process_input
from reminder import handle_set_reminder, handle_view_reminders, handle_delete_reminder
from scheduler import handle_add_schedule, handle_view_schedule, handle_delete_schedule
from database import init_db, get_all_reminders, get_all_schedules

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Virtual Assistant",
    page_icon="🤖",
    layout="wide"
)

# ─────────────────────────────────────────────
# CUSTOM CSS + BROWSER VOICE JS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #f0f0f0; }
    .main-header { text-align: center; padding: 2rem 0 1rem 0; }
    .main-header h1 {
        font-family: 'Syne', sans-serif; font-weight: 800; font-size: 3rem;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.2rem;
    }
    .main-header p { color: #a0aec0; font-size: 1rem; font-family: 'Space Mono', monospace; }
    .chat-bubble-user {
        background: linear-gradient(135deg, #6d28d9, #4f46e5); color: white;
        padding: 0.9rem 1.2rem; border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0; max-width: 80%; margin-left: auto; font-size: 0.95rem;
        box-shadow: 0 4px 15px rgba(109,40,217,0.3);
    }
    .chat-bubble-bot {
        background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.1);
        color: #e2e8f0; padding: 0.9rem 1.2rem; border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 0; max-width: 80%; font-size: 0.95rem; backdrop-filter: blur(10px);
    }
    .intent-badge {
        display: inline-block; background: linear-gradient(135deg, #059669, #10b981);
        color: white; padding: 0.2rem 0.7rem; border-radius: 20px;
        font-size: 0.75rem; font-family: 'Space Mono', monospace; margin-bottom: 0.4rem;
    }
    .nlp-debug {
        background: rgba(0,0,0,0.3); border: 1px solid rgba(168,85,247,0.3);
        border-radius: 10px; padding: 0.8rem 1rem;
        font-family: 'Space Mono', monospace; font-size: 0.75rem; color: white;
    }
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(167,139,250,0.4) !important;
        border-radius: 12px !important; color: black !important;
        font-family: 'Syne', sans-serif !important; padding: 0.7rem 1rem !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #4f46e5) !important; color: white !important;
        border: none !important; border-radius: 10px !important; font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important; padding: 0.5rem 1.5rem !important; transition: all 0.2s !important;
    }
    .stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(124,58,237,0.5) !important; }
    div[data-testid="stSidebar"] { background: rgba(15, 12, 41, 0.95) !important; }
    #voice-btn {
        background: linear-gradient(135deg, #059669, #10b981); color: white;
        border: none; border-radius: 10px; padding: 0.5rem 1rem; font-size: 1rem;
        cursor: pointer; width: 100%; font-family: 'Syne', sans-serif;
        font-weight: 600; transition: all 0.2s;
    }
    #voice-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(5,150,105,0.5); }
    #voice-btn.listening { background: linear-gradient(135deg, #dc2626, #ef4444) !important; animation: pulse 1s infinite; }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }
        70% { box-shadow: 0 0 0 10px rgba(239,68,68,0); }
        100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
    }
</style>

<script>
function startVoiceInput() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Voice not supported. Please use Chrome or Edge.');
        return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;
    const btn = document.getElementById('voice-btn');
    btn.classList.add('listening');
    btn.innerText = 'Listening...';
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        btn.classList.remove('listening');
        btn.innerText = 'Speak';
        const input = window.parent.document.querySelector('.stTextInput input');
        if (input) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            nativeInputValueSetter.call(input, transcript);
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    };
    recognition.onerror = function(event) {
        btn.classList.remove('listening');
        btn.innerText = 'Speak';
    };
    recognition.onend = function() {
        btn.classList.remove('listening');
        btn.innerText = 'Speak';
    };
    recognition.start();
}

function speakText(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const clean = text.replace(/\*\*/g,'').replace(/\*/g,'').replace(/#{1,6}/g,'').replace(/[^\x00-\x7F]/g,'');
    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.lang = 'en-US'; utterance.rate = 1.0; utterance.pitch = 1.0; utterance.volume = 1.0;
    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find(v => v.name.includes('Zira') || v.name.includes('Female') || v.name.includes('Susan'));
    if (preferred) utterance.voice = preferred;
    window.speechSynthesis.speak(utterance);
}

function showBrowserNotification(title, body) {
    if ('Notification' in window) {
        if (Notification.permission === 'default') {
            Notification.requestPermission().then(p => {
                if (p === 'granted') new Notification('🤖 ' + title, { body: body });
            });
        } else if (Notification.permission === 'granted') {
            new Notification('🤖 ' + title, { body: body });
        }
    }
}
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────
init_db()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "show_nlp_debug" not in st.session_state:
    st.session_state.show_nlp_debug = False
if "last_response" not in st.session_state:
    st.session_state.last_response = ""

# ─────────────────────────────────────────────
# CHECK DUE REMINDERS
# ─────────────────────────────────────────────
def check_due_reminders():
    reminders = get_all_reminders()
    now = datetime.now()
    current_formats = [
        now.strftime("%I:%M %p").lstrip("0"),
        now.strftime("%I %p").lstrip("0"),
        now.strftime("%H:%M"),
    ]
    for r in reminders:
        if r[2]:
            for fmt in current_formats:
                if r[2].strip().lower() == fmt.lower():
                    st.toast(f"Reminder: {r[1]} at {r[2]}", icon="🔔")
                    st.markdown(f"""
                    <script>showBrowserNotification("Reminder: {r[1]}", "Time: {r[2]}");</script>
                    """, unsafe_allow_html=True)

check_due_reminders()

# ─────────────────────────────────────────────
# RESPONSE HANDLER
# ─────────────────────────────────────────────
def generate_response(user_input: str) -> tuple:
    result = process_input(user_input)
    intent = result["intent"]
    entities = result["entities"]

    if intent == "set_reminder":
        response = handle_set_reminder(entities)
        st.toast("Reminder saved!", icon="🔔")
    elif intent == "add_schedule":
        response = handle_add_schedule(entities)
        st.toast("Event scheduled!", icon="📅")
    elif intent == "view_schedule":
        response = handle_view_schedule()
    elif intent == "view_reminders":
        response = handle_view_reminders()
    elif intent == "delete_reminder":
        import re
        id_match = re.search(r'\d+', user_input)
        if id_match:
            response = handle_delete_reminder(int(id_match.group()))
            st.toast("Reminder deleted!", icon="🗑️")
        else:
            response = "Please specify a reminder ID. E.g., *'Delete reminder 3'*"
    elif intent == "delete_schedule":
        import re
        id_match = re.search(r'\d+', user_input)
        if id_match:
            response = handle_delete_schedule(int(id_match.group()))
            st.toast("Event deleted!", icon="🗑️")
        else:
            events = handle_view_schedule()
            response = f"Please specify an event ID.\n\n{events}\nE.g., *'Delete event 1'*"
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
            "🔔 **Reminders:** 'Remind me to take medicine at 8 AM'\n"
            "📅 **Schedule:** 'Schedule a meeting at 3 PM tomorrow'\n"
            "👁️ **View:** 'Show my reminders' / 'Show my schedule'\n"
            "🗑️ **Delete:** 'Delete reminder 1' / 'Delete event 2'\n"
        )
        
    elif intent == "add_schedule":
        response = handle_add_schedule(entities)
        st.toast("Event scheduled!", icon="📅")

        #ADD THIS: if sentence also contains remind → auto set reminder too
        if any(word in user_input.lower() for word in ["remind", "reminder"]):
            handle_set_reminder(entities)
            response += "\n\n🔔 **Reminder also set** for the same time!"
            st.toast("Reminder also set!", icon="🔔")     
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
# SPEAK LAST RESPONSE
# ─────────────────────────────────────────────
if st.session_state.last_response:
    clean = st.session_state.last_response.replace("**","").replace("*","").replace("\n"," ")
    st.markdown(f"<script>setTimeout(function(){{speakText(`{clean}`);}},500);</script>", unsafe_allow_html=True)
    st.session_state.last_response = ""

# ─────────────────────────────────────────────
# CHAT AREA
# ─────────────────────────────────────────────
st.markdown("### 💬 Chat")

with st.container():
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="chat-bubble-bot">
            👋 Hello! I'm your AI Virtual Assistant powered by NLP.<br><br>
            Try: <em>'Remind me to call John at 5 PM'</em> or <em>'Show my schedule'</em>
        </div>
        """, unsafe_allow_html=True)
    else:
        for chat in st.session_state.chat_history:
            st.markdown(f'<div class="chat-bubble-user">👤 {chat["user"]}</div>', unsafe_allow_html=True)
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

# ─────────────────────────────────────────────
# INPUT AREA
# ─────────────────────────────────────────────
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import io

input_col, btn_col, voice_col = st.columns([5, 1, 1])

with input_col:
    user_input = st.text_input(
        "Message",
        placeholder="Type your message here...",
        label_visibility="collapsed",
        key="user_input"
    )

with btn_col:
    send = st.button("Send 🚀")

with voice_col:
    audio = mic_recorder(
        start_prompt="🎤 Speak",
        stop_prompt="⏹️ Stop",
        just_once=True,
        use_container_width=True,
        key="mic"
    )

# ─────────────────────────────────────────────
# TTS — BROWSER SPEAKS RESPONSE NATURALLY
# ─────────────────────────────────────────────
def speak_response(text: str):
    clean = (text
        .replace("**", "").replace("*", "")
        .replace("#", "").replace("━", "")
        .replace("🔔","").replace("📅","")
        .replace("✅","").replace("❌","")
        .replace("📌","").replace("🕐","")
        .replace("👋","").replace("🤖","")
        .replace("🆘","").replace("🆔","")
        .replace("🗑️","").replace("👁️","")
        .replace("\n", " ").replace('"', "'")
    )
    st.markdown(f"""
    <script>
    (function() {{
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance("{clean}");
        msg.lang = 'en-US';
        msg.rate = 1.0;
        msg.pitch = 1.1;
        msg.volume = 1.0;
        // Wait for voices to load then pick best one
        function setVoiceAndSpeak() {{
            var voices = window.speechSynthesis.getVoices();
            var preferred = voices.find(v =>
                v.name.includes('Zira') ||
                v.name.includes('Google US English') ||
                v.name.includes('Samantha') ||
                v.name.includes('Karen')
            );
            if (preferred) msg.voice = preferred;
            window.speechSynthesis.speak(msg);
        }}
        if (window.speechSynthesis.getVoices().length > 0) {{
            setVoiceAndSpeak();
        }} else {{
            window.speechSynthesis.onvoiceschanged = setVoiceAndSpeak;
        }}
    }})();
    </script>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# AUTO PROCESS VOICE — no manual submit needed!
# ─────────────────────────────────────────────
if audio and audio.get("bytes"):
    with st.spinner("🎤 Understanding your voice..."):
        try:
            recognizer = sr.Recognizer()
            from pydub import AudioSegment

            # Convert WebM/OGG to WAV
            audio_bytes = io.BytesIO(audio["bytes"])
            audio_segment = AudioSegment.from_file(audio_bytes)
            wav_bytes = io.BytesIO()
            audio_segment.export(wav_bytes, format="wav")
            wav_bytes.seek(0)

            with sr.AudioFile(wav_bytes) as source:
                audio_data = recognizer.record(source)
            voice_text = recognizer.recognize_google(audio_data)

            # ✅ Auto process
            response, nlp_result = generate_response(voice_text)
            st.session_state.chat_history.append({
                "user": f"🎤 {voice_text}",
                "bot": response,
                "intent": nlp_result["intent"],
                "nlp_data": nlp_result
            })
            speak_response(response)
            st.rerun()

        except sr.UnknownValueError:
            st.warning("🤔 Could not understand. Please speak clearly and try again.")
            speak_response("Sorry, I could not understand. Please speak clearly and try again.")
        except sr.RequestError:
            st.error("🌐 Internet required for voice recognition.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ─────────────────────────────────────────────
# HANDLE TEXT SEND
# ─────────────────────────────────────────────
if send and user_input.strip():
    response, nlp_result = generate_response(user_input.strip())
    st.session_state.chat_history.append({
        "user": user_input.strip(),
        "bot": response,
        "intent": nlp_result["intent"],
        "nlp_data": nlp_result
    })
    # 🔊 Speak text response too
    speak_response(response)
    st.rerun()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛠️ Controls")
    st.session_state.show_nlp_debug = st.toggle("🧠 Show NLP Debug", value=False)
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    reminders = get_all_reminders()
    schedules = get_all_schedules()
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
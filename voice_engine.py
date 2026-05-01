import speech_recognition as sr
import pyttsx3
import threading

# ─────────────────────────────────────────────
# TEXT TO SPEECH ENGINE
# ─────────────────────────────────────────────
engine = pyttsx3.init()

def configure_voice():
    voices = engine.getProperty('voices')
    # Use female voice if available
    for voice in voices:
        if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', 170)    # Speed (150-200 is natural)
    engine.setProperty('volume', 1.0)  # Max volume

configure_voice()

def speak(text: str):
    """Convert text to speech in a separate thread so UI doesn't freeze"""
    # Clean markdown symbols before speaking
    clean_text = (
        text.replace("**", "")
            .replace("*", "")
            .replace("#", "")
            .replace("🔔", "")
            .replace("📅", "")
            .replace("✅", "")
            .replace("❌", "")
            .replace("📌", "")
            .replace("🕐", "")
            .replace("👋", "")
            .replace("🤖", "")
            .replace("🆘", "")
            .replace("━", "")
            .replace("🆔", "ID")
    )

    def run_speech():
        engine.say(clean_text)
        engine.runAndWait()

    thread = threading.Thread(target=run_speech)
    thread.daemon = True
    thread.start()


# ─────────────────────────────────────────────
# SPEECH TO TEXT ENGINE
# ─────────────────────────────────────────────
recognizer = sr.Recognizer()

def listen() -> dict:
    """
    Listen from microphone and return recognized text.
    Returns: {"success": True, "text": "..."} or {"success": False, "error": "..."}
    """
    try:
        with sr.Microphone() as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            recognizer.pause_threshold = 1.0  # seconds of silence before stopping

            print("🎤 Listening...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

        # Recognize using Google (free, no API key needed)
        text = recognizer.recognize_google(audio)
        print(f"✅ Recognized: {text}")
        return {"success": True, "text": text}

    except sr.WaitTimeoutError:
        return {"success": False, "error": "⏰ No speech detected. Please try again."}
    except sr.UnknownValueError:
        return {"success": False, "error": "🤔 Could not understand. Please speak clearly."}
    except sr.RequestError:
        return {"success": False, "error": "🌐 Internet required for voice recognition."}
    except Exception as e:
        return {"success": False, "error": f"❌ Microphone error: {str(e)}"}
import nltk
import spacy
import re
from datetime import datetime, timedelta

# Download required NLTK data
import nltk
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# ─────────────────────────────────────────────
# INTENT DEFINITIONS
# ─────────────────────────────────────────────
INTENTS = {
    "set_reminder": [
        "remind", "reminder", "alert", "notify", "notification", "set alarm", "alarm"
    ],
    "add_schedule": [
    "schedule", "meeting", "appointment", "event", "book", "plan",
    "make", "create", "set up", "organize", "arrange", "add meeting",
    "job", "jobs", "work", "session", "call"
     ],
    "view_schedule": [
    "show schedule", "view schedule", "what's scheduled", "my events",
    "list events", "show events", "upcoming", "calendar",
    "show my schedule", "view my schedule", "all events", "my schedule"
    ],
    "view_reminders": [
        "show reminders", "view reminders", "my reminders", "list reminders"
    ],
    "delete_reminder": [
        "delete reminder", "remove reminder", "cancel reminder"
    ],
    "delete_schedule": [
    "delete event", "remove event", "cancel event", "cancel meeting",
    "delete schedule", "remove schedule"
    ],
    "greet": [
        "hello", "hi", "hey", "good morning", "good evening", "good afternoon", "howdy"
    ],
    "help": [
        "help", "what can you do", "commands", "features", "capabilities"
    ],
    "exit": [
        "bye", "goodbye", "exit", "quit", "close", "see you"
    ]
}

# ─────────────────────────────────────────────
# DELETE KEYWORDS — checked FIRST before anything
# ─────────────────────────────────────────────
DELETE_KEYWORDS = ["delete", "remove", "cancel", "erase", "clear"]
# DETECT INTENT FUNCTION
def detect_intent(user_input: str) -> str:
    text = user_input.lower().strip()
    tokens = word_tokenize(text)
    lemmatized = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words]

    # ── STEP 1: Check delete intents FIRST ──────
    # If user says delete/remove/cancel → check what they want to delete
    has_delete = any(word in text for word in DELETE_KEYWORDS)

    if has_delete:
        if any(word in text for word in ["reminder", "remind", "alarm", "alert"]):
            return "delete_reminder"
        if any(word in text for word in ["event", "schedule", "meeting", "appointment"]):
            return "delete_schedule"

    # ── STEP 2: Check view intents ───────────────
    view_reminder_keys = ["show reminder", "view reminder", "my reminder", "list reminder"]
    view_schedule_keys = ["show schedule", "view schedule", "my schedule", "list schedule",
                          "show event", "view event", "my event", "list event", "upcoming"]

    if any(k in text for k in view_reminder_keys):
        return "view_reminders"
    if any(k in text for k in view_schedule_keys):
        return "view_schedule"

    # ── STEP 3: Check greet & help ───────────────
    greet_words = ["hello", "hi", "hey", "good morning", "good evening"]
    is_short = len(tokens) <= 4
    if any(word in text for word in greet_words) and is_short:
        return "greet"
    if any(word in text for word in ["help", "what can you do", "commands", "features"]):
        return "help"
    if any(word in text for word in ["bye", "goodbye", "exit", "quit"]):
        return "exit"

    # ── STEP 4: Check set/add intents LAST ───────
    if any(word in text for word in ["remind", "reminder", "alert", "notify", "alarm"]):
        return "set_reminder"
    if any(word in text for word in ["schedule", "meeting", "appointment", "event",
                                  "book", "plan", "make", "create", "organize",
                                  "arrange","session"]):
        return "add_schedule"

    # ── STEP 5: Score-based fallback ─────────────
    scores = {}
    for intent, keywords in INTENTS.items():
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 2
            elif any(keyword in t for t in lemmatized):
                score += 1
        scores[intent] = score

    best_intent = max(scores, key=scores.get)
    if scores[best_intent] == 0:
        return "unknown"
    return best_intent

# ─────────────────────────────────────────────
# ENTITY EXTRACTION (spaCy NER)
# ─────────────────────────────────────────────
def extract_entities(user_input: str) -> dict:
    doc = nlp(user_input)
    entities = {
        "time": None,
        "date": None,
        "title": None,
        "location": None, 
        "raw_entities": []
    }

    for ent in doc.ents:
        entities["raw_entities"].append({"text": ent.text, "label": ent.label_})
        if ent.label_ == "TIME":
            entities["time"] = ent.text
        elif ent.label_ == "DATE":
            entities["date"] = ent.text
        elif ent.label_ in  ["GPE", "LOC"]:
            entities["location"] = ent.text

    # Extract title: text after keywords like "remind me to", "schedule", "about"
    title_patterns = [
        r"remind(?:er)? (?:me )?(?:to |about |for )?(.+?)(?:\s+at\s+|\s+on\s+|$)",
        r"schedule (?:a |an )?(.+?)(?:\s+at\s+|\s+on\s+|$)",
        r"(?:meeting|appointment|event) (?:about |for |titled )?['\"]?(.+?)['\"]?(?:\s+at\s+|\s+on\s+|$)",
    ]

    text = user_input.lower()
    for pattern in title_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            entities["title"] = match.group(1).strip().title()
            break

    # Fallback time extraction with regex
    if not entities["time"]:
        time_match = re.search(
            r'\b(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\b', user_input, re.IGNORECASE
        )
        if time_match:
            entities["time"] = time_match.group(1)

    return entities

# TEXT PREPROCESSING

def preprocess_text(text: str) -> dict:
    tokens = word_tokenize(text.lower())
    filtered = [t for t in tokens if t not in stop_words and t.isalpha()]
    lemmatized = [lemmatizer.lemmatize(t) for t in filtered]
    pos_tags = nltk.pos_tag(tokens)

    return {
        "original": text,
        "tokens": tokens,
        "filtered_tokens": filtered,
        "lemmatized": lemmatized,
        "pos_tags": pos_tags
    }

# MAIN PROCESS FUNCTION

def process_input(user_input: str) -> dict:
    intent = detect_intent(user_input)
    entities = extract_entities(user_input)
    preprocessed = preprocess_text(user_input)

    return {
        "intent": intent,
        "entities": entities,
        "preprocessed": preprocessed,
        "original_input": user_input
    }
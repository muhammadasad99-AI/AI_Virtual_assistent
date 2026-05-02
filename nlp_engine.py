import sys
import subprocess

# Force install nltk
try:
    import nltk
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "nltk"], check=False)
    import nltk

import re
import os

# Download NLTK data
for resource in ['punkt', 'punkt_tab', 'wordnet', 'stopwords', 'averaged_perceptron_tagger', 'averaged_perceptron_tagger_eng']:
    try:
        nltk.download(resource, quiet=True)
    except:
        pass

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# ─────────────────────────────────────────────
# INTENT DEFINITIONS
# ─────────────────────────────────────────────
INTENTS = {
    "set_reminder": ["remind", "reminder", "alert", "notify", "notification", "alarm"],
    "add_schedule": ["schedule", "meeting", "appointment", "event", "book", "plan",
                     "make", "create", "organize", "arrange", "job", "jobs", "session"],
    "view_schedule": ["show schedule", "view schedule", "my schedule", "list schedule",
                      "show event", "view event", "my event", "upcoming", "calendar"],
    "view_reminders": ["show reminder", "view reminder", "my reminder", "list reminder"],
    "delete_reminder": ["delete reminder", "remove reminder", "cancel reminder"],
    "delete_schedule": ["delete event", "remove event", "cancel event", "cancel meeting"],
    "greet": ["hello", "hi", "hey", "good morning", "good evening"],
    "help": ["help", "what can you do", "commands", "features"],
    "exit": ["bye", "goodbye", "exit", "quit"]
}

DELETE_KEYWORDS = ["delete", "remove", "cancel", "erase", "clear"]

# ─────────────────────────────────────────────
# ENTITY EXTRACTION — pure regex, no spaCy
# ─────────────────────────────────────────────
def extract_entities(user_input: str) -> dict:
    entities = {
        "time": None,
        "date": None,
        "title": None,
        "location": None,
        "raw_entities": []
    }

    text = user_input.lower()

    # Extract time
    time_match = re.search(
        r'\b(\d{1,2}(?::\d{2})?\s*(?:am|pm))\b', user_input, re.IGNORECASE
    )
    if time_match:
        entities["time"] = time_match.group(1)

    # Extract date keywords
    date_keywords = ["today", "tomorrow", "monday", "tuesday", "wednesday",
                     "thursday", "friday", "saturday", "sunday", "next week"]
    for dk in date_keywords:
        if dk in text:
            entities["date"] = dk.title()
            break

    # Extract location — look for "in [City]" pattern
    loc_match = re.search(r'\bin\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)', user_input)
    if loc_match:
        entities["location"] = loc_match.group(1)

    # Extract title
    title_patterns = [
        r"remind(?:er)?\s+(?:me\s+)?(?:to\s+|about\s+|for\s+)?(.+?)(?:\s+at\s+|\s+on\s+|$)",
        r"schedule\s+(?:a\s+|an\s+)?(.+?)(?:\s+at\s+|\s+on\s+|\s+in\s+|$)",
        r"(?:meeting|appointment|event|job)\s+(?:about\s+|for\s+|with\s+)?(.+?)(?:\s+at\s+|\s+on\s+|$)",
    ]
    for pattern in title_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            title = match.group(1).strip().title()
            if len(title) > 2:
                entities["title"] = title
                break

    return entities

# ─────────────────────────────────────────────
# INTENT DETECTION
# ─────────────────────────────────────────────
def detect_intent(user_input: str) -> str:
    text = user_input.lower().strip()
    tokens = word_tokenize(text)
    lemmatized = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words]

    # STEP 1: Delete intents first
    has_delete = any(word in text for word in DELETE_KEYWORDS)
    if has_delete:
        if any(w in text for w in ["reminder", "remind", "alarm", "alert"]):
            return "delete_reminder"
        if any(w in text for w in ["event", "schedule", "meeting", "appointment"]):
            return "delete_schedule"

    # STEP 2: View intents
    if any(k in text for k in ["show reminder", "view reminder", "my reminder", "list reminder", "show my reminder"]):
        return "view_reminders"
    if any(k in text for k in ["show schedule", "view schedule", "my schedule", "show event", "view event", "upcoming"]):
        return "view_schedule"

    # STEP 3: Greet — only short messages
    if any(w in text for w in ["hello", "hi", "hey", "good morning", "good evening"]) and len(tokens) <= 4:
        return "greet"

    # STEP 4: Help and exit
    if any(w in text for w in ["help", "what can you do", "commands"]):
        return "help"
    if any(w in text for w in ["bye", "goodbye", "exit", "quit"]):
        return "exit"

    # STEP 5: Set/add intents
    if any(w in text for w in ["remind", "reminder", "alert", "notify", "alarm"]):
        return "set_reminder"
    if any(w in text for w in ["schedule", "meeting", "appointment", "event",
                                "book", "plan", "make", "create", "organize",
                                "arrange", "job", "jobs", "session"]):
        return "add_schedule"

    # STEP 6: Score fallback
    scores = {}
    for intent, keywords in INTENTS.items():
        score = sum(2 if kw in text else 1 if any(kw in t for t in lemmatized) else 0
                   for kw in keywords)
        scores[intent] = score

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unknown"

# ─────────────────────────────────────────────
# TEXT PREPROCESSING
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# MAIN PROCESS FUNCTION
# ─────────────────────────────────────────────
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
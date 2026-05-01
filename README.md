# AI Virtual Assistant

An NLP-powered virtual assistant built with **spaCy**, **NLTK**, and **Streamlit**.

---

## Features
- Set & manage reminders using natural language
- Schedule & manage events/meetings
- NLP-powered intent detection & entity extraction
- Conversational chat interface
- SQLite local database storage

---

## Installation

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## Run the App

```bash
streamlit run app.py
```

---

## Example Commands

| Command | Action |
|---------|--------|
| `Remind me to call John at 5 PM` | Sets a reminder |
| `Schedule a meeting at 3 PM tomorrow` | Adds a schedule |
| `Show my reminders` | Lists all reminders |
| `Show my schedule` | Lists all events |
| `Delete reminder 1` | Deletes reminder #1 |
| `Delete event 2` | Deletes event #2 |

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| spaCy | Named Entity Recognition (NER) |
| NLTK | Tokenization, Lemmatization, POS Tagging |
| Streamlit | Web UI |
| SQLite | Local database |
| Python schedule | Scheduling logic |

---

## Project Structure

```
virtual_assistant/
├── app.py           → Main Streamlit UI
├── nlp_engine.py    → NLP processing (spaCy + NLTK)
├── reminder.py      → Reminder logic
├── scheduler.py     → Schedule logic
├── database.py      → SQLite database
├── requirements.txt → Dependencies
└── README.md
```
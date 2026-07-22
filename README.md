# Suraksha Shield

Real-time AI-powered scam / "digital arrest" call detection. A rules engine scans a live call transcript for known scam patterns, and Claude provides a contextual verdict (safe / suspicious / likely_scam / scam) with an explanation and recommended action steps.

- **Backend:** FastAPI + a keyword-based rules engine + Claude (Anthropic API)
- **Frontend:** Static HTML/CSS/JS using the browser's Web Speech API for live transcription

> Hackathon prototype — not production-hardened. See "Known limitations" below.

## Project structure

```
suraksha-shield/
├── app.py                # FastAPI app and routes
├── rules_engine.py       # Keyword/pattern-based scam signal detection
├── llm_classifier.py     # Claude-based contextual classification
├── session_manager.py    # In-memory session + call-transcript state
├── requirements.txt
├── .env.example
├── index.html
├── script.js
└── style.css
```

## Prerequisites

- Python 3.9+
- An [Anthropic API key](https://console.anthropic.com/)
- A modern Chromium-based browser (the frontend uses the Web Speech API, which Chrome supports best)

## Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and paste in your real ANTHROPIC_API_KEY

uvicorn app:app --reload --port 8000
```

The API will be live at `http://127.0.0.1:8000`. Check `http://127.0.0.1:8000/health` to confirm it's running.

## Frontend setup

The frontend is static — no build step required.

```bash
cd frontend
python -m http.server 5500
```

Then open `http://127.0.0.1:5500` in Chrome and click **Start Protection** (grant microphone access when prompted).

> `script.js` points at `http://127.0.0.1:8000` by default (see `API_URL` at the top of the file). Update this if your backend runs elsewhere.

## API endpoints

| Method | Endpoint                       | Description                                  |
|--------|---------------------------------|-----------------------------------------------|
| GET    | `/health`                       | Health check                                  |
| POST   | `/session/start`                | Start a new live call session                 |
| POST   | `/session/{session_id}/transcript` | Add a transcript chunk to an active session |
| POST   | `/check`                        | One-shot analysis of a block of text          |

## Known limitations

- Sessions are stored in memory only — they're lost on server restart and won't scale across multiple processes/workers.
- CORS is wide open (`allow_origins=["*"]`) for local development — lock this down to your real frontend origin before deploying publicly.
- No authentication on any endpoint.
- Web Speech API transcription accuracy varies by browser/accent/background noise.

## Emergency resources (India)

If money has already been transferred to a suspected scammer, contact the **National Cyber Crime Helpline: 1930** immediately.

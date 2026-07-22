import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rules_engine import scan_text
from llm_classifier import classify
from session_manager import SessionManager


app = FastAPI(
    title="Suraksha Shield API",
    description="Real-time AI-powered scam detection backend",
    version="2.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hackathon/local dev only — restrict to your real frontend origin(s) before deploying publicly
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# SESSION MANAGER
# --------------------------------------------------

manager = SessionManager()


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class TranscriptChunk(BaseModel):
    text: str


class OneShotCheck(BaseModel):
    text: str


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "Suraksha Shield"
    }


# --------------------------------------------------
# START LIVE SESSION
# --------------------------------------------------

@app.post("/session/start")
def start_session():

    session_id = str(uuid.uuid4())

    manager.start_session(session_id)

    return {
        "session_id": session_id,
        "message": "Protection session started"
    }


# --------------------------------------------------
# ADD LIVE TRANSCRIPT
# --------------------------------------------------

@app.post("/session/{session_id}/transcript")
def add_transcript(
    session_id: str,
    chunk: TranscriptChunk
):

    if manager.get_session(session_id) is None:

        raise HTTPException(
            status_code=404,
            detail="Session not found. Start a new session first."
        )


    if not chunk.text or not chunk.text.strip():

        raise HTTPException(
            status_code=400,
            detail="Transcript text cannot be empty."
        )


    return manager.add_transcript_chunk(
        session_id,
        chunk.text.strip()
    )


# --------------------------------------------------
# ONE-SHOT ANALYSIS
# --------------------------------------------------

@app.post("/check")
def one_shot_check(
    payload: OneShotCheck
):

    if not payload.text or not payload.text.strip():

        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty."
        )


    text = payload.text.strip()


    rules_result = scan_text(text)

    rules_dict = rules_result.to_dict()


    try:

        verdict = classify(
            text,
            rules_dict
        )

        llm_error = None


    except Exception as error:

        print(
            "Claude classification failed:",
            error
        )

        verdict = None

        llm_error = str(error)


    return {

        "rules_result": rules_dict,

        "verdict": verdict,

        "llm_error": llm_error

    }
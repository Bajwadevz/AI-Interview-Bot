# local_server.py
# Minimal FastAPI backend that implements Module-3 API surface for local testing.
# Run with: uvicorn local_server:app --reload --port 8000

import uuid, json, os, time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# try to import the followup logic from orchestrator_lambda (if present)
try:
    from orchestrator_lambda.followup import choose_next_question
except Exception:
    def choose_next_question(session, current_question, last_response):
        return {"questionId": "q-placeholder", "text": "Describe your experience with backend systems."}

DATA_FILE = "module3_data.json"

app = FastAPI(title="Module-3 Local Backend (test stub)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_sessions = {}
_transcripts = {}
_questions = [
    {"questionId": "q-1", "text": "Explain difference between TCP and UDP.", "domain": "backend", "difficulty": 2},
    {"questionId": "q-2", "text": "What is a REST API? Explain idempotency.", "domain": "backend", "difficulty": 2},
    {"questionId": "q-3", "text": "Describe a time you designed a retry mechanism.", "domain": "backend", "difficulty": 3}
]

def now_ts():
    return str(int(time.time()*1000))

def persist():
    try:
        obj = {"sessions": _sessions, "transcripts": _transcripts}
        with open(DATA_FILE, "w") as f:
            json.dump(obj, f, indent=2)
    except Exception as e:
        print("persist error", e)

def load_persist():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                obj = json.load(f)
            _sessions.update(obj.get("sessions", {}))
            _transcripts.update(obj.get("transcripts", {}))
        except Exception as e:
            print("load persist error", e)

load_persist()

class StartReq(BaseModel):
    userId: Optional[str] = "student"
    domain: Optional[str] = "backend"
    difficulty: Optional[int] = 2

class UtterReq(BaseModel):
    text: Optional[str] = None
    audioS3Key: Optional[str] = None

class FeedbackReq(BaseModel):
    rating: Optional[int] = None
    notes: Optional[str] = None

@app.post("/v1/conversation/start")
async def start_conversation(req: StartReq):
    sessionId = str(uuid.uuid4())
    q = next((x for x in _questions if x.get("domain") == req.domain and int(x.get("difficulty",1)) == req.difficulty), None)
    if not q:
        q = _questions[0]
    session = {
        "sessionId": sessionId,
        "userId": req.userId,
        "domain": req.domain,
        "currentQuestionId": q.get("questionId"),
        "state": {"clarityAttempts": 0, "recent_scores": []},
        "startedAt": datetime.utcnow().isoformat(),
        "lastUpdatedAt": datetime.utcnow().isoformat(),
        "status": "active"
    }
    _sessions[sessionId] = session
    _transcripts[sessionId] = [{"ts": now_ts(), "speaker": "bot", "text": q.get("text")}]
    persist()
    return {"sessionId": sessionId, "question": q}

@app.post("/v1/conversation/{sessionId}/utter")
async def utter(sessionId: str, req: UtterReq):
    if sessionId not in _sessions:
        raise HTTPException(status_code=404, detail="session not found")
    text = req.text or ""
    if req.audioS3Key and not text:
        text = f"(audio message - key: {req.audioS3Key})"
    _transcripts.setdefault(sessionId, []).append({"ts": now_ts(), "speaker": "user", "text": text})
    session = _sessions[sessionId]
    current_q = next((q for q in _questions if q.get("questionId") == session.get("currentQuestionId")), None)
    next_q = choose_next_question(session, current_q, {"text": text, "confidence": None, "keyPhrases": []})
    session["currentQuestionId"] = next_q.get("questionId")
    session["lastUpdatedAt"] = datetime.utcnow().isoformat()
    _transcripts[sessionId].append({"ts": now_ts(), "speaker": "bot", "text": next_q.get("text")})
    persist()
    return {"lex": {"intent": None, "confidence": None, "messages": []}, "nextQuestion": next_q, "sessionState": session.get("state", {})}

@app.post("/v1/conversation/{sessionId}/end")
async def end_session(sessionId: str):
    if sessionId not in _sessions:
        raise HTTPException(status_code=404, detail="session not found")
    _sessions[sessionId]["status"] = "finished"
    _sessions[sessionId]["lastUpdatedAt"] = datetime.utcnow().isoformat()
    persist()
    return {"message": "session ended"}

@app.get("/v1/conversation/{sessionId}/transcript")
async def get_transcript(sessionId: str):
    if sessionId not in _sessions:
        raise HTTPException(status_code=404, detail="session not found")
    return {"sessionId": sessionId, "transcript": _transcripts.get(sessionId, [])}

@app.post("/v1/conversation/{sessionId}/feedback")
async def post_feedback(sessionId: str, req: FeedbackReq):
    if sessionId not in _sessions:
        raise HTTPException(status_code=404, detail="session not found")
    s = _sessions[sessionId]
    s.setdefault("feedback", []).append({"ts": now_ts(), "rating": req.rating, "notes": req.notes})
    persist()
    return {"message": "feedback saved"}

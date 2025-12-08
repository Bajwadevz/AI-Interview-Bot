# local_server.py
# Improved local orchestrator stub for Module-3 with end-session summary.
# Run with: uvicorn local_server:app --reload --port 8000

import uuid, json, os, time, hashlib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

DATA_FILE = "module3_data.json"
CONFIDENCE_CLARIFY_THRESHOLD = 0.40  # below this -> ask for clarification
MAX_CLARITY_ATTEMPTS = 2

app = FastAPI(title="Module-3 Local Orchestrator (improved)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_sessions = {}
_transcripts = {}

_QUESTIONS = [
    {"questionId": "q-1", "text": "Explain difference between TCP and UDP.", "domain": "backend", "difficulty": 2},
    {"questionId": "q-2", "text": "What is a REST API? Explain idempotency.", "domain": "backend", "difficulty": 2},
    {"questionId": "q-3", "text": "Describe a retry mechanism you designed.", "domain": "backend", "difficulty": 3},
    {"questionId": "q-4", "text": "How do you design a scalable API?", "domain": "backend", "difficulty": 3},
    {"questionId": "q-5", "text": "What is eventual consistency? Give an example.", "domain": "backend", "difficulty": 3}
]

def now_ts():
    return str(int(time.time()*1000))

def persist():
    try:
        obj = {"sessions": _sessions, "transcripts": _transcripts}
        with open(DATA_FILE, "w") as f:
            json.dump(obj, f, indent=2)
    except Exception:
        pass

def load_persist():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                obj = json.load(f)
            _sessions.update(obj.get("sessions", {}))
            _transcripts.update(obj.get("transcripts", {}))
        except Exception:
            pass

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

def pseudo_confidence(text: str) -> float:
    if not text:
        return 0.2
    h = hashlib.sha256(text.encode('utf-8')).hexdigest()
    val = int(h[:8], 16)
    norm = (val % 10000) / 10000.0
    return 0.2 + norm * (0.75)

def pick_next_by_rotation(current_qid: Optional[str]):
    if not current_qid:
        return _QUESTIONS[0]
    ids = [q["questionId"] for q in _QUESTIONS]
    try:
        idx = ids.index(current_qid)
        return _QUESTIONS[(idx + 1) % len(_QUESTIONS)]
    except ValueError:
        return _QUESTIONS[0]

def make_clarify_prompt(current_question, attempts):
    base = [
        "Could you clarify what part of your approach you focused on?",
        "I didn't fully catch that — can you give a short example or mention specific technologies?",
        "Please provide one specific detail about your implementation (e.g., library, pattern, or metric)."
    ]
    idx = min(attempts, len(base)-1)
    qtxt = (current_question or {}).get("text", "")
    return f"{base[idx]} (Context: {qtxt})"

@app.post("/v1/conversation/start")
async def start_conversation(req: StartReq):
    sessionId = str(uuid.uuid4())
    q = next((x for x in _QUESTIONS if x.get("domain") == req.domain and int(x.get("difficulty",1)) == req.difficulty), None)
    if not q:
        q = _QUESTIONS[0]
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
    return {"sessionId": sessionId, "question": q, "sessionState": session["state"]}

@app.post("/v1/conversation/{sessionId}/utter")
async def utter(sessionId: str, req: UtterReq):
    if sessionId not in _sessions:
        raise HTTPException(status_code=404, detail="session not found")
    text = (req.text or "").strip()
    if req.audioS3Key and not text:
        text = f"(audio message - key: {req.audioS3Key})"
    _transcripts.setdefault(sessionId, []).append({"ts": now_ts(), "speaker": "user", "text": text})
    session = _sessions[sessionId]
    current_q = next((q for q in _QUESTIONS if q.get("questionId") == session.get("currentQuestionId")), None)
    conf = pseudo_confidence(text)
    session["state"].setdefault("recent_scores", []).append(conf)
    if len(session["state"]["recent_scores"])>5:
        session["state"]["recent_scores"] = session["state"]["recent_scores"][-5:]
    clarify = False
    if conf < CONFIDENCE_CLARIFY_THRESHOLD and session["state"].get("clarityAttempts",0) < MAX_CLARITY_ATTEMPTS:
        clarify = True
        session["state"]["clarityAttempts"] = session["state"].get("clarityAttempts",0) + 1
        bot_text = make_clarify_prompt(current_q, session["state"]["clarityAttempts"]-1)
        next_q = {"questionId": f"clarify-{session['state']['clarityAttempts']}", "text": bot_text}
    else:
        session["state"]["clarityAttempts"] = 0
        next_q = pick_next_by_rotation(current_q.get("questionId") if current_q else None)
        bot_text = next_q.get("text")
    _transcripts.setdefault(sessionId, []).append({"ts": now_ts(), "speaker": "bot", "text": bot_text})
    session["currentQuestionId"] = next_q.get("questionId")
    session["lastUpdatedAt"] = datetime.utcnow().isoformat()
    persist()
    return {
        "lex": {"intent": None, "confidence": conf, "messages": []},
        "nextQuestion": next_q,
        "sessionState": session["state"],
        "clarify": clarify
    }

@app.post("/v1/conversation/{sessionId}/end")
async def end_session(sessionId: str):
    if sessionId not in _sessions:
        raise HTTPException(status_code=404, detail="session not found")
    s = _sessions[sessionId]
    s["status"] = "finished"
    s["lastUpdatedAt"] = datetime.utcnow().isoformat()
    # compute summary from recent_scores
    recent = s.get("state", {}).get("recent_scores", [])
    avg = sum(recent)/len(recent) if recent else None
    count = len(_transcripts.get(sessionId, []))
    summary = {
        "sessionId": sessionId,
        "average_confidence": avg,
        "turns": count,
        "startedAt": s.get("startedAt"),
        "finishedAt": datetime.utcnow().isoformat()
    }
    persist()
    return {"message": "session ended", "summary": summary}

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

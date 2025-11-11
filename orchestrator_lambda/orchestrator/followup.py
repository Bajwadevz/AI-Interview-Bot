# lambda/orchestrator/followup.py
import boto3
import os

dynamodb = boto3.resource("dynamodb")
QUESTION_TABLE = os.environ.get("QUESTION_BANK_TABLE", "QuestionBank")
question_table = dynamodb.Table(QUESTION_TABLE)

CONFIDENCE_THRESHOLD = 0.55

def load_question_by_id(qid):
    if not qid:
        return None
    try:
        resp = question_table.get_item(Key={"questionId": qid})
        return resp.get("Item")
    except Exception:
        return None

def choose_next_question(session, current_question, last_response):
    state = session.get("state", {}) or {}
    clarity_attempts = state.get("clarityAttempts", 0)

    conf = None
    if last_response and last_response.get("confidence") is not None:
        try:
            conf = float(last_response.get("confidence"))
        except Exception:
            conf = None

    rules = (current_question or {}).get("followUpRules") or {}

    if conf is not None and conf < CONFIDENCE_THRESHOLD:
        if clarity_attempts < 1 and rules.get("clarify"):
            state['clarityAttempts'] = clarity_attempts + 1
            session['state'] = state
            return load_question_by_id(rules.get("clarify"))
        elif rules.get("simplify"):
            return load_question_by_id(rules.get("simplify"))
        else:
            return sample_next_by_domain(session.get("domain"))

    expected = (current_question or {}).get("expectedKeywords") or []
    text = last_response.get("text","") if last_response else ""
    missing = []
    for k in expected:
        if k.lower() not in text.lower():
            missing.append(k)
    if missing and rules.get("hint"):
        return load_question_by_id(rules.get("hint"))

    recent_scores = state.get("recent_scores", [])
    if recent_scores:
        try:
            avg = sum(recent_scores)/len(recent_scores)
            if avg > 0.8:
                return sample_question_by_relative_difficulty(session, +1)
            elif avg < 0.4:
                return sample_question_by_relative_difficulty(session, -1)
        except Exception:
            pass

    return sample_next_by_domain(session.get("domain"))

def sample_question_by_relative_difficulty(session, delta):
    domain = session.get("domain", "general")
    try:
        resp = question_table.scan(Limit=50)
        items = resp.get("Items", [])
    except Exception:
        items = []
    last_qid = session.get("currentQuestionId")
    last_q = None
    for it in items:
        if it.get("questionId") == last_qid:
            last_q = it
            break
    last_diff = int(last_q.get("difficulty",2)) if last_q else 2
    target = max(1, last_diff + delta)
    candidates = [i for i in items if i.get("domain")==domain and int(i.get("difficulty",1))==target]
    if candidates:
        return candidates[0]
    return sample_next_by_domain(domain)

def sample_next_by_domain(domain):
    try:
        resp = question_table.scan(Limit=50)
        items = resp.get("Items", [])
    except Exception:
        items = []
    for it in items:
        if it.get("domain") == domain:
            return it
    return items[0] if items else None

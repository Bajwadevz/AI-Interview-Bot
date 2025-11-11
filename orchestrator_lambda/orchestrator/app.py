# lambda/orchestrator/app.py
import os
import json
import time
import uuid
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from followup import choose_next_question, load_question_by_id

# AWS clients (will attempt to connect if credentials present)
dynamodb = boto3.resource("dynamodb")
lex = boto3.client("lexv2-runtime")
s3 = boto3.client("s3")
comprehend = boto3.client("comprehend")

CONV_TABLE = os.environ.get("CONVERSATION_TABLE", "ConversationSessions")
TRANS_TABLE = os.environ.get("TRANSCRIPTS_TABLE", "Transcripts")
QUESTION_TABLE = os.environ.get("QUESTION_BANK_TABLE", "QuestionBank")
MEDIA_BUCKET = os.environ.get("MEDIA_BUCKET")
LEX_BOT_ID = os.environ.get("LEX_BOT_ID")
LEX_BOT_ALIAS_ID = os.environ.get("LEX_BOT_ALIAS_ID")
LEX_LOCALE = os.environ.get("LEX_BOT_LOCALE_ID", "en_US")

conv_table = dynamodb.Table(CONV_TABLE)
trans_table = dynamodb.Table(TRANS_TABLE)
question_table = dynamodb.Table(QUESTION_TABLE)

def _now_iso():
    return datetime.utcnow().isoformat()

def lambda_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    method = event.get("httpMethod")
    path = event.get("path", "")
    body = event.get("body")
    if body:
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}
    else:
        payload = {}

    # route
    if path.endswith("/start") and method == "POST":
        return start_session(payload)
    if "/v1/conversation/" in path and method == "POST":
        parts = path.split("/")
        try:
            session_idx = parts.index("conversation") + 1
            session_id = parts[session_idx]
        except ValueError:
            return lambda_response(400, {"message": "invalid path"})
        if path.endswith("/utter"):
            return handle_utter(session_id, payload)
        elif path.endswith("/end"):
            return end_session(session_id, payload)
    return lambda_response(404, {"message": "not found"})

def start_session(payload):
    userId = payload.get("userId", "anon")
    domain = payload.get("domain", "general")
    try:
        difficulty = int(payload.get("difficulty", 2))
    except Exception:
        difficulty = 2
    sessionId = str(uuid.uuid4())

    q = sample_question_by_difficulty(domain, difficulty)
    now = _now_iso()
    session_item = {
        "sessionId": sessionId,
        "userId": userId,
        "domain": domain,
        "currentQuestionId": q.get("questionId") if q else None,
        "state": {"clarityAttempts": 0, "recent_scores": []},
        "startedAt": now,
        "lastUpdatedAt": now,
        "status": "active"
    }
    try:
        conv_table.put_item(Item=session_item)
    except Exception as e:
        print("DynamoDB put_item failed:", e)

    ts = str(int(time.time()*1000))
    try:
        trans_table.put_item(Item={
            "sessionId": sessionId,
            "ts": ts,
            "speaker": "bot",
            "text": q.get("text") if q else "No question found",
            "intent": None,
            "confidence": None,
            "metadata": {}
        })
    except Exception:
        pass

    return lambda_response(200, {"sessionId": sessionId, "question": q})

def handle_utter(sessionId, payload):
    text = payload.get("text")
    audio_key = payload.get("audioS3Key")
    if audio_key and not text:
        text = transcribe_from_s3(audio_key)

    if not text:
        return lambda_response(400, {"message": "No input text provided"})

    # load session
    session = None
    try:
        session = conv_table.get_item(Key={"sessionId": sessionId}).get("Item")
    except Exception:
        session = None

    if not session:
        session = {"sessionId": sessionId, "domain": "general", "state": {"clarityAttempts": 0, "recent_scores": []}, "currentQuestionId": None}

    lex_resp = call_lex(text, sessionId)
    intent = None
    confidence = None
    messages = []
    if lex_resp:
        interpretation = lex_resp.get("interpretations", [])
        if interpretation:
            top = interpretation[0]
            intent = top.get("intent", {}).get("name")
            confidence = top.get("nluConfidence", {}).get("score")
            messages = [m.get("content") for m in lex_resp.get("messages",[])] if lex_resp.get("messages") else []

    sentiment = None
    key_phrases = []
    try:
        comp = comprehend.detect_sentiment(Text=text, LanguageCode="en")
        sentiment = comp.get("Sentiment")
        kp = comprehend.detect_key_phrases(Text=text, LanguageCode="en")
        key_phrases = [k['Text'] for k in kp.get('KeyPhrases',[])]
    except Exception:
        sentiment = None
        key_phrases = []

    ts = str(int(time.time()*1000))
    try:
        trans_table.put_item(Item={
            "sessionId": sessionId,
            "ts": ts,
            "speaker": "user",
            "text": text,
            "intent": intent,
            "confidence": confidence,
            "metadata": {"sentiment": sentiment, "keyPhrases": key_phrases}
        })
    except Exception:
        pass

    current_qid = session.get("currentQuestionId")
    current_question = load_question_by_id(current_qid)
    next_q = choose_next_question(session, current_question, {"text": text, "confidence": confidence, "keyPhrases": key_phrases})

    session["currentQuestionId"] = next_q.get("questionId") if next_q else None
    session["lastUpdatedAt"] = _now_iso()
    try:
        conv_table.put_item(Item=session)
    except Exception:
        pass

    bot_ts = str(int(time.time()*1000)+1)
    bot_text = next_q.get("text") if next_q else "Thank you. Session ended."
    try:
        trans_table.put_item(Item={
            "sessionId": sessionId,
            "ts": bot_ts,
            "speaker": "bot",
            "text": bot_text,
            "intent": None,
            "confidence": None,
            "metadata": {}
        })
    except Exception:
        pass

    response = {
        "lex": {"intent": intent, "confidence": confidence, "messages": messages},
        "nextQuestion": next_q,
        "sessionState": session.get("state", {})
    }
    return lambda_response(200, response)

def end_session(sessionId, payload):
    try:
        conv_table.update_item(
            Key={"sessionId": sessionId},
            UpdateExpression="SET #s = :st, lastUpdatedAt = :t",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":st": "finished", ":t": _now_iso()}
        )
    except Exception:
        pass
    return lambda_response(200, {"message": "session ended"})

def sample_question_by_difficulty(domain, difficulty):
    try:
        resp = question_table.scan(Limit=50)
        items = resp.get("Items", [])
    except Exception:
        items = []
    candidates = [i for i in items if i.get("domain") == domain and int(i.get("difficulty",1)) == difficulty]
    if not candidates:
        candidates = [i for i in items if i.get("domain") == domain]
    if not candidates:
        return None
    return candidates[0]

def call_lex(text, sessionId):
    if not (LEX_BOT_ID and LEX_BOT_ALIAS_ID):
        print("LEX env not set; skipping lex call")
        return None
    try:
        resp = lex.recognize_text(
            botId=LEX_BOT_ID,
            botAliasId=LEX_BOT_ALIAS_ID,
            localeId=LEX_LOCALE,
            sessionId=sessionId,
            text=text
        )
        return resp
    except ClientError as e:
        print("Lex error:", e)
        return None

def transcribe_from_s3(s3_key):
    job_name = f"transcribe-{int(time.time())}"
    job_uri = f"s3://{MEDIA_BUCKET}/{s3_key}"
    transcribe = boto3.client("transcribe")
    try:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": job_uri},
            MediaFormat=s3_key.split(".")[-1],
            LanguageCode="en-US",
            OutputBucketName=MEDIA_BUCKET
        )
        while True:
            job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            status = job['TranscriptionJob']['TranscriptionJobStatus']
            if status in ("COMPLETED", "FAILED"):
                break
            time.sleep(1)
        if status == "COMPLETED":
            return ""  # production: download and parse transcript JSON
    except Exception as e:
        print("Transcribe failed", e)
    return ""

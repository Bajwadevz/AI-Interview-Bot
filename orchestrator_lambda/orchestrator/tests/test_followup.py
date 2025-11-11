# unit test for followup logic
import pytest
import followup

def test_low_confidence_clarify(monkeypatch):
    session = {"domain":"backend", "state":{"clarityAttempts":0}, "currentQuestionId":"q-backend-1"}
    current_question = {
        "questionId":"q-backend-1",
        "followUpRules": {"clarify":"q-backend-1-clarify", "simplify":"q-backend-1-simplify"},
        "expectedKeywords":["tcp"]
    }
    last_response = {"text":"I think it's about speed", "confidence":0.4, "keyPhrases": []}

    def fake_load(qid):
        if qid=="q-backend-1-clarify":
            return {"questionId":"q-backend-1-clarify","text":"Clarify?"}
        return None

    monkeypatch.setattr(followup, "load_question_by_id", fake_load)
    next_q = followup.choose_next_question(session, current_question, last_response)
    assert next_q["questionId"] == "q-backend-1-clarify"

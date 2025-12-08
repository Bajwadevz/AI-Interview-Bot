def choose_next_question(session, current_question, last_response):
    # simple follow-up: rotate through some static questions
    base = [
        {"questionId": "q-1", "text": "Explain difference between TCP and UDP."},
        {"questionId": "q-2", "text": "What is a REST API and why idempotency matters?"},
        {"questionId": "q-3", "text": "Describe a retry mechanism you designed."}
    ]
    # pick next by last questionId or default to first
    last = (current_question or {}).get("questionId")
    if not last:
        return base[0]
    ids = [q["questionId"] for q in base]
    try:
        idx = ids.index(last)
        return base[(idx+1) % len(base)]
    except ValueError:
        return base[0]

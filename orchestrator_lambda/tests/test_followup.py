from followup import choose_next_question
def test_choose():
    r = choose_next_question({}, None, {})
    assert "questionId" in r

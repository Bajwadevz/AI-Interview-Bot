# lambda/orchestrator/question_seeder.py
import boto3
import os

QUESTION_TABLE = os.environ.get("QUESTION_BANK_TABLE", "QuestionBank")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(QUESTION_TABLE)

SAMPLE_QUESTIONS = [
    {
        "questionId": "q-backend-1",
        "domain": "backend",
        "text": "Explain the difference between TCP and UDP.",
        "type": "open",
        "difficulty": 2,
        "expectedKeywords": ["tcp", "udp", "connection", "reliability"],
        "followUpRules": {"clarify": "q-backend-1-clarify", "simplify": "q-backend-1-simplify", "hint": "q-backend-1-hint"},
        "scoreWeight": 1.0
    },
    {
        "questionId": "q-backend-1-clarify",
        "domain": "backend",
        "text": "Do you mean reliability or speed when you say UDP?",
        "type": "followup",
        "difficulty": 1,
        "expectedKeywords": [],
        "followUpRules": {},
        "scoreWeight": 0.2
    },
    {
        "questionId": "q-backend-1-simplify",
        "domain": "backend",
        "text": "Which protocol would you pick if you need reliable delivery? TCP or UDP?",
        "type": "followup",
        "difficulty": 1,
        "expectedKeywords": ["tcp"],
        "followUpRules": {},
        "scoreWeight": 0.2
    },
    {
        "questionId": "q-backend-1-hint",
        "domain": "backend",
        "text": "Hint: One provides connection-oriented communication, the other is connectionless.",
        "type": "hint",
        "difficulty": 1,
        "expectedKeywords": ["connection-oriented"],
        "followUpRules": {},
        "scoreWeight": 0.0
    }
]

def seed():
    for q in SAMPLE_QUESTIONS:
        print("Putting", q['questionId'])
        table.put_item(Item=q)

if __name__ == "__main__":
    print("Seeding table:", QUESTION_TABLE)
    seed()
    print("Done.")

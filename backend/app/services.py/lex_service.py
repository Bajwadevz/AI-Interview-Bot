import boto3
from app.core.config import settings

class LexService:
    def __init__(self):
        self.client = boto3.client('lexv2-runtime', region_name=settings.AWS_REGION)
        self.bot_id = None  # You'll need to set this based on your Lex bot
        self.bot_alias_id = None  # You'll need to set this based on your Lex bot alias
    
    def recognize_text(self, session_id, text):
        try:
            response = self.client.recognize_text(
                botId=self.bot_id,
                botAliasId=self.bot_alias_id,
                localeId=settings.LEX_LOCALE_ID,
                sessionId=session_id,
                text=text
            )
            return response
        except Exception as e:
            raise Exception(f"Error communicating with Lex: {str(e)}")
    
    def start_conversation(self, session_id, initial_message=""):
        try:
            if initial_message:
                return self.recognize_text(session_id, initial_message)
            else:
                # Return a welcome message or initial question
                return {
                    "messages": [{
                        "content": "Welcome to your interview! Let's begin with your first question.",
                        "contentType": "PlainText"
                    }]
                }
        except Exception as e:
            raise Exception(f"Error starting conversation: {str(e)}")
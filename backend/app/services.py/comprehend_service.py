import boto3
from app.core.config import settings

class ComprehendService:
    def __init__(self):
        self.client = boto3.client('comprehend', region_name=settings.AWS_REGION)
    
    def detect_sentiment(self, text):
        try:
            response = self.client.detect_sentiment(
                Text=text,
                LanguageCode=settings.COMPREHEND_LANGUAGE_CODE
            )
            return response
        except Exception as e:
            raise Exception(f"Error detecting sentiment: {str(e)}")
    
    def detect_key_phrases(self, text):
        try:
            response = self.client.detect_key_phrases(
                Text=text,
                LanguageCode=settings.COMPREHEND_LANGUAGE_CODE
            )
            return response
        except Exception as e:
            raise Exception(f"Error detecting key phrases: {str(e)}")
    
    def analyze_text(self, text):
        try:
            sentiment = self.detect_sentiment(text)
            key_phrases = self.detect_key_phrases(text)
            
            return {
                "sentiment": sentiment,
                "key_phrases": key_phrases
            }
        except Exception as e:
            raise Exception(f"Error analyzing text: {str(e)}")
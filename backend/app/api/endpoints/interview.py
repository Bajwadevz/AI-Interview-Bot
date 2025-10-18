from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.core.security import security
from app.services.lex_service import LexService
from app.services.comprehend_service import ComprehendService

router = APIRouter()

@router.post("/start")
async def start_interview(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Start a new interview session
    lex_service = LexService()
    session_id = "some_unique_session_id"  # Generate a unique session ID
    response = lex_service.start_conversation(session_id)
    return response

@router.post("/response")
async def submit_response(response: str, session_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Process user response
    lex_service = LexService()
    comprehend_service = ComprehendService()
    
    # Get next question from Lex
    lex_response = lex_service.recognize_text(session_id, response)
    
    # Analyze response with Comprehend
    analysis = comprehend_service.analyze_text(response)
    
    return {
        "lex_response": lex_response,
        "analysis": analysis
    }
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    cognito_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(String, default="candidate")  # candidate, interviewer, admin
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    domain = Column(String)
    difficulty = Column(String)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(String, default="in-progress")  # in-progress, completed
    overall_score = Column(Float)
    feedback = Column(JSON)

class QuestionResponse(Base):
    __tablename__ = "question_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, index=True)
    question_text = Column(String)
    user_response = Column(String)
    score = Column(Float)
    feedback = Column(String)
    analysis = Column(JSON)  # NLP analysis results
    timestamp = Column(DateTime, default=datetime.utcnow)
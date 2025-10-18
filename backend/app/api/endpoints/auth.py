from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.services.cognito_service import CognitoService
from app.core.security import security, create_access_token
from app.core.config import settings

router = APIRouter()

class SignUpRequest(BaseModel):
    username: str
    password: str
    email: str
    full_name: str

class ConfirmSignUpRequest(BaseModel):
    username: str
    confirmation_code: str

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/signup")
async def sign_up(request: SignUpRequest):
    cognito = CognitoService()
    
    user_attributes = [
        {'Name': 'email', 'Value': request.email},
        {'Name': 'name', 'Value': request.full_name}
    ]
    
    try:
        response = cognito.sign_up(
            request.username, 
            request.password, 
            request.email, 
            user_attributes
        )
        return {"message": "User created successfully", "user_sub": response['UserSub']}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/confirm")
async def confirm_sign_up(request: ConfirmSignUpRequest):
    cognito = CognitoService()
    
    try:
        response = cognito.confirm_sign_up(request.username, request.confirmation_code)
        return {"message": "User confirmed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(request: LoginRequest):
    cognito = CognitoService()
    
    try:
        response = cognito.initiate_auth(request.username, request.password)
        access_token = response['AuthenticationResult']['AccessToken']
        
        # Get user info
        user_info = cognito.get_user(access_token)
        user_attributes = {attr['Name']: attr['Value'] for attr in user_info['UserAttributes']}
        
        # Create JWT token for our API
        jwt_token = create_access_token(
            data={"sub": user_attributes['email'], "username": request.username}
        )
        
        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": {
                "email": user_attributes['email'],
                "username": request.username,
                "full_name": user_attributes.get('name', '')
            }
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # This endpoint is protected and requires a valid JWT token
    return {"message": "This is a protected endpoint", "user": credentials}
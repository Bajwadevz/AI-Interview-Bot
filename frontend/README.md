# Frontend code here
# How They Work Together: A Step-by-Step Flow

1. User loads localhost:3000/signup (Next.js frontend)

2. User fills form and clicks "Create account"

3. Frontend sends POST request to http://localhost:8000/auth/signup with user data.

4. Backend (FastAPI) receives request, processes it through the sign_up function in auth.py.

5. Backend uses CognitoService to create the user in AWS Cognito.

6. Backend sends response back to the frontend: {"message": "User created successfully", "user_sub": "..."}

7. Frontend displays success message and prompts user to check email for confirmation.

8. After confirmation, user goes to login page, fills in their username and password.

9. Frontend sends POST request to http://localhost:8000/auth/login.

10. Backend uses CognitoService to validate credentials with AWS Cognito.

11. Backend generates a JWT token and sends it to the frontend: { "access_token": "xyz", "token_type": "bearer", "user": {...} }.

12. Frontend stores the token and uses it for all future API requests (via the Authorization: Bearer <token> header).s
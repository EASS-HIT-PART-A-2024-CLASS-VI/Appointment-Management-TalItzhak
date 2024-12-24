from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from app.security import SECRET_KEY, ALGORITHM
from app.database import SessionLocal
import jwt

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Contains user data like username and role
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

# Function to check the role of the user
def check_user_role(required_role: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role != required_role:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user
    return role_checker
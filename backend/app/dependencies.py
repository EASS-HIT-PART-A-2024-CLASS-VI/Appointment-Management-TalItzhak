from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from app.security import SECRET_KEY, ALGORITHM
from app.database import SessionLocal
import jwt
from jwt.exceptions import InvalidTokenError
from app.models import User
from sqlalchemy.orm import Session
from jwt import PyJWTError


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
        user_data = payload.get("sub")
        role = payload.get("role")
        if not user_data or not role:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        print(f"Decoded JWT: {payload}") 
        return payload  
    except PyJWTError as e:
        print(f"JWT Error: {str(e)}")  
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    
def check_user_role(required_role: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role != required_role:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user
    return role_checker

def business_owner_required(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "business_owner":
        raise HTTPException(status_code=403, detail="Access forbidden: Only business owners are allowed.")
    return current_user
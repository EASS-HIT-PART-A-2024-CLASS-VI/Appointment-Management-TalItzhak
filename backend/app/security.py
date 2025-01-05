from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key_for_development")

ALGORITHM = "HS256"  # האלגוריתם להצפנה

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# הצפנת סיסמא
def get_password_hash(password: str):
    return pwd_context.hash(password)

# אימות סיסמא
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# יצירת JWT Token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
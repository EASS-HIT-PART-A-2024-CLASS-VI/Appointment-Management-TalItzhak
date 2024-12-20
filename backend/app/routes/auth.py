from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserLogin
from app.models import User
from app.security import get_password_hash, verify_password, create_access_token
from app.dependencies import get_db
from datetime import timedelta

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user": new_user.username}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": db_user.username, "role": db_user.role}, expires_delta=token_expires)
    return {"access_token": access_token, "token_type": "bearer"}



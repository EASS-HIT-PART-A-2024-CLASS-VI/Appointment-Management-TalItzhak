from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserLogin
from app.models import User
from app.security import get_password_hash, verify_password, create_access_token
from app.dependencies import get_db
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status, Form
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.phone == user.phone)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or phone already registered")

    if user.role == "business_owner" and not user.business_name:
        raise HTTPException(status_code=400, detail="Business name is required for business owners")

    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        phone=user.phone,
        password_hash=get_password_hash(user.password),
        role=user.role,
        business_name=user.business_name if user.role == "business_owner" else None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user": new_user.username}


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
        
    access_token = create_access_token(
        data={"sub": db_user.username, "role": db_user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}
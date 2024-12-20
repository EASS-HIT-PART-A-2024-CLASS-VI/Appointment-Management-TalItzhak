from datetime import datetime, time
from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, EmailStr
from typing import Optional

# סכמת הרשמה
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str  # "business_owner" או "customer"

# סכמת התחברות
class UserLogin(BaseModel):
    username: str
    password: str

# סכמת החזרת משתמש
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        orm_mode = True


class AppointmentCreate(BaseModel):
    date: datetime
    start_time: time  # Hours and minutes for start time
    duration: int  # Duration in minutes
    title: str
    customer_name: str
    customer_phone: str
    type: str
    cost: int
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    date: Optional[datetime] = None
    start_time: Optional[time] = None
    duration: Optional[int] = None  # Add duration here
    title: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    type: Optional[str] = None
    cost: Optional[int] = None
    notes: Optional[str] = None

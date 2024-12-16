from datetime import datetime, time
from pydantic import BaseModel
from typing import Optional

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

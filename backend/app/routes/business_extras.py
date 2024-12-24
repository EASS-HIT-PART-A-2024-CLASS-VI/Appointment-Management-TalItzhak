from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.schemas import AppointmentCreate, AppointmentUpdate, UserResponse
from app.models import appointments, User
from app.utils import search_appointment_by_phone_and_name
from app.dependencies import get_db, check_user_role

router = APIRouter()

# Business owners only access
business_owner_required = check_user_role("business_owner")

@router.get("/appointments/{appointment_id}", dependencies=[Depends(business_owner_required)])
def get_appointment_details(appointment_id: int):
    if appointment_id not in appointments:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appointment = appointments[appointment_id]
    return appointment

@router.get("/appointments", dependencies=[Depends(business_owner_required)])
def list_appointments(title: Optional[str] = None):
    if title:
        return {k: v for k, v in appointments.items() if v["title"] == title}
    return appointments

@router.get("/appointments/search/{phone}/{name}", dependencies=[Depends(business_owner_required)])
def search_appointment(phone: str, name: str):
    return search_appointment_by_phone_and_name(phone, name, appointments)

@router.get("/appointments/stats/{date}", dependencies=[Depends(business_owner_required)])
def get_appointments_stats(date: str):
    try:
        target_date = datetime.strptime(date, "%m-%d-%Y").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Please use MM-DD-YYYY format."
        )

    matching_appointments = [
        v for v in appointments.values()
        if isinstance(v.get("date"), str) and datetime.fromisoformat(v["date"].replace("Z", "+00:00")).date() == target_date
    ]

    if not matching_appointments:
        raise HTTPException(
            status_code=404,
            detail="No appointments found for the given date."
        )

    titles = [appointment["title"] for appointment in matching_appointments]
    total_revenue = sum(appointment["cost"] for appointment in matching_appointments)

    return {
        "date": target_date.strftime("%m/%d/%Y"),
        "titles": titles,
        "total_revenue": total_revenue
    }

@router.get("/", response_model=List[UserResponse], dependencies=[Depends(business_owner_required)])
def get_users(role: str = None, db: Session = Depends(get_db)):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.all()
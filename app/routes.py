from fastapi import APIRouter, HTTPException
from app.schemas import AppointmentCreate, AppointmentUpdate
from app.models import appointments
from typing import Optional
from datetime import datetime, timedelta
import re

router = APIRouter()


def is_time_conflict(start_time: str, duration: int, date: str, exclude_id: Optional[int] = None) -> bool:
   
    new_start = datetime.strptime(f"{date}T{start_time}", "%Y-%m-%dT%H:%M")
    new_end = new_start + timedelta(minutes=duration)

    for appointment_id, appointment in appointments.items():
        if exclude_id and appointment_id == exclude_id:
            continue
        existing_date = appointment["date"][:10]  # Extract YYYY-MM-DD
        existing_start = datetime.strptime(f"{existing_date}T{appointment['start_time']}", "%Y-%m-%dT%H:%M")
        existing_end = existing_start + timedelta(minutes=appointment["duration"])

        if date == existing_date and not (new_end <= existing_start or new_start >= existing_end):
            return True

    return False

def normalize_phone(phone: str) -> str:
    """
    Normalizes a phone number by removing all non-digit characters.
    """
    return re.sub(r'\D', '', phone)


# Create Appointment
@router.post("/appointments")
def create_appointment(appointment: AppointmentCreate):
    appointment_id = len(appointments) + 1
    appointment_data = appointment.dict()
    appointment_data["date"] = appointment_data["date"].isoformat()
    appointment_data["start_time"] = appointment_data["start_time"].strftime("%H:%M")  # Format as HH:MM

    if is_time_conflict(
        start_time=appointment_data["start_time"],
        duration=appointment_data["duration"],
        date=appointment_data["date"][:10]
    ):
        raise HTTPException(
            status_code=400,
            detail="An appointment already exists during this time."
        )

    appointments[appointment_id] = appointment_data
    return {"message": "Appointment created successfully", "appointment_id": appointment_id}



# Get Appointment Details
@router.get("/appointments/{appointment_id}")
def get_appointment_details(appointment_id: int):
    if appointment_id not in appointments:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appointment = appointments[appointment_id]
    return appointment


# List Appointments
@router.get("/appointments")
def list_appointments(title: Optional[str] = None):
    if title:
        return {k: v for k, v in appointments.items() if v["title"] == title}
    return appointments



# Search Appointments
@router.get("/appointments/search/{phone}/{name}")
def search_appointment(phone: str, name: str):
    normalized_phone = normalize_phone(phone)
    matching_appointments = {
        k: v
        for k, v in appointments.items()
        if normalize_phone(v.get("customer_phone", "")) == normalized_phone and name.lower() in v.get("customer_name", "").lower()
    }

    if not matching_appointments:
        raise HTTPException(
            status_code=404, 
            detail="No appointment found matching the given phone and name."
        )

    return matching_appointments



@router.put("/appointments/{appointment_id}")
def update_appointment(appointment_id: int, update: AppointmentUpdate):
    if appointment_id not in appointments:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    current_appointment = appointments[appointment_id]
    update_data = update.dict(exclude_unset=True) 
    
    for key, value in update_data.items():
        if key == "date" and value is not None:
            update_data["date"] = value.isoformat()
        elif key == "start_time" and value is not None:
            update_data["start_time"] = value.strftime("%H:%M")
    
    current_appointment.update(update_data)
    
    if is_time_conflict(
        start_time=current_appointment["start_time"],
        duration=current_appointment["duration"],
        date=current_appointment["date"][:10],
        exclude_id=appointment_id  
    ):
        raise HTTPException(
            status_code=400,
            detail="An appointment already exists during this time."
        )
    
    appointments[appointment_id] = current_appointment
    return {"message": "Appointment updated successfully", "appointment_id": appointment_id}



# Delete Appointment
@router.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int):
    if appointment_id not in appointments:
        raise HTTPException(status_code=404, detail="Appointment not found")
    del appointments[appointment_id]
    return {"message": "Appointment deleted successfully"}


# Get Appointment Stats
@router.get("/appointments/stats/{date}")
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

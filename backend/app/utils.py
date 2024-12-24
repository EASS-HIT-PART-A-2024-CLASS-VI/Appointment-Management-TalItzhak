from fastapi import  HTTPException
from app.schemas import AppointmentCreate, AppointmentUpdate
from app.models import appointments
from typing import Optional
from datetime import datetime, timedelta
import re


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


def search_appointment_by_phone_and_name(phone: str, name: str, appointments: dict):
    """
    Search appointments by normalized phone and name.
    """
    normalized_phone = normalize_phone(phone)
    matching_appointments = {
        k: v
        for k, v in appointments.items()
        if normalize_phone(v.get("customer_phone", "")) == normalized_phone 
        and name.lower() in v.get("customer_name", "").lower()
    }

    if not matching_appointments:
        raise HTTPException(
            status_code=404, 
            detail="No appointment found matching the given phone and name."
        )

    return matching_appointments
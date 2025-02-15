from fastapi import HTTPException
from datetime import datetime, timedelta
import re
from sqlalchemy.orm import Session
from app.models import Appointment, Availability
from typing import Optional
from sqlalchemy import and_, extract, text

def is_time_conflict(
    start_time: str,
    duration: int,
    date: str,
    db: Session,
    owner_id: int,
    exclude_id: Optional[int] = None
) -> bool:
    """
    Check if there's a time conflict with existing appointments or if it's outside business hours.
    Returns True if there is a conflict or not available, False if the time slot is available.
    """
    try:
        print("\n=== TIME CONFLICT CHECK ===")
        
        check_date = datetime.strptime(date, "%Y-%m-%d")
        day_of_week = check_date.strftime("%A")
        print(f"Checking conflicts for date: {check_date.date()} ({day_of_week})")

        availability = db.query(Availability).filter(
            and_(
                Availability.owner_id == owner_id,
                Availability.day_of_week == day_of_week
            )
        ).all()

        if not availability:
            print(f"No business availability set for {day_of_week}")
            return True

        new_time = datetime.strptime(start_time, "%H:%M")
        new_start = datetime.combine(check_date.date(), new_time.time())
        new_end = new_start + timedelta(minutes=duration)

        print(f"\nNew appointment window:")
        print(f"Start: {new_start.strftime('%H:%M')}")
        print(f"End: {new_end.strftime('%H:%M')}")

        # Check if appointment fits within business hours
        is_within_hours = False
        for slot in availability:
            slot_start = datetime.combine(check_date.date(), slot.start_time)
            slot_end = datetime.combine(check_date.date(), slot.end_time)

            if slot_start <= new_start and new_end <= slot_end:
                is_within_hours = True
                break

        if not is_within_hours:
            print("Appointment is outside business hours")
            return True

        # Check for conflicts with existing appointments
        existing_appointments = db.query(Appointment).filter(
            text("DATE(date) = DATE(:check_date)")
        ).params(check_date=check_date).all()

        print(f"\nFound {len(existing_appointments)} existing appointments")
        for apt in existing_appointments:
            if exclude_id and apt.id == exclude_id:
                continue

            # Convert existing appointment to datetime
            existing_start = datetime.combine(check_date.date(), apt.start_time)
            existing_end = existing_start + timedelta(minutes=apt.duration)

            print(f"Checking appointment {apt.id}:")
            print(f"Start: {existing_start.strftime('%H:%M')}")
            print(f"End: {existing_end.strftime('%H:%M')}")

            # Check for overlap using datetime comparison
            if (new_start < existing_end and new_end > existing_start):
                print(f"CONFLICT DETECTED: Overlaps with appointment {apt.id}")
                return True

        print("No conflicts found")
        return False

    except Exception as e:
        print(f"Error in conflict checking: {str(e)}")
        return True

def normalize_phone(phone: str) -> str:

    return re.sub(r'\D', '', phone)

def search_appointment_by_phone_and_name(phone: str, name: str, appointments: dict):

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
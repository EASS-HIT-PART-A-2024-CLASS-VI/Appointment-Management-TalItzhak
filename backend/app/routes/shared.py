from fastapi import APIRouter, Depends, HTTPException
from app.schemas import AppointmentCreate, AppointmentUpdate, UserResponse
from app.models import appointments, Service
from app.utils import is_time_conflict
from app.dependencies import get_current_user
from app.models import Topic
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Appointment
from datetime import datetime, timedelta 
from sqlalchemy import and_
from app.models import Availability, Service
from typing import List
from app.schemas import AppointmentResponse
from app.models import User
from app.schemas import UserResponse
from sqlalchemy.sql import text


router = APIRouter()

@router.post("/appointments")
def create_appointment(
    appointment: AppointmentCreate,
    business_id: int,
    db: Session = Depends(get_db)
):
    print("\n=== CREATE APPOINTMENT DEBUG ===")
    print(f"Requested date: {appointment.date}")
    print(f"Requested time: {appointment.start_time}")

    # Get the service details
    service = db.query(Service).filter(
        Service.name == appointment.title,
        Service.owner_id == business_id
    ).first()

    if not service:
        available_services = db.query(Service).filter(
            Service.owner_id == business_id
        ).all()
        available_service_names = [s.name for s in available_services]
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Invalid service: '{appointment.title}'. Service must be one of the available services.",
                "available_services": available_service_names
            }
        )

    # Format appointment time for checking
    appointment_time = appointment.start_time.strftime("%H:%M")
    appointment_date = appointment.date.strftime("%Y-%m-%d")
    service_end_time = (datetime.combine(appointment.date.date(), appointment.start_time) 
                       + timedelta(minutes=service.duration)).time()

    # Check business availability and time conflicts
    has_conflict = is_time_conflict(
        start_time=appointment_time,
        duration=service.duration,
        date=appointment_date,
        db=db,
        owner_id=business_id
    )

    if has_conflict:
        # Check if it's due to no availability
        day_of_week = appointment.date.strftime("%A")
        availability = db.query(Availability).filter(
            and_(
                Availability.owner_id == business_id,
                Availability.day_of_week == day_of_week
            )
        ).first()

        if not availability:
            raise HTTPException(
                status_code=400,
                detail=f"The business is not available on {day_of_week}s. Please choose another day."
            )

        # Check for existing appointments at the same time
        existing_appointments = db.query(Appointment).filter(
            text("DATE(date) = DATE(:check_date)")
        ).params(check_date=appointment_date).all()

        for apt in existing_appointments:
            existing_start = datetime.combine(appointment.date.date(), apt.start_time)
            existing_end = existing_start + timedelta(minutes=apt.duration)
            new_start = datetime.combine(appointment.date.date(), appointment.start_time)
            new_end = new_start + timedelta(minutes=service.duration)

            if (new_start < existing_end and new_end > existing_start):
                raise HTTPException(
                    status_code=400,
                    detail="This time slot conflicts with an existing appointment. Please select a different time."
                )

        # If we get here, it means the time is outside business hours
        available_slots = db.query(Availability).filter(
            Availability.owner_id == business_id,
            Availability.day_of_week == day_of_week
        ).all()
        
        hours = [f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}"
                for slot in available_slots]
        
        raise HTTPException(
            status_code=400,
            detail={
                "message": "This time is outside business hours.",
                "business_hours": hours
            }
        )

    # Create new appointment
    new_appointment = Appointment(
        date=appointment.date.date(),
        start_time=appointment.start_time,
        duration=service.duration,
        title=service.name,
        customer_name=appointment.customer_name,
        customer_phone=appointment.customer_phone,
        type=service.name,
        cost=service.price,
        notes=None
    )

    try:
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        return {
            "message": f"Appointment created successfully for {appointment_time}-{service_end_time.strftime('%H:%M')}",
            "appointment": new_appointment
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the appointment: {str(e)}"
        )
    

@router.put("/appointments/{appointment_id}")  # Not /api/shared/appointments
def update_appointment(
    appointment_id: int,
    update: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Get the service to find the owner_id
    service = db.query(Service).filter(Service.name == appointment.type).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    update_data = update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        if value is not None:
            setattr(appointment, key, value)
    
    if is_time_conflict(
        start_time=appointment.start_time.strftime("%H:%M"),
        duration=appointment.duration,
        date=appointment.date.strftime("%Y-%m-%d"),
        db=db,
        owner_id=service.owner_id,
        exclude_id=appointment_id
    ):
        raise HTTPException(status_code=400, detail="Time slot conflict")
    
    try:
        db.commit()
        return {"message": "Appointment updated successfully", "appointment": appointment}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/appointments/{appointment_id}")  # Not /api/shared/appointments
def delete_appointment(
   appointment_id: int,
   db: Session = Depends(get_db),
   current_user: dict = Depends(get_current_user)
):
   appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
   if not appointment:
       raise HTTPException(status_code=404, detail="Appointment not found")
   
   try:
       db.delete(appointment)
       db.commit()
       return {"message": "Appointment deleted successfully"}
   except Exception as e:
       db.rollback()
       raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-topics")
def get_available_topics(db: Session = Depends(get_db)):
    """Get all available topics that can be used for appointments"""
    topics = db.query(Topic).join(Service).all()
    
    # Format the response to show useful information
    topic_list = []
    for topic in topics:
        topic_list.append({
            "name": topic.name,
            "duration": topic.duration,
            "cost": topic.cost,
            "service_name": topic.service.name,
            "business_owner": topic.service.owner.first_name + " " + topic.service.owner.last_name
        })
    
    return topic_list

@router.get("/appointments/search-by-user", response_model=List[AppointmentResponse])
async def search_appointments_by_user(
   db: Session = Depends(get_db),
   current_user: dict = Depends(get_current_user)
):
   user = db.query(User).filter(User.username == current_user["sub"]).first()
   if not user:
       raise HTTPException(status_code=404, detail="User not found")

   appointments = db.query(Appointment).filter(
       Appointment.customer_phone.contains(user.phone)
   ).order_by(Appointment.date.desc()).all()

   if not appointments:
       raise HTTPException(status_code=404, detail="No appointments found")

   return appointments


@router.get("/api/shared/me", response_model=UserResponse)
async def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current user information"""
    # Get username from the token payload
    username = current_user.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Query the database for the user
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Return UserResponse model
    return UserResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        phone=user.phone,
        role=user.role,
        business_name=user.business_name
    )

@router.delete("/appointments/{appointment_id}", response_model=dict)  # Make DELETE explicit
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    try:
        db.delete(appointment)
        db.commit()
        return {"message": "Appointment deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


 
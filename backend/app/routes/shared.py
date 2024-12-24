from fastapi import APIRouter, Depends, HTTPException
from app.schemas import AppointmentCreate, AppointmentUpdate, UserResponse
from app.models import appointments
from app.utils import is_time_conflict
from app.dependencies import get_current_user

router = APIRouter()

# Create Appointment
@router.post("/appointments")
def create_appointment(
    appointment: AppointmentCreate,
    current_user: dict = Depends(get_current_user)  # Ensuring the user is authenticated
):
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

@router.put("/appointments/{appointment_id}")
def update_appointment(
    appointment_id: int,
    update: AppointmentUpdate,
    current_user: dict = Depends(get_current_user)  # Ensuring the user is authenticated
):
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

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return current_user

@router.delete("/appointments/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    current_user: dict = Depends(get_current_user)  # Ensuring the user is authenticated
):
    if appointment_id not in appointments:
        raise HTTPException(status_code=404, detail="Appointment not found")
    del appointments[appointment_id]
    return {"message": "Appointment deleted successfully"}
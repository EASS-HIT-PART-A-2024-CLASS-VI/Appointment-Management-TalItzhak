from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Availability, User
from app.schemas import (
    AvailabilityCreate, 
    AvailabilityResponse, 
    BusinessAvailabilityResponse
)
from app.dependencies import get_db, business_owner_required
from typing import List

router = APIRouter()

@router.post("/availability", response_model=AvailabilityResponse)
def create_availability(
    availability: AvailabilityCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(business_owner_required)
):
    """הוספת זמן זמינות חדש"""
    # מציאת המשתמש לפי ה-username מה-token
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # בדיקה אם כבר קיים זמן זמינות שחופף
    existing_availability = db.query(Availability).filter(
        and_(
            Availability.owner_id == user.id,
            Availability.day_of_week == availability.day_of_week,
            Availability.start_time <= availability.end_time,
            Availability.end_time >= availability.start_time
        )
    ).first()

    if existing_availability:
        raise HTTPException(
            status_code=400, 
            detail="This time slot overlaps with an existing availability"
        )

    new_availability = Availability(
        day_of_week=availability.day_of_week,
        start_time=availability.start_time,
        end_time=availability.end_time,
        owner_id=user.id
    )

    db.add(new_availability)
    db.commit()
    db.refresh(new_availability)
    return new_availability

@router.get("/my-availability", response_model=List[AvailabilityResponse])
def get_my_availability(
    db: Session = Depends(get_db),
    current_user: dict = Depends(business_owner_required)
):
    """קבלת כל זמני הזמינות של בעל העסק המחובר"""
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    availability = db.query(Availability).filter(
        Availability.owner_id == user.id
    ).order_by(
        Availability.day_of_week,
        Availability.start_time
    ).all()

    return availability

@router.get("/business/{business_id}/availability", response_model=BusinessAvailabilityResponse)
def get_business_availability(business_id: int, db: Session = Depends(get_db)):
    """קבלת זמני הזמינות של עסק ספציפי"""
    business = db.query(User).filter(
        User.id == business_id,
        User.role == "business_owner"
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    availability = db.query(Availability).filter(
        Availability.owner_id == business_id
    ).order_by(
        Availability.day_of_week,
        Availability.start_time
    ).all()

    return {
        "business_id": business.id,
        "business_name": f"{business.first_name} {business.last_name}",
        "availability": availability
    }

@router.delete("/availability/{availability_id}")
def delete_availability(
    availability_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(business_owner_required)
):
    """מחיקת זמן זמינות"""
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    availability = db.query(Availability).filter(
        Availability.id == availability_id,
        Availability.owner_id == user.id
    ).first()

    if not availability:
        raise HTTPException(
            status_code=404,
            detail="Availability slot not found or you don't have permission to delete it"
        )

    db.delete(availability)
    db.commit()

    return {"message": "Availability slot deleted successfully"}
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.schemas import AppointmentResponse
from app.models import Appointment, User, appointments,Service
from app.utils import search_appointment_by_phone_and_name
from app.dependencies import get_db, check_user_role, get_current_user
from sqlalchemy import and_, text
from typing import List
import pandas as pd
from io import BytesIO
from fastapi.responses import Response
from fastapi.responses import StreamingResponse





router = APIRouter()

# Business owners only access
business_owner_required = check_user_role("business_owner")

def check_business_ownership(business_id: int, current_user: dict, db: Session):
    """Helper function to check if the current user owns the business"""
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user or user.id != business_id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to access this business's data"
        )
    return user


@router.get("/appointments/export")
async def export_appointments_to_excel(
    db: Session = Depends(get_db),
    current_user: dict = Depends(business_owner_required)
):
    try:
        print("Starting export process...")
        # Get the business owner
        user = db.query(User).filter(User.username == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get owner's services
        services = db.query(Service).filter(Service.owner_id == user.id).all()
        service_names = [service.name for service in services]

        # Get appointments for these services
        appointments = db.query(Appointment).filter(
            Appointment.type.in_(service_names)
        ).order_by(Appointment.date, Appointment.start_time).all()

        # Create DataFrame
        data = []
        for apt in appointments:
            data.append({
                'Date': apt.date.strftime('%Y-%m-%d') if apt.date else '',
                'Time': apt.start_time.strftime('%H:%M') if apt.start_time else '',
                'Service': apt.type or '',
                'Duration (minutes)': apt.duration or 0,
                'Customer Name': apt.customer_name or '',
                'Customer Phone': apt.customer_phone or '',
                'Cost': apt.cost or 0,
                'Notes': apt.notes or ''
            })

        # Create DataFrame with default columns if no data
        if not data:
            data = [{
                'Date': '',
                'Time': '',
                'Service': '',
                'Duration (minutes)': 0,
                'Customer Name': '',
                'Customer Phone': '',
                'Cost': 0,
                'Notes': ''
            }]

        df = pd.DataFrame(data)

        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Appointments')

        output.seek(0)

        # Use StreamingResponse instead of Response
        return StreamingResponse(
            BytesIO(output.getvalue()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename=appointments_{datetime.now().strftime("%Y%m%d")}.xlsx'
            }
        )

    except Exception as e:
        print(f"Export error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/appointments/{appointment_id}")
def get_appointment_details(
    appointment_id: int,
    business_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(business_owner_required)
):
    # Check business ownership
    check_business_ownership(business_id, current_user, db)
    
    # Get appointment
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    return appointment

@router.get("/appointments")
def list_appointments(
    business_id: int,
    title: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(business_owner_required)
):
    # Check business ownership
    check_business_ownership(business_id, current_user, db)
    
    # Query appointments
    query = db.query(Appointment)
    if title:
        query = query.filter(Appointment.title == title)
    
    return query.all()

@router.get("/appointments/search/{phone}")
def search_appointment(
   phone: str,
   db: Session = Depends(get_db),
   current_user: dict = Depends(business_owner_required)
):
   # Get the business owner
   user = db.query(User).filter(User.username == current_user["sub"]).first()
   if not user:
       raise HTTPException(status_code=404, detail="User not found")

   # Get the business owner's services
   services = db.query(Service).filter(Service.owner_id == user.id).all()
   service_names = [service.name for service in services]

   # Search appointments matching phone and business services
   appointments = db.query(Appointment).filter(
       Appointment.customer_phone.contains(phone),
       Appointment.type.in_(service_names)
   ).all()
   
   if not appointments:
       raise HTTPException(
           status_code=404,
           detail="No appointments found for this phone number with your business"
       )
   
   return appointments

@router.get("/appointments/stats/{date}")
def get_appointments_stats(
    date: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(business_owner_required)
):
    try:
        # Get the business owner
        user = db.query(User).filter(User.username == current_user["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Convert date string to date object
        target_date = datetime.strptime(date, "%m-%d-%Y").date()
        
        # Get owner's services
        services = db.query(Service).filter(Service.owner_id == user.id).all()
        service_names = [service.name for service in services]

        # Get appointments for the date that match owner's services
        appointments = db.query(Appointment).filter(
            text("DATE(date) = DATE(:target_date)"),
            Appointment.type.in_(service_names)
        ).params(target_date=target_date).all()

        if not appointments:
            raise HTTPException(
                status_code=404,
                detail=f"No appointments found for {target_date.strftime('%m/%d/%Y')}"
            )

        # Calculate statistics by service type
        service_stats = {}
        total_revenue = 0

        for appointment in appointments:
            if appointment.type not in service_stats:
                service_stats[appointment.type] = {
                    'count': 0,
                    'revenue': 0
                }
            
            service_stats[appointment.type]['count'] += 1
            service_stats[appointment.type]['revenue'] += appointment.cost
            total_revenue += appointment.cost

        return {
            "date": target_date.strftime("%m/%d/%Y"),
            "total_revenue": total_revenue,
            "services": service_stats
        }

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Please use MM-DD-YYYY format.")


@router.get("/my-appointments", response_model=List[AppointmentResponse])
async def get_business_appointments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(business_owner_required)
):
    # Get the business owner's info
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all appointments for this business owner's services
    appointments = db.query(Appointment).join(
        Service, 
        and_(
            Service.name == Appointment.type,
            Service.owner_id == user.id
        )
    ).order_by(Appointment.date.desc()).all()

    return appointments


from app.routes import (
    create_appointment,
    get_appointment_details,
    list_appointments,
    search_appointment,
    update_appointment,
    delete_appointment,
    get_appointments_stats,
)

from pydantic import ValidationError
from fastapi import APIRouter, HTTPException
from app.models import appointments
from app.schemas import AppointmentCreate, AppointmentUpdate
import pytest
from datetime import datetime


@pytest.fixture(autouse=True)
def reset_appointments():
    """Reset the appointments dictionary before each test."""
    appointments.clear()


# Test create_appointment
def test_create_appointment():
    new_appointment = AppointmentCreate(
        date=datetime(2024, 12, 11, 10, 0),
        start_time=datetime(2024, 12, 11, 10, 0).time(),  # Include start_time
        duration=30,  # Include duration
        title="Haircut",
        customer_name="John Doe",
        customer_phone="123-456-7890",
        type="Service",
        cost=50,
        notes="Test notes"
    )
    response = create_appointment(new_appointment)
    appointment_id = response["appointment_id"]
    assert response["message"] == "Appointment created successfully"
    assert appointment_id in appointments
    assert appointments[appointment_id]["title"] == "Haircut"


def test_create_appointment_invalid_data():
    """Test that creating an appointment with invalid data raises a ValidationError."""
    with pytest.raises(ValidationError): 
        create_appointment(AppointmentCreate(
            date="InvalidDate",  
            start_time="InvalidTime",  # Invalid time format
            duration="InvalidDuration",  # Invalid duration format
            title="",  # Empty title
            customer_name="John Doe",  
            customer_phone="123-456-7890", 
            type="Service", 
            cost=50, 
            notes="Test notes"  
        ))
        


# Test get_appointment_details
def test_get_appointment_details():
    appointments[1] = {
        "date": "2024-12-11T10:00:00",
        "title": "Haircut",
        "customer_name": "John Doe",
        "customer_phone": "123-456-7890",
        "type": "Service",
        "cost": 50,
        "notes": "Test notes"
    }
    response = get_appointment_details(1)
    assert response["title"] == "Haircut"


def test_get_appointment_details_not_found():
    with pytest.raises(HTTPException) as e:
        get_appointment_details(999)
    assert e.value.status_code == 404


# Test list_appointments
def test_list_appointments_all():
    appointments[1] = {"title": "Haircut"}
    appointments[2] = {"title": "Hair Color"}
    response = list_appointments()
    assert len(response) == 2


def test_list_appointments_no_appointments():
    response = list_appointments()
    assert response == {}


# Test search_appointment
def test_search_appointment():
    appointments[1] = {
        "customer_phone": "123-456-7890",
        "customer_name": "John Doe",
        "title": "Haircut"
    }
    response = search_appointment("123-456-7890", "John")
    assert 1 in response


def test_search_appointment_not_found():
    with pytest.raises(HTTPException) as e:
        search_appointment("987-654-3210", "Jane")
    assert e.value.status_code == 404



def test_update_appointment():
    appointments[1] = {
        "date": "2024-12-11T10:00:00",
        "start_time": "10:00", 
        "duration": 30, 
        "title": "Haircut",
        "customer_name": "John Doe",
        "customer_phone": "123-456-7890",
        "type": "Service",
        "cost": 50,
        "notes": "Test notes"
    }
    update_data = AppointmentUpdate(cost=60)
    response = update_appointment(1, update_data)
    assert response["message"] == "Appointment updated successfully"
    assert appointments[1]["cost"] == 60




def test_update_appointment_partial():
    # Mock an existing appointment with required fields
    appointments[1] = {
        "date": "2024-12-11T10:00:00",
        "start_time": "10:00",  # Add start_time
        "duration": 30,        # Add duration
        "title": "Haircut",
        "cost": 50,
        "type": "Service"
    }
    # Create update data
    update_data = AppointmentUpdate(cost=70)
    response = update_appointment(1, update_data)
    
    # Assertions
    assert response["message"] == "Appointment updated successfully"
    assert appointments[1]["cost"] == 70
    assert appointments[1]["type"] == "Service"  # Ensure type remains unchanged



def test_update_appointment_not_found():
    with pytest.raises(HTTPException) as e:
        update_appointment(999, AppointmentUpdate(cost=60))
    assert e.value.status_code == 404


def test_delete_appointment():
    appointments[1] = {"title": "Haircut"}
    response = delete_appointment(1)
    assert response["message"] == "Appointment deleted successfully"
    assert 1 not in appointments


def test_delete_appointment_not_found():
    with pytest.raises(HTTPException) as e:
        delete_appointment(999)
    assert e.value.status_code == 404


# Test get_appointments_stats
def test_get_appointments_stats():
    appointments[1] = {
        "date": "2024-12-11T10:00:00",
        "title": "Haircut",
        "cost": 50
    }
    appointments[2] = {
        "date": "2024-12-11T14:00:00",
        "title": "Hair Color",
        "cost": 70
    }
    response = get_appointments_stats("12-11-2024")
    assert response["date"] == "12/11/2024"
    assert response["titles"] == ["Haircut", "Hair Color"]
    assert response["total_revenue"] == 120


def test_get_appointments_stats_no_appointments():
    with pytest.raises(HTTPException) as e:
        get_appointments_stats("12-12-2024")
    assert e.value.status_code == 404


def test_get_appointments_stats_multiple_dates():
    appointments[1] = {"date": "2024-12-11T10:00:00", "title": "Haircut", "cost": 50}
    appointments[2] = {"date": "2024-12-12T14:00:00", "title": "Hair Color", "cost": 70}
    response = get_appointments_stats("12-11-2024")
    assert response["date"] == "12/11/2024"
    assert response["titles"] == ["Haircut"]
    assert response["total_revenue"] == 50
    

def test_create_overlapping_appointment():
    # Add an existing appointment
    appointments[1] = {
        "date": "2024-12-11T10:00:00",
        "start_time": "10:00",  # Existing appointment starts at 10:00
        "duration": 30,         # Existing appointment ends at 10:30
        "title": "Haircut",
        "customer_name": "John Doe",
        "customer_phone": "123-456-7890",
        "type": "Service",
        "cost": 50,
        "notes": "Test notes"
    }

    # Attempt to create a new appointment that overlaps with the existing one
    overlapping_appointment = AppointmentCreate(
        date=datetime(2024, 12, 11, 10, 15),  # Starts during the existing appointment
        start_time=datetime(2024, 12, 11, 10, 15).time(),
        duration=30,
        title="Consultation",
        customer_name="Jane Smith",
        customer_phone="987-654-3210",
        type="Service",
        cost=60,
        notes="Follow-up"
    )

    with pytest.raises(HTTPException) as e:
        create_appointment(overlapping_appointment)
    
    # Assert that the system rejects the overlapping appointment
    assert e.value.status_code == 400
    assert e.value.detail == "An appointment already exists during this time."


def test_update_to_overlapping_appointment():
    # Add two existing appointments
    appointments[1] = {
        "date": "2024-12-11T10:00:00",
        "start_time": "10:00",  # First appointment starts at 10:00
        "duration": 30,         # First appointment ends at 10:30
        "title": "Haircut",
        "customer_name": "John Doe",
        "customer_phone": "123-456-7890",
        "type": "Service",
        "cost": 50,
        "notes": "Test notes"
    }

    appointments[2] = {
        "date": "2024-12-11T11:00:00",
        "start_time": "11:00",  # Second appointment starts at 11:00
        "duration": 30,         # Second appointment ends at 11:30
        "title": "Consultation",
        "customer_name": "Jane Smith",
        "customer_phone": "987-654-3210",
        "type": "Service",
        "cost": 60,
        "notes": "Follow-up"
    }

    # Attempt to update the second appointment to overlap with the first
    overlapping_update = AppointmentUpdate(
        start_time=datetime.strptime("10:15", "%H:%M").time(),  # Overlaps with the first appointment
        duration=30
    )

    with pytest.raises(HTTPException) as e:
        update_appointment(2, overlapping_update)
    
    # Assert that the system rejects the update
    assert e.value.status_code == 400
    assert e.value.detail == "An appointment already exists during this time."
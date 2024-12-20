import pytest
from fastapi import HTTPException
from app.routes.shared import (
    create_appointment, update_appointment, delete_appointment, get_current_user_info
)
from app.schemas import AppointmentCreate, AppointmentUpdate
from app.models import appointments
from datetime import datetime
from unittest.mock import Mock

# -------------------------------------- #
# Pytest Fixture to Reset Appointments   #
# -------------------------------------- #
@pytest.fixture(autouse=True)
def reset_appointments():
    """
    Resets the 'appointments' dictionary before each test to ensure 
    test isolation. Prevents data from one test affecting another.
    """
    appointments.clear()

# -------------------------------------- #
# Fixture for Mock Authenticated User    #
# -------------------------------------- #
@pytest.fixture
def mock_user():
    """
    Simulates an authenticated user with a predefined username and role.
    This fixture can be passed to endpoints requiring authentication.
    """
    return {"username": "johndoe", "role": "customer"}

# -------------------------------------- #
# Test Create Appointment Endpoint       #
# -------------------------------------- #
def test_create_appointment(mock_user):
    """
    Test creating a new appointment successfully.
    Verifies that the appointment is added to the system.
    """
    new_appointment = AppointmentCreate(
        date=datetime(2024, 12, 11, 10, 0),
        start_time=datetime(2024, 12, 11, 10, 0).time(),
        duration=30,
        title="Haircut",
        customer_name="John Doe",
        customer_phone="123-456-7890",
        type="Service",
        cost=50,
        notes="Test notes"
    )
    response = create_appointment(new_appointment, current_user=mock_user)
    assert response["message"] == "Appointment created successfully"
    assert len(appointments) == 1  # Verify appointment was added

def test_create_appointment_time_conflict(mock_user):
    """
    Test creating an appointment that overlaps with an existing appointment.
    Verifies that an HTTP 400 error is raised.
    """
    # Existing appointment
    appointments[1] = {
        "date": "2024-12-11",
        "start_time": "10:00",
        "duration": 30
    }
    overlapping_appointment = AppointmentCreate(
        date=datetime(2024, 12, 11, 10, 15),  # Overlaps with the existing one
        start_time=datetime(2024, 12, 11, 10, 15).time(),
        duration=30,
        title="Consultation",
        customer_name="Jane Doe",
        customer_phone="555-555-5555",
        type="Service",
        cost=60
    )
    with pytest.raises(HTTPException) as e:
        create_appointment(overlapping_appointment, current_user=mock_user)
    assert e.value.status_code == 400
    assert e.value.detail == "An appointment already exists during this time."

# -------------------------------------- #
# Test Update Appointment Endpoint       #
# -------------------------------------- #
def test_update_appointment(mock_user):
    """
    Test updating an existing appointment successfully.
    Verifies that the appointment details are updated.
    """
    appointments[1] = {
        "date": "2024-12-11",
        "start_time": "10:00",
        "duration": 30,
        "title": "Haircut",
        "customer_name": "John Doe",
        "customer_phone": "123-456-7890",
        "type": "Service",
        "cost": 50
    }
    update_data = AppointmentUpdate(cost=60, notes="Updated notes")
    response = update_appointment(1, update_data, current_user=mock_user)
    assert response["message"] == "Appointment updated successfully"
    assert appointments[1]["cost"] == 60
    assert appointments[1]["notes"] == "Updated notes"

def test_update_appointment_not_found(mock_user):
    """
    Test updating a non-existent appointment.
    Verifies that an HTTP 404 error is raised.
    """
    update_data = AppointmentUpdate(cost=70)
    with pytest.raises(HTTPException) as e:
        update_appointment(999, update_data, current_user=mock_user)
    assert e.value.status_code == 404
    assert e.value.detail == "Appointment not found"

def test_update_appointment_time_conflict(mock_user):
    """
    Test updating an appointment to a time that conflicts with another appointment.
    Verifies that an HTTP 400 error is raised.
    """
    # Existing appointments
    appointments[1] = {"date": "2024-12-11", "start_time": "10:00", "duration": 30}
    appointments[2] = {"date": "2024-12-11", "start_time": "10:30", "duration": 30}
    update_data = AppointmentUpdate(
        start_time=datetime.strptime("10:15", "%H:%M").time(),
        duration=30
    )
    with pytest.raises(HTTPException) as e:
        update_appointment(2, update_data, current_user=mock_user)
    assert e.value.status_code == 400
    assert e.value.detail == "An appointment already exists during this time."

# -------------------------------------- #
# Test Get Current User Info             #
# -------------------------------------- #
def test_get_current_user_info(mock_user):
    """
    Test retrieving the current authenticated user info.
    Verifies that the correct user details are returned.
    """
    response = get_current_user_info(current_user=mock_user)
    assert response == mock_user

# -------------------------------------- #
# Test Delete Appointment Endpoint       #
# -------------------------------------- #
def test_delete_appointment(mock_user):
    """
    Test deleting an existing appointment successfully.
    Verifies that the appointment is removed from the system.
    """
    appointments[1] = {"title": "Haircut"}
    response = delete_appointment(1, current_user=mock_user)
    assert response["message"] == "Appointment deleted successfully"
    assert len(appointments) == 0  # Verify appointment was deleted

def test_delete_appointment_not_found(mock_user):
    """
    Test deleting a non-existent appointment.
    Verifies that an HTTP 404 error is raised.
    """
    with pytest.raises(HTTPException) as e:
        delete_appointment(999, current_user=mock_user)
    assert e.value.status_code == 404
    assert e.value.detail == "Appointment not found"

def test_delete_appointment_empty(mock_user):
    """
    Test deleting an appointment when no appointments exist.
    Verifies that an HTTP 404 error is raised.
    """
    with pytest.raises(HTTPException) as e:
        delete_appointment(1, current_user=mock_user)
    assert e.value.status_code == 404

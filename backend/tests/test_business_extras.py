import pytest
from fastapi import HTTPException
from app.routes.business_extras import (
    get_appointment_details, list_appointments, search_appointment, get_appointments_stats
)
from app.utils import search_appointment_by_phone_and_name
from app.models import appointments
from datetime import datetime

# -------------------------------------- #
# Pytest Fixture to Reset Appointments   #
# -------------------------------------- #
@pytest.fixture(autouse=True)
def reset_appointments():
    """
    Resets the 'appointments' dictionary before each test to ensure 
    a clean slate and prevent test data from interfering with each other.
    """
    appointments.clear()

# -------------------------------------- #
# Tests for Get Appointment Details      #
# -------------------------------------- #
def test_get_appointment_details():
    """
    Test retrieving the details of an existing appointment.
    Verifies that the correct appointment data is returned.
    """
    appointments[1] = {"title": "Haircut", "date": "2024-12-11T10:00:00"}
    response = get_appointment_details(1)
    assert response["title"] == "Haircut"

def test_get_appointment_details_not_found():
    """
    Test retrieving details for a non-existent appointment.
    Verifies that an HTTP 404 error is raised.
    """
    with pytest.raises(HTTPException) as e:
        get_appointment_details(999)
    assert e.value.status_code == 404
    assert e.value.detail == "Appointment not found"

# -------------------------------------- #
# Tests for List Appointments            #
# -------------------------------------- #
def test_list_appointments():
    """
    Test listing all appointments without filters.
    Verifies that all appointments are returned.
    """
    appointments[1] = {"title": "Haircut"}
    appointments[2] = {"title": "Consultation"}
    response = list_appointments()
    assert len(response) == 2

def test_list_appointments_with_title_filter():
    """
    Test listing appointments with a title filter.
    Verifies that only matching appointments are returned.
    """
    appointments[1] = {"title": "Haircut"}
    appointments[2] = {"title": "Consultation"}
    response = list_appointments(title="Haircut")
    assert len(response) == 1
    assert 1 in response

# -------------------------------------- #
# Tests for Search Appointment           #
# -------------------------------------- #
def test_search_appointment():
    """
    Test searching for an appointment using customer phone and name.
    Verifies that the correct appointment is returned.
    """
    appointments[1] = {
        "customer_phone": "123-456-7890",
        "customer_name": "John Doe",
        "title": "Haircut"
    }
    response = search_appointment("123-456-7890", "John")
    assert 1 in response

def test_search_appointment_not_found():
    """
    Test searching for an appointment that does not exist.
    Verifies that an HTTP 404 error is raised.
    """
    with pytest.raises(HTTPException) as e:
        search_appointment("555-555-5555", "Jane")
    assert e.value.status_code == 404
    assert e.value.detail == "No appointment found matching the given phone and name."

# -------------------------------------- #
# Tests for Get Appointments Stats       #
# -------------------------------------- #
def test_get_appointments_stats():
    """
    Test retrieving statistics for appointments on a specific date.
    Verifies the total revenue and titles of appointments.
    """
    appointments[1] = {"date": "2024-12-11T10:00:00", "title": "Haircut", "cost": 50}
    appointments[2] = {"date": "2024-12-11T14:00:00", "title": "Hair Color", "cost": 70}
    response = get_appointments_stats("12-11-2024")
    assert response["date"] == "12/11/2024"
    assert response["total_revenue"] == 120
    assert response["titles"] == ["Haircut", "Hair Color"]

def test_get_appointments_stats_no_appointments():
    """
    Test retrieving statistics for a date with no appointments.
    Verifies that an HTTP 404 error is raised.
    """
    with pytest.raises(HTTPException) as e:
        get_appointments_stats("12-11-2024")
    assert e.value.status_code == 404
    assert e.value.detail == "No appointments found for the given date."

def test_get_appointments_stats_invalid_date():
    """
    Test retrieving statistics with an invalid date format.
    Verifies that an HTTP 400 error is raised.
    """
    with pytest.raises(HTTPException) as e:
        get_appointments_stats("invalid-date")
    assert e.value.status_code == 400
    assert e.value.detail == "Invalid date format. Please use MM-DD-YYYY format."

# -------------------------------------- #
# Tests for Search Utility Function      #
# -------------------------------------- #
def test_search_appointment_by_phone_and_name():
    """
    Test the utility function 'search_appointment_by_phone_and_name'.
    Verifies that it correctly returns the matching appointment.
    """
    appointments[1] = {
        "customer_phone": "123-456-7890",
        "customer_name": "John Doe",
        "title": "Haircut"
    }
    result = search_appointment_by_phone_and_name("123-456-7890", "John", appointments)
    assert 1 in result

def test_search_appointment_by_phone_and_name_not_found():
    """
    Test the utility function 'search_appointment_by_phone_and_name' with no match.
    Verifies that an HTTP 404 error is raised.
    """
    appointments[1] = {
        "customer_phone": "123-456-7890",
        "customer_name": "John Doe",
        "title": "Haircut"
    }
    with pytest.raises(HTTPException) as e:
        search_appointment_by_phone_and_name("000-000-0000", "Jane", appointments)
    assert e.value.status_code == 404

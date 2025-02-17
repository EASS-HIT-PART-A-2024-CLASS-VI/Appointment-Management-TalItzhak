import pytest
from fastapi.testclient import TestClient
import os
os.environ["TESTING"] = "True"  # Set testing environment

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from app.dependencies import get_db
from datetime import datetime, timedelta

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def get_next_monday():
    today = datetime.now()
    days_ahead = 0 - today.weekday()  # Monday is 0
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return today + timedelta(days=days_ahead)

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    return TestClient(app)

@pytest.fixture
def business_owner_data():
    return {
        "first_name": "John",
        "last_name": "Smith",
        "username": "johnsmith",
        "phone": "0509876543",
        "password": "Pass1234!",
        "role": "business_owner",
        "business_name": "John's Hair Design"
    }

@pytest.fixture
def customer_data():
    return {
        "first_name": "Danny",
        "last_name": "Brown",
        "username": "dannybrown",
        "phone": "0501112222",
        "password": "Pass1234!",
        "role": "customer"
    }

def test_business_complete_flow(client, business_owner_data):
    """Test complete business owner journey"""
    print("\n=== Testing Complete Business Flow ===")
    
    # 1. Registration
    register_response = client.post("/auth/register", json=business_owner_data)
    assert register_response.status_code == 200
    
    # 2. Login
    login_response = client.post(
        "/auth/login",
        data={
            "username": business_owner_data["username"],
            "password": business_owner_data["password"]
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Service Setup
    services = [
        {
            "name": "Men's Haircut",
            "duration": 30,
            "price": 80
        },
        {
            "name": "Hair Coloring",
            "duration": 120,
            "price": 200
        },
        {
            "name": "Kids Haircut",
            "duration": 20,
            "price": 50
        }
    ]
    
    for service in services:
        response = client.post("/api/services/services", headers=headers, json=service)
        assert response.status_code == 200
        
    # 4. Availability Setup
    availability_slots = [
        {"day_of_week": "Sunday", "start_time": "09:00", "end_time": "17:00"},
        {"day_of_week": "Monday", "start_time": "09:00", "end_time": "17:00"},
        {"day_of_week": "Tuesday", "start_time": "09:00", "end_time": "17:00"},
        {"day_of_week": "Wednesday", "start_time": "09:00", "end_time": "17:00"},
        {"day_of_week": "Thursday", "start_time": "09:00", "end_time": "17:00"}
    ]
    
    for slot in availability_slots:
        response = client.post("/api/availability/availability", headers=headers, json=slot)
        assert response.status_code == 200
    
    # 5. Verify Service Setup
    services_response = client.get("/api/services/my-services", headers=headers)
    assert services_response.status_code == 200
    assert len(services_response.json()) == 3
    
    # 6. Verify Availability Setup
    availability_response = client.get("/api/availability/my-availability", headers=headers)
    assert availability_response.status_code == 200
    assert len(availability_response.json()) == 5

def test_customer_booking_flow(client, business_owner_data, customer_data):
    """Test complete customer journey"""
    print("\n=== Testing Complete Customer Flow ===")
    
    # 1. Setup Business Owner
    client.post("/auth/register", json=business_owner_data)
    business_login = client.post(
        "/auth/login",
        data={
            "username": business_owner_data["username"],
            "password": business_owner_data["password"]
        }
    )
    business_token = business_login.json()["access_token"]
    business_headers = {"Authorization": f"Bearer {business_token}"}
    
    # 2. Setup Services and Availability
    service = {
        "name": "Men's Haircut",
        "duration": 30,
        "price": 80
    }
    client.post("/api/services/services", headers=business_headers, json=service)
    
    availability = {
        "day_of_week": "Monday",
        "start_time": "09:00",
        "end_time": "17:00"
    }
    client.post("/api/availability/availability", headers=business_headers, json=availability)
    
    # 3. Register Customer
    client.post("/auth/register", json=customer_data)
    customer_login = client.post(
        "/auth/login",
        data={
            "username": customer_data["username"],
            "password": customer_data["password"]
        }
    )
    customer_token = customer_login.json()["access_token"]
    customer_headers = {"Authorization": f"Bearer {customer_token}"}
    
    # 4. Book Appointment
    next_monday = get_next_monday()
    appointment_data = {
        "date": next_monday.strftime("%Y-%m-%dT10:00:00"),
        "start_time": "10:00",
        "title": "Men's Haircut",
        "customer_name": f"{customer_data['first_name']} {customer_data['last_name']}",
        "customer_phone": customer_data["phone"]
    }
    
    book_response = client.post(
        "/api/shared/appointments?business_id=1",
        json=appointment_data,
        headers=customer_headers
    )
    assert book_response.status_code == 200
    
    # 5. Send Message to Business
    message_data = {
        "title": "Questions About Services",
        "content": "Can I reschedule my appointment to an earlier time?"
    }
    message_response = client.post(
        "/api/messages/send/1",
        json=message_data,
        headers=customer_headers
    )
    assert message_response.status_code == 200
    
    # 6. Business Checks Messages
    messages_response = client.get("/api/messages/my-messages", headers=business_headers)
    assert messages_response.status_code == 200
    assert len(messages_response.json()) == 1

def test_double_booking_prevention(client, business_owner_data, customer_data):
    """Test that double booking the same time slot is prevented"""
    # Create business owner and service setup
    client.post("/auth/register", json=business_owner_data)
    business_login = client.post(
        "/auth/login",
        data={
            "username": business_owner_data["username"],
            "password": business_owner_data["password"]
        }
    )
    business_token = business_login.json()["access_token"]
    business_headers = {"Authorization": f"Bearer {business_token}"}
    
    # Setup service and availability
    service = {
        "name": "Men's Haircut",
        "duration": 30,
        "price": 80
    }
    client.post("/api/services/services", headers=business_headers, json=service)
    
    availability = {
        "day_of_week": "Monday",
        "start_time": "09:00",
        "end_time": "17:00"
    }
    client.post("/api/availability/availability", headers=business_headers, json=availability)
    
    # Register two customers
    client.post("/auth/register", json=customer_data)
    customer2_data = customer_data.copy()
    customer2_data.update({
        "username": "customer2",
        "phone": "0503333333"
    })
    client.post("/auth/register", json=customer2_data)
    
    # Login first customer
    customer1_login = client.post(
        "/auth/login",
        data={
            "username": customer_data["username"],
            "password": customer_data["password"]
        }
    )
    customer1_token = customer1_login.json()["access_token"]
    customer1_headers = {"Authorization": f"Bearer {customer1_token}"}
    
    # Login second customer
    customer2_login = client.post(
        "/auth/login",
        data={
            "username": customer2_data["username"],
            "password": customer2_data["password"]
        }
    )
    customer2_token = customer2_login.json()["access_token"]
    customer2_headers = {"Authorization": f"Bearer {customer2_token}"}
    
    # Book same time slot with both customers
    next_monday = get_next_monday()
    appointment_data = {
        "date": next_monday.strftime("%Y-%m-%dT10:00:00"),
        "start_time": "10:00",
        "title": "Men's Haircut",
        "customer_name": f"{customer_data['first_name']} {customer_data['last_name']}",
        "customer_phone": customer_data["phone"]
    }
    
    # First booking should succeed
    response1 = client.post(
        "/api/shared/appointments?business_id=1",
        json=appointment_data,
        headers=customer1_headers
    )
    assert response1.status_code == 200
    
    # Second booking should fail
    appointment_data["customer_name"] = f"{customer2_data['first_name']} {customer2_data['last_name']}"
    appointment_data["customer_phone"] = customer2_data["phone"]
    response2 = client.post(
        "/api/shared/appointments?business_id=1",
        json=appointment_data,
        headers=customer2_headers
    )
    assert response2.status_code == 400
    assert "conflicts" in response2.json()["detail"]

def test_service_modification_with_existing_appointments(client, business_owner_data, customer_data):
    """Test modifying service duration when appointments exist"""
    # Setup and create appointment
    client.post("/auth/register", json=business_owner_data)
    business_login = client.post(
        "/auth/login",
        data={
            "username": business_owner_data["username"],
            "password": business_owner_data["password"]
        }
    )
    business_token = business_login.json()["access_token"]
    business_headers = {"Authorization": f"Bearer {business_token}"}
    
    # Create service
    service = {
        "name": "Men's Haircut",
        "duration": 30,
        "price": 80
    }
    service_response = client.post("/api/services/services", headers=business_headers, json=service)
    service_id = service_response.json()["id"]
    
    # Set availability
    availability = {
        "day_of_week": "Monday",
        "start_time": "09:00",
        "end_time": "17:00"
    }
    client.post("/api/availability/availability", headers=business_headers, json=availability)
    
    # Register and login customer
    client.post("/auth/register", json=customer_data)
    customer_login = client.post(
        "/auth/login",
        data={
            "username": customer_data["username"],
            "password": customer_data["password"]
        }
    )
    customer_token = customer_login.json()["access_token"]
    customer_headers = {"Authorization": f"Bearer {customer_token}"}
    
    # Create an appointment
    next_monday = get_next_monday()
    appointment_data = {
        "date": next_monday.strftime("%Y-%m-%dT10:00:00"),
        "start_time": "10:00",
        "title": "Men's Haircut",
        "customer_name": f"{customer_data['first_name']} {customer_data['last_name']}",
        "customer_phone": customer_data["phone"]
    }
    
    book_response = client.post(
        "/api/shared/appointments?business_id=1",
        json=appointment_data,
        headers=customer_headers
    )
    assert book_response.status_code == 200
    appointment_id = book_response.json()["appointment"]["id"]

    # Try to modify service duration
    updated_service = {
        "duration": 60,  # Double the duration
        "price": 100    # Increase price
    }
    
    modification_response = client.put(
        f"/api/services/services/{service_id}",
        headers=business_headers,
        json=updated_service
    )
    assert modification_response.status_code == 200
    
    # Verify service was updated
    service_check = client.get(
        "/api/services/my-services",
        headers=business_headers
    )
    updated_service_data = next(s for s in service_check.json() if s["id"] == service_id)
    assert updated_service_data["duration"] == 60
    assert updated_service_data["price"] == 100
    
    # Verify existing appointment duration was not affected
    appointment_check = client.get(
        f"/api/business/appointments/{appointment_id}?business_id=1",
        headers=business_headers
    )
    assert appointment_check.json()["duration"] == 30  # Original duration
    
    # Try to book a new appointment (should use new duration)
    new_appointment_data = {
        "date": next_monday.strftime("%Y-%m-%dT11:00:00"),
        "start_time": "11:00",
        "title": "Men's Haircut",
        "customer_name": f"{customer_data['first_name']} {customer_data['last_name']}",
        "customer_phone": customer_data["phone"]
    }
    
    new_book_response = client.post(
        "/api/shared/appointments?business_id=1",
        json=new_appointment_data,
        headers=customer_headers
    )
    assert new_book_response.status_code == 200
    new_appointment = new_book_response.json()["appointment"]
    assert new_appointment["duration"] == 60  # New duration
    assert new_appointment["cost"] == 100     # New price
    
    # Try to book an appointment that would overlap due to new duration
    overlap_appointment_data = {
        "date": next_monday.strftime("%Y-%m-%dT11:45:00"),  # Would overlap with 60-min duration
        "start_time": "11:45",
        "title": "Men's Haircut",
        "customer_name": f"{customer_data['first_name']} {customer_data['last_name']}",
        "customer_phone": customer_data["phone"]
    }
    
    overlap_response = client.post(
        "/api/shared/appointments?business_id=1",
        json=overlap_appointment_data,
        headers=customer_headers
    )
    assert overlap_response.status_code == 400
    assert "conflicts" in overlap_response.json()["detail"]

def test_message_notification_flow(client, business_owner_data, customer_data):
    """Test the complete message notification flow between customer and business"""
    # Setup business owner
    client.post("/auth/register", json=business_owner_data)
    business_login = client.post(
        "/auth/login",
        data={
            "username": business_owner_data["username"],
            "password": business_owner_data["password"]
        }
    )
    business_token = business_login.json()["access_token"]
    business_headers = {"Authorization": f"Bearer {business_token}"}

    # Register customer
    client.post("/auth/register", json=customer_data)
    customer_login = client.post(
        "/auth/login",
        data={
            "username": customer_data["username"],
            "password": customer_data["password"]
        }
    )
    customer_token = customer_login.json()["access_token"]
    customer_headers = {"Authorization": f"Bearer {customer_token}"}

    # Customer sends message
    message_data = {
        "title": "Questions About Services",
        "content": "Do you have any availability tomorrow?"
    }
    send_response = client.post(
        "/api/messages/send/1",
        json=message_data,
        headers=customer_headers
    )
    assert send_response.status_code == 200
    message_id = send_response.json()["id"]

    # Business owner checks unread count
    unread_response = client.get(
        "/api/messages/unread-count",
        headers=business_headers
    )
    assert unread_response.status_code == 200
    assert unread_response.json()["unread_count"] == 1

    # Business owner reads message
    messages_response = client.get(
        "/api/messages/my-messages",
        headers=business_headers
    )
    assert messages_response.status_code == 200
    messages = messages_response.json()
    assert len(messages) == 1
    assert messages[0]["content"] == message_data["content"]
    assert not messages[0]["read"]

    # Mark message as read
    mark_read_response = client.patch(
        f"/api/messages/messages/{message_id}/read",
        headers=business_headers
    )
    assert mark_read_response.status_code == 200

    # Verify message is marked as read
    messages_response = client.get(
        "/api/messages/my-messages",
        headers=business_headers
    )
    assert messages_response.json()[0]["read"]

def test_multiple_day_booking_validation(client, business_owner_data, customer_data):
    """Test booking validation across multiple days with different availability"""
    # Setup business owner
    client.post("/auth/register", json=business_owner_data)
    business_login = client.post(
        "/auth/login",
        data={
            "username": business_owner_data["username"],
            "password": business_owner_data["password"]
        }
    )
    business_token = business_login.json()["access_token"]
    business_headers = {"Authorization": f"Bearer {business_token}"}

    # Create service
    service = {
        "name": "Men's Haircut",
        "duration": 30,
        "price": 80
    }
    client.post("/api/services/services", headers=business_headers, json=service)

    # Set different availability for different days
    availability_slots = [
        {"day_of_week": "Monday", "start_time": "09:00", "end_time": "17:00"},
        {"day_of_week": "Tuesday", "start_time": "12:00", "end_time": "20:00"},
    ]
    for slot in availability_slots:
        response = client.post(
            "/api/availability/availability",
            headers=business_headers,
            json=slot
        )
        assert response.status_code == 200

    # Register and login customer
    client.post("/auth/register", json=customer_data)
    customer_login = client.post(
        "/auth/login",
        data={
            "username": customer_data["username"],
            "password": customer_data["password"]
        }
    )
    customer_token = customer_login.json()["access_token"]
    customer_headers = {"Authorization": f"Bearer {customer_token}"}

    # Try booking on Monday during business hours
    next_monday = get_next_monday()
    monday_data = {
        "date": next_monday.strftime("%Y-%m-%dT10:00:00"),
        "start_time": "10:00",
        "title": "Men's Haircut",
        "customer_name": f"{customer_data['first_name']} {customer_data['last_name']}",
        "customer_phone": customer_data["phone"]
    }
    monday_response = client.post(
        "/api/shared/appointments?business_id=1",
        json=monday_data,
        headers=customer_headers
    )
    assert monday_response.status_code == 200

    # Try booking on Monday outside business hours
    monday_early = {
        "date": next_monday.strftime("%Y-%m-%dT08:00:00"),
        "start_time": "08:00",
        "title": "Men's Haircut",
        "customer_name": f"{customer_data['first_name']} {customer_data['last_name']}",
        "customer_phone": customer_data["phone"]
    }
    early_response = client.post(
        "/api/shared/appointments?business_id=1",
        json=monday_early,
        headers=customer_headers
    )
    assert early_response.status_code == 400
    assert "outside business hours" in early_response.json()["detail"]["message"]

    # Try booking on Tuesday during its specific hours
    next_tuesday = next_monday + timedelta(days=1)
    tuesday_data = {
        "date": next_tuesday.strftime("%Y-%m-%dT15:00:00"),
        "start_time": "15:00",
        "title": "Men's Haircut",
        "customer_name": f"{customer_data['first_name']} {customer_data['last_name']}",
        "customer_phone": customer_data["phone"]
    }
    tuesday_response = client.post(
        "/api/shared/appointments?business_id=1",
        json=tuesday_data,
        headers=customer_headers
    )
    assert tuesday_response.status_code == 200
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.main import app
from app.database import Base
from app.dependencies import get_db
from app.models import Appointment, User

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

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    return TestClient(app)

@pytest.fixture
def business_owner_token(client):
    # Register business owner
    client.post(
        "/auth/register",
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "username": "janesmith",
            "phone": "0987654321",
            "password": "testpass123",
            "role": "business_owner",
            "business_name": "Jane's Salon"
        }
    )
    
    # Login and get token
    response = client.post(
        "/auth/login",
        data={
            "username": "janesmith",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def create_test_appointment(test_db):
    db = TestingSessionLocal()
    appointment = Appointment(
        date=datetime.now().date(),
        start_time=datetime.strptime("10:00", "%H:%M").time(),
        duration=60,
        title="Test Service",
        customer_name="John Doe",
        customer_phone="1234567890",
        type="Test Type",
        cost=100
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    db.close()
    return appointment

def test_get_appointment_details(client, business_owner_token, create_test_appointment):
    response = client.get(
        f"/api/business/appointments/{create_test_appointment.id}?business_id=1",
        headers={"Authorization": f"Bearer {business_owner_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Service"
    assert data["customer_name"] == "John Doe"

def test_list_appointments(client, business_owner_token, create_test_appointment):
    response = client.get(
        "/api/business/appointments?business_id=1",
        headers={"Authorization": f"Bearer {business_owner_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "Test Service"

def test_list_appointments_with_title_filter(client, business_owner_token, create_test_appointment):
    response = client.get(
        "/api/business/appointments?business_id=1&title=Test Service",
        headers={"Authorization": f"Bearer {business_owner_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(appointment["title"] == "Test Service" for appointment in data)

def test_unauthorized_access(client, create_test_appointment):
    response = client.get(
        f"/api/business/appointments/{create_test_appointment.id}?business_id=1"
    )
    assert response.status_code == 401

def test_appointment_not_found(client, business_owner_token):
    response = client.get(
        "/api/business/appointments/999?business_id=1",
        headers={"Authorization": f"Bearer {business_owner_token}"}
    )
    assert response.status_code == 404

def test_invalid_date_format_stats(client, business_owner_token):
    response = client.get(
        "/api/business/appointments/stats/invalid-date?business_id=1",
        headers={"Authorization": f"Bearer {business_owner_token}"}
    )
    assert response.status_code == 400

def test_get_appointments_stats_empty_day(client, business_owner_token):
    """Test statistics for a day with no appointments"""
    # Use a date in the past to ensure no appointments
    response = client.get(
        "/api/business/appointments/stats/01-01-2020",
        headers={"Authorization": f"Bearer {business_owner_token}"}
    )
    assert response.status_code == 404
    assert "No appointments found" in response.json()["detail"]

def test_appointment_details_wrong_business(client, business_owner_token, create_test_appointment):
    """Test accessing appointment details with wrong business ID"""
    response = client.get(
        f"/api/business/appointments/{create_test_appointment.id}?business_id=999",  # Wrong business ID
        headers={"Authorization": f"Bearer {business_owner_token}"}
    )
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()



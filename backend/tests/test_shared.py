import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, time
from app.main import app
from app.database import Base, get_db
from app.models import Service, User, Availability, Appointment

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def business_owner(db):
    user = User(
        first_name="Jane",
        last_name="Smith",
        username="janesmith",
        phone="0987654321",
        password_hash="hashed_password",
        role="business_owner",
        business_name="Jane's Salon"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_service(db, business_owner):
    service = Service(
        name="Test Service",
        duration=60,
        price=100,
        owner_id=business_owner.id
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

@pytest.fixture
def test_availability(db, business_owner):
    availability = Availability(
        day_of_week="Monday",
        start_time=time(9, 0),
        end_time=time(17, 0),
        owner_id=business_owner.id
    )
    db.add(availability)
    db.commit()
    db.refresh(availability)
    return availability

def test_create_appointment(client, test_service, test_availability):
    tomorrow = datetime.now() + timedelta(days=1)
    if tomorrow.strftime("%A") != "Monday":
        tomorrow = tomorrow + timedelta(days=(7 - tomorrow.weekday()))
    
    response = client.post(
        f"/api/shared/appointments?business_id={test_service.owner_id}",
        json={
            "date": tomorrow.strftime("%Y-%m-%dT10:00:00"),
            "start_time": "10:00",
            "title": test_service.name,
            "customer_name": "Test Customer",
            "customer_phone": "1234567890"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "appointment" in data

# Add these tests to your test_shared.py

def test_create_appointment_outside_business_hours(client, test_service, test_availability):
    """Test creating appointment outside business hours"""
    tomorrow = datetime.now() + timedelta(days=1)
    if tomorrow.strftime("%A") != "Monday":
        tomorrow = tomorrow + timedelta(days=(7 - tomorrow.weekday()))
    
    response = client.post(
        f"/api/shared/appointments?business_id={test_service.owner_id}",
        json={
            "date": tomorrow.strftime("%Y-%m-%dT18:00:00"),  # After business hours
            "start_time": "18:00",
            "title": test_service.name,
            "customer_name": "Test Customer",
            "customer_phone": "1234567890"
        }
    )
    assert response.status_code == 400
    assert "outside business hours" in response.json()["detail"]["message"]

def test_create_overlapping_appointment(client, test_service, test_availability, db):
    """Test creating an appointment that overlaps with existing one"""
    # Create first appointment
    tomorrow = datetime.now() + timedelta(days=1)
    if tomorrow.strftime("%A") != "Monday":
        tomorrow = tomorrow + timedelta(days=(7 - tomorrow.weekday()))
    
    # First appointment
    first_response = client.post(
        f"/api/shared/appointments?business_id={test_service.owner_id}",
        json={
            "date": tomorrow.strftime("%Y-%m-%dT10:00:00"),
            "start_time": "10:00",
            "title": test_service.name,
            "customer_name": "Test Customer 1",
            "customer_phone": "1234567890"
        }
    )
    
    # Try to create overlapping appointment
    second_response = client.post(
        f"/api/shared/appointments?business_id={test_service.owner_id}",
        json={
            "date": tomorrow.strftime("%Y-%m-%dT10:30:00"),  # Overlaps with first appointment
            "start_time": "10:30",
            "title": test_service.name,
            "customer_name": "Test Customer 2",
            "customer_phone": "0987654321"
        }
    )
    
    assert second_response.status_code == 400
    assert "conflicts" in second_response.json()["detail"]

def test_create_appointment_invalid_service(client, business_owner, test_availability):
    """Test creating appointment with non-existent service"""
    tomorrow = datetime.now() + timedelta(days=1)
    if tomorrow.strftime("%A") != "Monday":
        tomorrow = tomorrow + timedelta(days=(7 - tomorrow.weekday()))
    
    response = client.post(
        f"/api/shared/appointments?business_id={business_owner.id}",
        json={
            "date": tomorrow.strftime("%Y-%m-%dT10:00:00"),
            "start_time": "10:00",
            "title": "Non-existent Service",
            "customer_name": "Test Customer",
            "customer_phone": "1234567890"
        }
    )
    assert response.status_code == 400
    assert "Invalid service" in response.json()["detail"]["message"]

def test_create_appointment_no_availability(client, test_service, db):
    """Test creating appointment when no availability is set"""
    tomorrow = datetime.now() + timedelta(days=1)
    
    response = client.post(
        f"/api/shared/appointments?business_id={test_service.owner_id}",
        json={
            "date": tomorrow.strftime("%Y-%m-%dT10:00:00"),
            "start_time": "10:00",
            "title": test_service.name,
            "customer_name": "Test Customer",
            "customer_phone": "1234567890"
        }
    )
    assert response.status_code == 400
    assert "not available" in response.json()["detail"]


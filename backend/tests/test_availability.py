import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import time
from app.main import app
from app.database import Base
from app.dependencies import get_db

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

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    return TestClient(app)

@pytest.fixture
def business_owner_token(client):
    # Register a business owner
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

def test_create_availability_success(client, business_owner_token):
    response = client.post(
        "/api/availability/availability",
        headers={"Authorization": f"Bearer {business_owner_token}"},
        json={
            "day_of_week": "Monday",
            "start_time": "09:00",
            "end_time": "17:00"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["day_of_week"] == "Monday"
    assert data["start_time"] == "09:00:00"
    assert data["end_time"] == "17:00:00"

def test_create_availability_overlap(client, business_owner_token):
    # Create first availability
    client.post(
        "/api/availability/availability",
        headers={"Authorization": f"Bearer {business_owner_token}"},
        json={
            "day_of_week": "Monday",
            "start_time": "09:00",
            "end_time": "17:00"
        }
    )
    
    # Try to create overlapping availability
    response = client.post(
        "/api/availability/availability",
        headers={"Authorization": f"Bearer {business_owner_token}"},
        json={
            "day_of_week": "Monday",
            "start_time": "10:00",
            "end_time": "18:00"
        }
    )
    assert response.status_code == 400
    assert "overlaps" in response.json()["detail"]

def test_get_my_availability(client, business_owner_token):
    # Create availability first
    client.post(
        "/api/availability/availability",
        headers={"Authorization": f"Bearer {business_owner_token}"},
        json={
            "day_of_week": "Monday",
            "start_time": "09:00",
            "end_time": "17:00"
        }
    )
    
    response = client.get(
        "/api/availability/my-availability",
        headers={"Authorization": f"Bearer {business_owner_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["day_of_week"] == "Monday"

def test_get_business_availability(client, business_owner_token):
    # Create availability first
    client.post(
        "/api/availability/availability",
        headers={"Authorization": f"Bearer {business_owner_token}"},
        json={
            "day_of_week": "Monday",
            "start_time": "09:00",
            "end_time": "17:00"
        }
    )
    
    # Get the business ID (assuming it's 1 since it's the first user)
    response = client.get(
        "/api/availability/business/1/availability"
    )
    assert response.status_code == 200
    data = response.json()
    assert "business_id" in data
    assert "availability" in data
    assert len(data["availability"]) == 1

def test_delete_availability(client, business_owner_token):
    # Create availability first
    response = client.post(
        "/api/availability/availability",
        headers={"Authorization": f"Bearer {business_owner_token}"},
        json={
            "day_of_week": "Monday",
            "start_time": "09:00",
            "end_time": "17:00"
        }
    )
    availability_id = response.json()["id"]
    
    # Delete availability
    response = client.delete(
        f"/api/availability/availability/{availability_id}",
        headers={"Authorization": f"Bearer {business_owner_token}"}
    )
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]

def test_unauthorized_access(client):
    response = client.get("/api/availability/my-availability")
    assert response.status_code == 401

def test_invalid_time_range(client, business_owner_token):
    response = client.post(
        "/api/availability/availability",
        headers={"Authorization": f"Bearer {business_owner_token}"},
        json={
            "day_of_week": "Monday",
            "start_time": "17:00",
            "end_time": "09:00"  # End time before start time
        }
    )
    assert response.status_code == 422  # Validation error

def test_create_availability_for_multiple_days(client, business_owner_token):
    days = ["Monday", "Tuesday", "Wednesday"]
    for day in days:
        response = client.post(
            "/api/availability/availability",
            headers={"Authorization": f"Bearer {business_owner_token}"},
            json={
                "day_of_week": day,
                "start_time": "09:00",
                "end_time": "17:00"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["day_of_week"] == day

def test_create_availability_with_invalid_day(client, business_owner_token):
    response = client.post(
        "/api/availability/availability",
        headers={"Authorization": f"Bearer {business_owner_token}"},
        json={
            "day_of_week": "NotADay",
            "start_time": "09:00",
            "end_time": "17:00"
        }
    )
    assert response.status_code == 422  # Validation error

def test_create_availability_with_exact_matching_time(client, business_owner_token):
    client.post(
        "/api/availability/availability",
        headers={"Authorization": f"Bearer {business_owner_token}"},
        json={
            "day_of_week": "Monday",
            "start_time": "09:00",
            "end_time": "17:00"
        }
    )
    response = client.post(
        "/api/availability/availability",
        headers={"Authorization": f"Bearer {business_owner_token}"},
        json={
            "day_of_week": "Monday",
            "start_time": "09:00",
            "end_time": "17:00"
        }
    )
    assert response.status_code == 400  # Overlapping test

def test_get_availability_when_none_exists(client, business_owner_token):
    response = client.get(
        "/api/availability/my-availability",
        headers={"Authorization": f"Bearer {business_owner_token}"}
    )
    assert response.status_code == 200
    assert response.json() == []  # Expecting an empty list

def test_delete_non_existent_availability(client, business_owner_token):
    response = client.delete(
        "/api/availability/availability/9999",
        headers={"Authorization": f"Bearer {business_owner_token}"}
    )
    assert response.status_code == 404  # Availability not found


import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, time
from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function", autouse=True)
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client():
    return TestClient(app)

def test_complete_business_flow(client, test_db):
    # Register business owner
    register_response = client.post(
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
    assert register_response.status_code == 200

    # Login
    login_response = client.post(
        "/auth/login",
        data={
            "username": "janesmith",
            "password": "testpass123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create service
    service_response = client.post(
        "/api/services/services",
        headers=headers,
        json={
            "name": "Haircut",
            "duration": 60,
            "price": 100
        }
    )
    assert service_response.status_code == 200

    # Set availability
    availability_response = client.post(
        "/api/availability/availability",
        headers=headers,
        json={
            "day_of_week": "Monday",
            "start_time": "09:00",
            "end_time": "17:00"
        }
    )
    assert availability_response.status_code == 200

    # Create appointment
    tomorrow = datetime.now() + timedelta(days=1)
    if tomorrow.strftime("%A") != "Monday":
        tomorrow = tomorrow + timedelta(days=(7 - tomorrow.weekday()))

    appointment_response = client.post(
        "/api/shared/appointments",
        params={"business_id": 1},
        json={
            "date": tomorrow.strftime("%Y-%m-%dT10:00:00"),
            "start_time": "10:00",
            "title": "Haircut",
            "customer_name": "John Doe",
            "customer_phone": "1234567890"
        }
    )
    assert appointment_response.status_code == 200

    # Verify appointment list
    appointments_response = client.get(
        "/api/business/appointments?business_id=1",
        headers=headers
    )
    assert appointments_response.status_code == 200
    appointments = appointments_response.json()
    assert len(appointments) == 1

    # Check business stats
    stats_response = client.get(
        f"/api/business/appointments/stats/{tomorrow.strftime('%m-%d-%Y')}?business_id=1",
        headers=headers
    )
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["total_revenue"] == 100
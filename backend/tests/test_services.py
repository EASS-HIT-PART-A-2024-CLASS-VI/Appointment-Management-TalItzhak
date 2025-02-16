import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from app.dependencies import get_db
from app.models import Service, User

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
    response = client.post(
        "/auth/login",
        data={
            "username": "janesmith",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def test_service(business_owner_token, client):
    response = client.post(
        "/api/services/services",
        headers={"Authorization": f"Bearer {business_owner_token}"},
        json={
            "name": "Test Service",
            "duration": 60,
            "price": 100
        }
    )
    return response.json()

def test_create_service(client, business_owner_token):
    response = client.post(
        "/api/services/services",
        headers={"Authorization": f"Bearer {business_owner_token}"},
        json={
            "name": "Haircut",
            "duration": 30,
            "price": 50
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Haircut"
    assert data["duration"] == 30
    assert data["price"] == 50

def test_get_my_services(client, business_owner_token, test_service):
    response = client.get(
        "/api/services/my-services",
        headers={"Authorization": f"Bearer {business_owner_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test Service"

def test_get_public_businesses(client, business_owner_token):
    response = client.get("/api/services/public/businesses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "first_name" in data[0]
    assert "last_name" in data[0]
    assert "username" in data[0]
    assert "services" in data[0]

def test_get_business_services(client, business_owner_token, test_service):
    response = client.get("/api/services/public/businesses/1/services")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test Service"

def test_update_service(client, business_owner_token, test_service):
    response = client.put(
        f"/api/services/services/{test_service['id']}",
        headers={"Authorization": f"Bearer {business_owner_token}"},
        json={
            "name": "Updated Service",
            "price": 75
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Service"
    assert data["price"] == 75
    assert data["duration"] == 60  # Unchanged

def test_delete_service(client, business_owner_token, test_service):
    response = client.delete(
        f"/api/services/services/{test_service['id']}",
        headers={"Authorization": f"Bearer {business_owner_token}"}
    )
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]

def test_unauthorized_service_creation(client):
    response = client.post(
        "/api/services/services",
        json={
            "name": "Unauthorized Service",
            "duration": 30,
            "price": 50
        }
    )
    assert response.status_code == 401

def test_nonexistent_service(client, business_owner_token):
    response = client.get("/api/services/public/businesses/999/services")
    assert response.status_code == 404

def test_create_service_missing_fields(client, business_owner_token):
    response = client.post(
        "/api/services/services",
        headers={"Authorization": f"Bearer {business_owner_token}"},
        json={
            "name": "Missing Fields Service"
        }
    )
    assert response.status_code == 422
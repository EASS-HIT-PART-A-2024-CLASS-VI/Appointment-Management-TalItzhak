import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from app.dependencies import get_db

# Test database setup
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

# Test registration endpoints
def test_register_customer_success(client):
    response = client.post(
        "/auth/register",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "phone": "1234567890",
            "password": "testpass123",
            "role": "customer"
        }
    )
    assert response.status_code == 200
    assert "User registered successfully" in response.json()["message"]

def test_register_business_owner_success(client):
    response = client.post(
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
    assert response.status_code == 200
    assert "User registered successfully" in response.json()["message"]

def test_register_business_owner_without_business_name(client):
    response = client.post(
        "/auth/register",
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "username": "janesmith",
            "phone": "0987654321",
            "password": "testpass123",
            "role": "business_owner"
        }
    )
    assert response.status_code == 400
    assert "Business name is required" in response.json()["detail"]

def test_register_duplicate_username(client):
    # Register first user
    client.post(
        "/auth/register",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "phone": "1234567890",
            "password": "testpass123",
            "role": "customer"
        }
    )
    
    # Try to register with same username
    response = client.post(
        "/auth/register",
        json={
            "first_name": "John",
            "last_name": "Smith",
            "username": "johndoe",
            "phone": "9876543210",
            "password": "testpass123",
            "role": "customer"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

# Test login endpoints
def test_login_success(client):
    # First register a user
    client.post(
        "/auth/register",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "phone": "1234567890",
            "password": "testpass123",
            "role": "customer"
        }
    )
    
    # Then try to login
    response = client.post(
        "/auth/login",
        data={
            "username": "johndoe",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(client):
    # First register a user
    client.post(
        "/auth/register",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "phone": "1234567890",
            "password": "testpass123",
            "role": "customer"
        }
    )
    
    # Try to login with wrong password
    response = client.post(
        "/auth/login",
        data={
            "username": "johndoe",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]

def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "nonexistent",
            "password": "testpass123"
        }
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]
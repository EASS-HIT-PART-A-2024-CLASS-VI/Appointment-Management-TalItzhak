import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from app.dependencies import get_db
from app.models import User
from app.security import verify_password

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

@pytest.fixture(scope="function")
def test_customer():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "phone": "1234567890",
        "password": "testpass123",
        "role": "customer"
    }

@pytest.fixture(scope="function")
def test_business_owner():
    return {
        "first_name": "Jane",
        "last_name": "Smith",
        "username": "janesmith",
        "phone": "0987654321",
        "password": "testpass123",
        "role": "business_owner",
        "business_name": "Jane's Salon"
    }

# Registration Tests
def test_register_customer_success(client, test_customer):
    response = client.post("/auth/register", json=test_customer)
    assert response.status_code == 200
    assert "User registered successfully" in response.json()["message"]
    assert response.json()["user"] == test_customer["username"]

def test_register_business_owner_success(client, test_business_owner):
    response = client.post("/auth/register", json=test_business_owner)
    assert response.status_code == 200
    assert "User registered successfully" in response.json()["message"]
    assert response.json()["user"] == test_business_owner["username"]

def test_register_missing_required_fields(client):
    incomplete_data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe"
        # Missing password, phone, and role
    }
    response = client.post("/auth/register", json=incomplete_data)
    assert response.status_code == 422  # Validation error

def test_register_business_owner_without_business_name(client, test_business_owner):
    data = test_business_owner.copy()
    del data["business_name"]
    response = client.post("/auth/register", json=data)
    assert response.status_code == 400
    assert "Business name is required" in response.json()["detail"]

def test_register_duplicate_username(client, test_customer):
    # Register first user
    client.post("/auth/register", json=test_customer)
    
    # Try to register with same username
    data = test_customer.copy()
    data["phone"] = "9999999999"  # Different phone
    response = client.post("/auth/register", json=data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_register_duplicate_phone(client, test_customer):
    # Register first user
    client.post("/auth/register", json=test_customer)
    
    # Try to register with same phone
    data = test_customer.copy()
    data["username"] = "different_username"  # Different username
    response = client.post("/auth/register", json=data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_register_password_hashing(client, test_customer, test_db):
    # Register user
    client.post("/auth/register", json=test_customer)
    
    # Get user from database
    db = TestingSessionLocal()
    user = db.query(User).filter(User.username == test_customer["username"]).first()
    db.close()
    
    # Verify password is hashed
    assert user.password_hash != test_customer["password"]
    assert verify_password(test_customer["password"], user.password_hash)

# Login Tests
def test_login_success(client, test_customer):
    # Register user
    client.post("/auth/register", json=test_customer)
    
    # Login
    response = client.post(
        "/auth/login",
        data={
            "username": test_customer["username"],
            "password": test_customer["password"]
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(client, test_customer):
    # Register user
    client.post("/auth/register", json=test_customer)
    
    # Try to login with wrong password
    response = client.post(
        "/auth/login",
        data={
            "username": test_customer["username"],
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

def test_login_missing_fields(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "johndoe"
            # Missing password
        }
    )
    assert response.status_code == 422  # Validation error

def test_login_empty_credentials(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "",
            "password": ""
        }
    )
    assert response.status_code == 401  # מעדכנים לקוד השגיאה הנכון

def test_invalid_token_format(client):
    response = client.get(
        "/api/shared/me",
        headers={"Authorization": "Invalid token"}
    )
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_expired_token(client):
    # This would require mocking the token creation time
    # Implementation depends on your token expiration mechanism
    pass
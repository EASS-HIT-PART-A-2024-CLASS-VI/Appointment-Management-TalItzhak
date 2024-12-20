import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from app.routes.auth import register, login
from app.schemas import UserCreate, UserLogin
from app.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from pydantic import ValidationError

# ---------------------------- #
# Mock Database Fixture        #
# ---------------------------- #
@pytest.fixture
def mock_db():
    """ 
    Mock SQLAlchemy-like database session.
    Provides methods for querying, adding, and committing users.
    """
    class MockQuery:
        def __init__(self, data):
            self.data = data  # Simulated database data

        def filter(self, condition):
            """
            Simulates SQLAlchemy's filter method.
            Filters users based on a given condition.
            """
            key, value = condition.left.name, condition.right.value
            filtered = [user for user in self.data if getattr(user, key) == value]
            return MockQuery(filtered)

        def first(self):
            """ Returns the first matching result or None. """
            return self.data[0] if self.data else None

    class MockDBSession:
        """
        Simulated database session that mimics SQLAlchemy methods.
        """
        def __init__(self):
            self.users = []  # Simulated list of users

        def query(self, model):
            return MockQuery(self.users)

        def add(self, user):
            """ Adds a user to the simulated database. """
            self.users.append(user)

        def commit(self):
            """ Simulates a commit action. """
            pass

        def refresh(self, user):
            """ Simulates refreshing the user instance. """
            pass

    return MockDBSession()

# ---------------------------- #
# Test Register Endpoint       #
# ---------------------------- #
def test_register_user(mock_db):
    """
    Test registering a new user successfully.
    Verifies that the user is added to the database.
    """
    user_data = UserCreate(
        username="johndoe",
        email="johndoe@example.com",
        password="password123",
        role="customer"
    )
    response = register(user_data, db=mock_db)
    assert response["message"] == "User registered successfully"
    assert response["user"] == "johndoe"
    assert len(mock_db.users) == 1  # Verify the user was added

def test_register_existing_user(mock_db):
    """
    Test registering a user with an already registered email.
    Verifies that the endpoint raises an HTTP 400 error.
    """
    user_data = UserCreate(
        username="johndoe",
        email="johndoe@example.com",
        password="password123",
        role="customer"
    )
    register(user_data, db=mock_db)  # Add the user first
    with pytest.raises(HTTPException) as e:
        register(user_data, db=mock_db)
    assert e.value.status_code == 400
    assert e.value.detail == "Email already registered"

def test_register_invalid_input(mock_db):
    """
    Test registering a user with invalid input (missing role).
    Verifies that Pydantic raises a ValidationError.
    """
    with pytest.raises(ValidationError) as e:
        invalid_user = UserCreate(
            username="janedoe",
            email="janedoe@example.com",
            password="password123",
            role=None
        )
    assert "none is not an allowed value" in str(e.value)

# ---------------------------- #
# Test Login Endpoint          #
# ---------------------------- #
def test_login_success(mock_db):
    """
    Test logging in successfully with valid credentials.
    Verifies that an access token is returned.
    """
    password = "password123"
    hashed_password = get_password_hash(password)
    mock_db.add(Mock(username="johndoe", email="johndoe@example.com", password_hash=hashed_password, role="customer"))

    login_data = UserLogin(username="johndoe", password=password)
    response = login(login_data, db=mock_db)
    assert "access_token" in response
    assert response["token_type"] == "bearer"

def test_login_invalid_username(mock_db):
    """
    Test logging in with an invalid username.
    Verifies that an HTTP 400 error is raised.
    """
    login_data = UserLogin(username="unknown", password="password123")
    with pytest.raises(HTTPException) as e:
        login(login_data, db=mock_db)
    assert e.value.status_code == 400
    assert e.value.detail == "Invalid username or password"

def test_login_invalid_password(mock_db):
    """
    Test logging in with an incorrect password.
    Verifies that an HTTP 400 error is raised.
    """
    password = "password123"
    hashed_password = get_password_hash(password)
    mock_db.add(Mock(username="johndoe", email="johndoe@example.com", password_hash=hashed_password, role="customer"))

    login_data = UserLogin(username="johndoe", password="wrongpassword")
    with pytest.raises(HTTPException) as e:
        login(login_data, db=mock_db)
    assert e.value.status_code == 400
    assert e.value.detail == "Invalid username or password"

def test_login_case_sensitivity(mock_db):
    """
    Test that login is case-sensitive for usernames.
    """
    password = "password123"
    hashed_password = get_password_hash(password)
    mock_db.add(Mock(username="JohnDoe", email="johndoe@example.com", password_hash=hashed_password, role="customer"))

    login_data = UserLogin(username="johndoe", password=password)
    with pytest.raises(HTTPException) as e:
        login(login_data, db=mock_db)
    assert e.value.status_code == 400
    assert e.value.detail == "Invalid username or password"

# ---------------------------- #
# Test Token Generation        #
# ---------------------------- #
def test_token_generation():
    """
    Test that a valid JWT access token is generated.
    Verifies the token is a string and non-empty.
    """
    data = {"sub": "johndoe", "role": "customer"}
    token = create_access_token(data=data, expires_delta=timedelta(minutes=30))
    assert isinstance(token, str)
    assert len(token) > 0

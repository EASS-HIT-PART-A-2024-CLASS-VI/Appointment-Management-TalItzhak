# Appointment Management Backend 🚀

This repository contains the backend for an Appointment Management application built using FastAPI and Docker.
The API supports features such as user authentication, creating, updating, deleting, and retrieving appointments, along with conflict detection, advanced search, and statistics generation.
The project is structured to include separate modules for authentication, shared functionality, and business-specific features, ensuring scalability and maintainability.
---

## Features ✨
- **User Authentication**: Register and log in users with secure password storage and JWT-based authentication.
- **CRUD Operations**: Create, read, update, and delete appointments.  
- **Conflict Detection**: Prevent overlapping appointments.  
- **Advanced Search**: Search appointments by phone number and customer name.  
- **Statistics Generation**: Summarize appointments and calculate total revenue.  
- **Phone Normalization**: Ensures consistent formatting for phone numbers.  
- **Dockerized Deployment**: Easily run the API in a containerized environment.  

**Technologies Used** 🛠  
Language: Python (FastAPI)
Database: SQLite (with SQLAlchemy ORM)
Validation: Pydantic
Authentication: OAuth2 with JWT
Password Hashing: Passlib (bcrypt)
Testing: Pytest
Containerization: Docker
Build System: Uvicorn

---

## Project Structure 📂
```plaintext
backend/
├── app/
│   ├── routes/
│   │   ├── auth.py             # Authentication routes (register, login).
│   │   ├── business_extras.py  # Routes for business-specific features.
│   │   ├── shared.py           # Shared routes for customers and business owners.
│   │   └── __init__.py         # Module initializer for routes.
│   ├── database.py             # Database connection and setup.
│   ├── dependencies.py         # Shared dependencies for routes.
│   ├── models.py               # SQLAlchemy models and in-memory data.
│   ├── schemas.py              # Pydantic models for validation.
│   ├── security.py             # Password hashing and JWT generation.
│   └── utils.py                # Utility functions for common tasks.
├── tests/
│   ├── test_auth.py            # Unit tests for authentication routes.
│   ├── test_business_extras.py # Unit tests for business-specific routes.
│   ├── test_shared.py          # Unit tests for shared routes.
│   └── __init__.py             # Module initializer for tests.
├── create_db.py                # Script to initialize the database.
├── Dockerfile                  # Docker configuration for containerized deployment.
├── requirements.txt            # Python dependencies.
├── .env                        # Environment variables for secure configuration.
└── .gitignore                  # Files and directories to ignore in version control.
ת
```
---

## Setup Instructions ❄️

Prerequisites Before running the application, ensure the following tools are installed:

---

## Docker 🐳  

Python 3.9+ (optional, if running locally without Docker)  


## bash
Copy code git clone https://github.com/your-username/appointment-management.git cd appointment-management Build the Docker image:

bash Copy code docker build -t appointment-management-backend . Run the Docker container:

bash Copy code docker run -d --name appointment-management-backend -p 8000:8000 appointment-management-backend Access the API:

Swagger UI: http://localhost:8000/docs

---

## Running Locally 🚀
Clone the repository:

bash Copy code git clone https://github.com/your-username/appointment-management.git cd appointment-management Install dependencies:

bash Copy code pip install -r requirements.txt Start the application:

bash Copy code uvicorn app.main:app --reload Access the API:

Swagger UI: http://127.0.0.1:8000/docs

---

## API Endpoints 🌐

### Authentication  

| **Method** | **Endpoint**             | **Description**                  |
|------------|--------------------------|----------------------------------|
| POST       | `/api/auth/register/`    | Register a new user.             |
| POST       | `//api/auth/login	/`    | Log in and retrieve a JWT token. |

---

### Shared  

| **Method** | **Endpoint**             | **Description**                         |
|------------|--------------------------|-----------------------------------------|
| POST       | `/api/shared/appointments/`     | Create a new appointment.        |
| PUT        | `/api/shared/appointments/{id}` | Update an existing appointment.  |
| DELETE     | `/api/shared/appointments/{id}` | Delete an appointment.           |
| GET        | `/api/shared/appointments/`     | Retrieve all appointments.       |
| GET        | `/api/shared/appointments/me`   | Get Current User Info            |
| GET        | `/api/shared/appointments/{id}` | Retrieve a specific appointment. |

---

### Business  

| **Method** | **Endpoint**                                       | **Description**                            |
|------------|----------------------------------------------------|--------------------------------------------|
| GET        | `/api/business/shared/appointments/{id}`           | Retrieve a specific appointment.           |
| GET        | `/api/business/shared/appointments/`               | Get list of appointments to specific title.|
| GET        | `/api/business/appointments/search/{phone}/{name}` | Search appointments by phone and name.     |
| GET        | `/api/business/appointments/stats/{date}`          | Retrieve statistics for a given date.      |
| GET        | `/api/business/`                                   | Get all Users                              |


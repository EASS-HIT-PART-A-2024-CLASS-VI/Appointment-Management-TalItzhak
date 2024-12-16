## Appointment Management Backend 📅
This repository contains the backend for an Appointment Management application built using FastAPI and Docker. The API provides features such as creating, updating, deleting, and retrieving appointments, with capabilities like conflict detection, advanced search, and statistics generation.

## Features ✨
CRUD Operations: Create, read, update, and delete appointments.
Conflict Detection: Prevent overlapping appointments.
Advanced Search: Search appointments by phone number and customer name.
Statistics Generation: Summarize appointments and calculate total revenue.
Phone Normalization: Ensures consistent formatting for phone numbers.
Dockerized Deployment: Easily run the API in a containerized environment.
Technologies Used 🛠️
Language: Python (FastAPI)
Containerization: Docker
Validation: Pydantic
Testing: Pytest
Build System: Uvicorn
## Project Structure 📂
plaintext
Copy code
app/
├── main.py          - Entry point for the FastAPI application.
├── routes.py        - API route definitions for managing appointments.
├── models.py        - In-memory data structure for storing appointments.
├── schemas.py       - Pydantic models for data validation.
unit_tests.py        - Unit tests for the FastAPI application.
integration_tests.py - Integration tests for API endpoints.
requirements.txt     - Python dependencies for the project.
Dockerfile           - Docker configuration for containerized deployment.
README.md            - Project documentation.
## Setup Instructions ⚙️
Prerequisites
Before running the application, ensure the following tools are installed:

## Docker
Python 3.9+ (optional, if running locally without Docker)
Using Docker 🐳
Clone the repository:

## bash
Copy code
git clone https://github.com/your-username/appointment-management.git
cd appointment-management
Build the Docker image:

bash
Copy code
docker build -t appointment-management-backend .
Run the Docker container:

bash
Copy code
docker run -d --name appointment-management-backend -p 8000:8000 appointment-management-backend
Access the API:

Swagger UI: http://localhost:8000/docs

## Running Locally 🚀
Clone the repository:

bash
Copy code
git clone https://github.com/your-username/appointment-management.git
cd appointment-management
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Start the application:

bash
Copy code
uvicorn app.main:app --reload
Access the API:


Swagger UI: http://127.0.0.1:8000/docs

## API Endpoints 🌐
Appointments
Method	Endpoint	Description
POST	/api/appointments/	Create a new appointment.
GET	/api/appointments/	Retrieve all appointments.
GET	/api/appointments/{id}	Retrieve a specific appointment.
PUT	/api/appointments/{id}	Update an existing appointment.
DELETE	/api/appointments/{id}	Delete an appointment.
Search
Method	Endpoint	Description
GET	/api/appointments/search/{phone}/{name}	Search appointments by phone and name.
Statistics
Method	Endpoint	Description
GET	/api/appointments/stats/{date}	Retrieve statistics for a given date.

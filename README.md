# 🗓️ Appointment Management System

<img src="screenshots/logo.png" alt="logo" width="650"/>

A full-stack appointment scheduling application built with FastAPI and React, featuring a dark/light theme and role-based access control.

## 🖼️ Screenshots

## Login 
<img src="screenshots/LoginPage.png" alt="Login Page" width="650"/>

## Business Management
<img src="screenshots/business_meetings.png" alt="Business Appointments" width="650"/>
<img src="screenshots/Services_screenshot.png" alt="Services Management" width="650"/>
<img src="screenshots/availability_screenshot.png" alt="Availability Management" width="650"/>

## Customer Features
<img src="screenshots/Create_Meeting.png" alt="Create Meeting" width="650"/>


## ✨ Features

### For Business Owners
- 📅 Manage service availability by day and time
- 💼 Create and manage services with pricing
- 📊 View daily statistics and revenue
- 📋 Export appointments to Excel
- 🔍 Search client appointments by phone number

### For Customers
- 👥 Browse available businesses
- 📅 Book appointments
- ⏰ View business availability
- 📋 Track appointment history

### General Features
- 🧠 Natural language business search
- 🎯 Intelligent service matching
- 🌓 Dark/Light theme toggle
- 🔐 JWT authentication
- 👥 Role-based access control
- 📱 Responsive design
- ⚡ Real-time validation

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.12+
- Node.js 16+
- MySQL 8.0+

### 🐳 Docker Setup (Recommended)

1. Create a `docker-compose.yml` file in the root directory:
   ```yaml
   version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      - db
      - llm_service

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend

  llm_service:
    build: ./llm_service
    ports:
      - "8001:8001"
    volumes:
      - ./llm_service:/app
    environment:
      - HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY}

  db:
    image: mysql:8.0
    environment:
      - MYSQL_DATABASE=appointmentdb
      - MYSQL_USER=appointment_user
      - MYSQL_PASSWORD=appointment_password
      - MYSQL_ROOT_PASSWORD=root_password
    ports:
      - "3307:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
   ```

2. **Run the application:**
  ```bash
  docker-compose up --build


3. Access the application:
- 💻 Frontend: http://localhost:3000
- 🔌 Backend API: http://localhost:8000
- 📚 API Documentation: http://localhost:8000/docs
- 📋 LLM Service: http://localhost:8001



### Manual Setup

'''
## 🏗️ Architecture

### Backend
- **FastAPI**: Modern, fast web framework for building APIs with Python
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **JWT**: Token-based authentication
- **SQLite**: Database (can be easily switched to PostgreSQL)

### Frontend
- **React**: UI library
- **Context API**: State management
- **CSS Modules**: Styling
- **Axios**: HTTP client
- **React Router**: Navigation

### LLM
- **FastAPI**: Dedicated microservice for intelligent search
- **Natural Language Processing:**: Custom keyword extraction
- **Smart Matching**: Business-service relevance scoring

## 📁 Project Structure

├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── models.py
│   │   └── schemas.py
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   └── context/
│   └── Dockerfile
├── llm_service/
│   ├── app/
│   │   └── main.py
│   └── Dockerfile
└── docker-compose.yml

```
## 📝 API Documentation

After running the backend server, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`




## 🌟 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 👏 Acknowledgments

- FastAPI documentation
- React documentation
- SQLAlchemy documentation

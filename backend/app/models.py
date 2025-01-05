from sqlalchemy import Column, Integer, String, DateTime, Time, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, time


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum("business_owner", "customer", name="user_roles"), nullable=False)
    services = relationship("Service", back_populates="owner")  # Relationship to services created by the user
    business_name = Column(String, nullable=True)  # New field
    availability = relationship("Availability", back_populates="owner")



class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    start_time = Column(Time, nullable=False)
    duration = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    type = Column(String, nullable=False)
    cost = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    duration = Column(Integer, nullable=False)  # Duration in minutes
    price = Column(Integer, nullable=False)  # Price of the service
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Link to the business owner
    owner = relationship("User", back_populates="services")  # Define relationship to User
    topics = relationship("Topic", back_populates="service")  # Relationship to related topics


class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)  # Duration in minutes
    cost = Column(Integer, nullable=False)  # Cost of the topic
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)  # Link to the related service
    service = relationship("Service", back_populates="topics")  # Back-reference to Service

class Availability(Base):
    __tablename__ = "availability"
    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String, nullable=False)  # Sunday, Monday, etc.
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="availability")


# Example predefined appointments (optional, for testing purposes)
appointments = {
    1: {
        "date": "2024-01-01T10:00:00",
        "start_time": "10:00",
        "duration": 30,  # Duration in minutes
        "title": "Haircut",
        "customer_name": "John Doe",
        "customer_phone": "123-456-7890",
        "type": "Haircut",
        "cost": 30,
        "notes": "Customer prefers short hair"
    },
    2: {
        "date": "2024-01-02T14:00:00",
        "start_time": "14:00",
        "duration": 60,  # Duration in minutes
        "title": "Hair Color",
        "customer_name": "Jane Smith",
        "customer_phone": "987-654-3210",
        "type": "Coloring",
        "cost": 50,
        "notes": "Use ammonia-free dye"
    }
}

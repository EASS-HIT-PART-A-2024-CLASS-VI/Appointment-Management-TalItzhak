from sqlalchemy import Column, Integer, String, DateTime, Time, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, time

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(Enum("business_owner", "customer", name="user_roles"), nullable=False)
    business_name = Column(String(200), nullable=True)
    services = relationship("Service", back_populates="owner")
    availability = relationship("Availability", back_populates="owner")

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    start_time = Column(Time, nullable=False)
    duration = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    customer_name = Column(String(200), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    type = Column(String(100), nullable=False)
    cost = Column(Integer, nullable=False)
    notes = Column(String(500), nullable=True)

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    duration = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="services")
    topics = relationship("Topic", back_populates="service")

class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    duration = Column(Integer, nullable=False)
    cost = Column(Integer, nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    service = relationship("Service", back_populates="topics")

class Availability(Base):
    __tablename__ = "availability"
    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String(20), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="availability")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(Enum(
        "Rescheduling an Appointment",
        "Canceling an Appointment", 
        "Questions About Services",
        "Payment and Billing Issues",
        "Other Inquiries",
        name="message_titles"
    ), nullable=False)
    content = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)
    
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    recipient = relationship("User", foreign_keys=[recipient_id], backref="received_messages")

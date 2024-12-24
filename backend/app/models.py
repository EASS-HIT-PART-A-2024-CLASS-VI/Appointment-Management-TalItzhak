
from sqlalchemy import Column, Integer, String, Enum
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum("business_owner", "customer", name="user_roles"), nullable=False)




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

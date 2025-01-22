from sqlalchemy import inspect
from app.database import engine, Base
from app.models import User, Appointment, Service, Topic, Availability

def init_db():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if not existing_tables:
        print("No existing tables found. Creating database schema...")
        Base.metadata.create_all(engine)
        print("Database tables created successfully!")
    else:
        print("Database tables already exist. Skipping initialization.")
        print(f"Found tables: {', '.join(existing_tables)}")

if __name__ == "__main__":
    init_db()
from sqlalchemy import inspect, text
from app.database import engine, Base
from app.models import User, Appointment, Service, Topic, Availability, Message

def init_db():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print("Checking database tables...")
    
    if not existing_tables:
        print("No existing tables found. Creating complete database schema...")
        Base.metadata.create_all(engine)
        print("All database tables created successfully!")
    else:
        print(f"Found existing tables: {', '.join(existing_tables)}")
        print("Creating any missing tables...")
        
        # Create tables that don't exist yet
        Base.metadata.create_all(engine, checkfirst=True)
        
        # Verify all tables after creation
        updated_tables = inspector.get_table_names()
        print(f"Current tables after update: {', '.join(updated_tables)}")
        
        if 'messages' in updated_tables:
            print("Messages table successfully created/verified!")
        else:
            print("Warning: Messages table creation may have failed!")

if __name__ == "__main__":
    init_db()
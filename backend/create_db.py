import sys
import os
from time import sleep

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine, wait_for_db
# Import all models to ensure they are registered with SQLAlchemy
from app.models import User, Appointment, Service, Topic, Availability

def init_db():
    retries = 5
    retry_delay = 5

    for i in range(retries):
        try:
            print(f"Attempting to create database (attempt {i + 1}/{retries})...")
            
            # Wait for database to be ready
            if not wait_for_db():
                raise Exception("Database connection timeout")

            # Drop all tables if they exist
            print("Dropping existing tables...")
            Base.metadata.drop_all(bind=engine)
            
            # Create all tables
            print("Creating tables...")
            Base.metadata.create_all(bind=engine)
            
            print("Database tables created successfully!")
            return True
        except Exception as e:
            print(f"Error creating database: {str(e)}")
            if i < retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                sleep(retry_delay)
            else:
                print("Max retries reached. Database creation failed.")
                return False

if __name__ == "__main__":
    init_db()
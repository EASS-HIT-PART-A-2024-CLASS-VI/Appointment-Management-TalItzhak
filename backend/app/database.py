from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import time

# Load .env if it's not already loaded
load_dotenv()

def wait_for_db():
    max_retries = 30
    retry_interval = 1

    for i in range(max_retries):
        try:
            # Test connection
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            with engine.connect() as connection:
                print("Database connection successful!")
            return True
        except Exception as e:
            print(f"Attempt {i + 1}/{max_retries} failed: {e}")
            if i < max_retries - 1:
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
    return False

# Database connection settings
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "appointmentdb")
DB_USER = os.getenv("DB_USER", "appointment_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "appointment_password")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
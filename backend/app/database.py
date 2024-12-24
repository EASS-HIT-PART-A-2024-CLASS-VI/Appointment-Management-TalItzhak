from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# כתובת החיבור למסד הנתונים (SQLITE כדוגמה)
DATABASE_URL = "sqlite:///./sql_app.db"

# יצירת מנוע (Engine) לחיבור למסד הנתונים
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # נדרש עבור SQLite
)

# יצירת מחלקת SessionLocal לניהול סשנים
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# בסיס משותף לכל המודלים במסד הנתונים
Base = declarative_base()

print("Using database at:", os.path.abspath("sql_app.db"))
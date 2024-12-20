import sys
import os

# הוספת הנתיב של backend לנתיב החיפוש של פייתון
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.database import Base, engine
from app.models import User

print("Creating database...")
Base.metadata.create_all(bind=engine)  # Create database tables based on the defined models
print("Database created successfully!")

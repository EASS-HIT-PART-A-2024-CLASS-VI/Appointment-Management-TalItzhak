
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import router as auth_router  # נתיבי Authentication
from app.routes.shared import router as shared_router  # נתיבים משותפים
from app.routes.business_extras import router as business_router  # נתיבים לבעלי עסקים
from app.routes.services import router as services_router
from app.routes.availability import router as availability_router  # Add this line



# יצירת אפליקציית FastAPI
app = FastAPI(title="Appointment Management API", version="1.0.0", description="API for managing appointments.")

# הגדרת CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # מומלץ להחליף בכתובת ספציפית ל-Frontend לפרודקשן
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]  # Add this line


)

# הוספת נתיבי Authentication kkk(התחברות והרשמה)
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# הוספת נתיבים משותפים (משותף ללקוחות ולבעלי עסקים)
app.include_router(shared_router, prefix="/api/shared", tags=["Shared"])

# הוספת נתיבים ייעודיים לבעלי עסקים
app.include_router(business_router, prefix="/api/business", tags=["Business"])

app.include_router(services_router, prefix="/api/services", tags=["Services"])

app.include_router(availability_router, prefix="/api/availability", tags=["Availability"])  # Add this line



# נקודת התחלה להפעלת השרת
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

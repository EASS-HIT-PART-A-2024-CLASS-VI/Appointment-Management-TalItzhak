from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import router as auth_router  # נתיבי Authentication
from app.routes.shared import router as shared_router  # נתיבים משותפים
from app.routes.business_extras import router as business_router  # נתיבים לבעלי עסקים

# יצירת אפליקציית FastAPI
app = FastAPI(title="Appointment Management API", version="1.0.0", description="API for managing appointments.")

# הגדרת CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # מומלץ להחליף בכתובת ספציפית ל-Frontend לפרודקשן
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# הוספת נתיבי Authentication kkk(התחברות והרשמה)
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

# הוספת נתיבים משותפים (משותף ללקוחות ולבעלי עסקים)
app.include_router(shared_router, prefix="/api/shared", tags=["Shared"])

# הוספת נתיבים ייעודיים לבעלי עסקים
app.include_router(business_router, prefix="/api/business", tags=["Business"])

# נקודת התחלה להפעלת השרת
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

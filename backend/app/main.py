from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import router as auth_router  
from app.routes.shared import router as shared_router  
from app.routes.business_extras import router as business_router
from app.routes.services import router as services_router
from app.routes.availability import router as availability_router
from app.routes.messages import router as messages_router


app = FastAPI(
    title="Appointment Management API",
    version="1.0.0",
    description="API for managing appointments"
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only. Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add a root endpoint for health check
@app.get("/")
async def root():
    return {"message": "API is running"}

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(shared_router, prefix="/api/shared", tags=["Shared"])
app.include_router(business_router, prefix="/api/business", tags=["Business"])
app.include_router(services_router, prefix="/api/services", tags=["Services"])
app.include_router(availability_router, prefix="/api/availability", tags=["Availability"])
app.include_router(messages_router, prefix="/api/messages", tags=["Messages"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
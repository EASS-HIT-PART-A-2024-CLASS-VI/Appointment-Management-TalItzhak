from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Appointment Management")

# Include routes
app.include_router(router, prefix="/api", tags=["Appointments"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)

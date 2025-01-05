from fastapi import APIRouter
from app.routes.auth import router as auth_router
from app.routes.shared import router as shared_router
from app.routes.business_extras import router as business_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(shared_router, prefix="/shared", tags=["Shared"])
router.include_router(business_router, prefix="/business", tags=["Business"])




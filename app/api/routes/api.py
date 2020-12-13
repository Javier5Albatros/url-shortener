from fastapi import APIRouter
from app.api.routes import auth, url

router = APIRouter()
router.include_router(auth.router, tags=["auth"])
router.include_router(url.router, tags=["urls"])
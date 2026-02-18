from fastapi import APIRouter

from .endpoints import auth

public_router = APIRouter()

public_router.include_router(auth.router)

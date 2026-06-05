from fastapi import APIRouter

from app.api.user.endpoints import portfolios, tags, transactions, wallets

user_router = APIRouter()

user_router.include_router(portfolios.router)
user_router.include_router(wallets.router)
user_router.include_router(transactions.router)
user_router.include_router(tags.router)

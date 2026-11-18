"""
Aggregates all v1 endpoint routers into a single APIRouter.

New feature modules (auth, tickers, predictions, decisions, chat, reports)
register themselves here as they are implemented in later phases.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health

api_router = APIRouter()
api_router.include_router(health.router)

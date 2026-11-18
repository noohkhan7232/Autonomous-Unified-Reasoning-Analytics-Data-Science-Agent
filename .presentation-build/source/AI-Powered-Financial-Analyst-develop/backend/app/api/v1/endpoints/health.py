"""Liveness/readiness endpoint used by Docker healthchecks and CI smoke tests."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check() -> dict:
    return {"status": "ok"}

"""API router aggregation."""

from fastapi import APIRouter

from app.api import tickets, users

api_router = APIRouter(prefix="/api")
api_router.include_router(users.router)
api_router.include_router(tickets.router)

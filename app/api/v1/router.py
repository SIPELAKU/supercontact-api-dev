from fastapi import APIRouter

from app.api.v1.endpoints import contacts_router, auth_router, users_router, leads_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(leads_router)
api_router.include_router(users_router)
api_router.include_router(contacts_router)
# api_router.include_router(mailing)
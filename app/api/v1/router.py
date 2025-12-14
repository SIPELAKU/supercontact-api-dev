from fastapi import APIRouter

from app.api.v1 import auth_router, users_router, leads_router, pipelines_router, contacts_router, userprofile_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(leads_router)
api_router.include_router(users_router)
api_router.include_router(pipelines_router)
api_router.include_router(contacts_router)
api_router.include_router(userprofile_router)
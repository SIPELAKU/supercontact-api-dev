from fastapi import APIRouter

from app.api.v1 import (
    auth_router,
    users_router,
    leads_router,
    pipelines_router,
    contacts_router,
    products_router,
    quotations_router,
    userprofile_router,
    manage_users_router,
    roles_router,
    permissions_router,
    department_router,
    mailings_router,
    userdevice_router,
    notes_router,
    chat_router,
)

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(leads_router)
api_router.include_router(users_router)
api_router.include_router(pipelines_router)
api_router.include_router(contacts_router)
api_router.include_router(products_router)
api_router.include_router(quotations_router)
api_router.include_router(userprofile_router)
api_router.include_router(manage_users_router)
api_router.include_router(roles_router)
api_router.include_router(permissions_router)
api_router.include_router(department_router)
api_router.include_router(mailings_router)
api_router.include_router(userdevice_router)
api_router.include_router(notes_router)
api_router.include_router(chat_router)

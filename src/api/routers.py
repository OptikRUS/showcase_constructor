from fastapi import APIRouter

from src.api.admin_auth import endpoints as admin_auth
from src.api.common import endpoints as common

root_router = APIRouter()
root_router.include_router(common.router, include_in_schema=False)
root_router.include_router(admin_auth.router)

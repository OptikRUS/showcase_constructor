from fastapi import APIRouter

from src.api.admin_auth import endpoints as admin_auth
from src.api.common import endpoints as common
from src.api.public_config import endpoints as public_config
from src.api.showcases import endpoints as showcases

root_router = APIRouter()
root_router.include_router(common.router, include_in_schema=False)
root_router.include_router(admin_auth.router)
root_router.include_router(public_config.router)
root_router.include_router(showcases.router)

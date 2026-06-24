from datetime import timedelta
from typing import Annotated

from fastapi import Depends, Security
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials

from src.api.auth.schemas import JwtUser
from src.config.settings import settings
from src.core.admin_auth.exceptions import AdminAuthenticationRequiredError

access_security = JwtAccessBearer(
    secret_key=settings.AUTH.SECRET_KEY.get_secret_value(),
    auto_error=False,
    access_expires_delta=timedelta(hours=settings.AUTH.ACCESS_TOKEN_EXPIRE_HOURS),
    refresh_expires_delta=timedelta(days=30),
    algorithm=settings.AUTH.ALGORITHM,
)


async def jwt_user_deps(
    credentials: Annotated[JwtAuthorizationCredentials | None, Security(access_security)],
) -> JwtUser:
    if credentials is None:
        raise AdminAuthenticationRequiredError

    return JwtUser.from_credentials(credentials.subject)


JwtUserDeps = Annotated[JwtUser, Depends(jwt_user_deps)]

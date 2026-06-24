from dishka import Provider, Scope, provide
from fastapi import Request

from src.core.admin_auth.schemas import AdminActorContext


class AdminAuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_admin_context(self, request: Request) -> AdminActorContext:
        return AdminActorContext.from_raw(
            user_id=request.headers.get("X-Admin-User-Id"),
            partner_id=request.headers.get("X-Partner-Id"),
        )

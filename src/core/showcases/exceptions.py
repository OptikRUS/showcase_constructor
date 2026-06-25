from src.core.admin_auth.exceptions import AdminPermissionDeniedError, AdminResourceNotFoundError
from src.core.exceptions import BaseExceptionError


class ShowcaseAccessDeniedError(AdminPermissionDeniedError):
    detail: str = "SHOWCASE_ACCESS_DENIED_ERROR"


class AdminShowcaseNotFoundError(AdminResourceNotFoundError):
    detail: str = "ADMIN_SHOWCASE_NOT_FOUND_ERROR"


class AdminShowcaseDraftBlockNotFoundError(AdminResourceNotFoundError):
    detail: str = "ADMIN_SHOWCASE_DRAFT_BLOCK_NOT_FOUND_ERROR"


class AdminShowcaseDraftOfferNotFoundError(AdminResourceNotFoundError):
    detail: str = "ADMIN_SHOWCASE_DRAFT_OFFER_NOT_FOUND_ERROR"


class AdminShowcasePublicationValidationError(BaseExceptionError):
    detail: str = "ADMIN_SHOWCASE_PUBLICATION_VALIDATION_ERROR"


class PublicShowcaseNotFoundError(BaseExceptionError):
    detail: str = "PUBLIC_SHOWCASE_NOT_FOUND_ERROR"

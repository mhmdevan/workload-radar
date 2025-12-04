from typing import Any, Dict, Optional


class APIError(Exception):
    """Base API error with HTTP status code and optional extra details."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.extra = extra or {}


class ValidationError(APIError):
    """Error for invalid input or payload."""

    def __init__(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=400, extra=extra)


class NotFoundError(APIError):
    """Error for missing resources."""

    def __init__(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=404, extra=extra)

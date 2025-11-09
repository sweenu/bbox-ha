"""Exceptions for Bbox integration."""

from aiobbox.exceptions import (
    BboxApiError,
    BboxAuthError,
    BboxInvalidCredentialsError,
    BboxRateLimitError,
    BboxSessionExpiredError,
    BboxTimeoutError,
    BboxUnauthenticatedError,
)

__all__ = [
    "BboxApiError",
    "BboxAuthError",
    "BboxInvalidCredentialsError",
    "BboxRateLimitError",
    "BboxSessionExpiredError",
    "BboxTimeoutError",
    "BboxUnauthenticatedError",
]

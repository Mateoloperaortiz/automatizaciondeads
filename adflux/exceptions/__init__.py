"""
Excepciones personalizadas para AdFlux.

Este módulo define las excepciones personalizadas utilizadas en AdFlux.
"""

from .base import AdFluxError, AdFluxWarning
from .api import (
    APIError, APIConnectionError, APITimeoutError, APIRateLimitError,
    APIAuthenticationError, APIPermissionError, APIResourceError,
    APIValidationError, APINotFoundError, APIServerError
)
from .database import (
    DatabaseError, DatabaseConnectionError, DatabaseQueryError,
    DatabaseIntegrityError, DatabaseTimeoutError, DatabaseNotFoundError
)
from .validation import (
    ValidationError, InvalidInputError, MissingRequiredFieldError,
    InvalidFormatError, InvalidValueError, InvalidTypeError
)
from .business import (
    BusinessError, ResourceNotFoundError, ResourceAlreadyExistsError,
    ResourceInUseError, OperationNotAllowedError, LimitExceededError
)
from .auth import (
    AuthenticationError, AuthorizationError, TokenExpiredError,
    InvalidTokenError, InvalidCredentialsError, AccountLockedError
)
from .file import (
    FileError, FileNotFoundError, FilePermissionError, FileFormatError,
    FileSizeError, FileUploadError, FileDownloadError
)

__all__ = [
    # Base
    'AdFluxError',
    'AdFluxWarning',
    
    # API
    'APIError',
    'APIConnectionError',
    'APITimeoutError',
    'APIRateLimitError',
    'APIAuthenticationError',
    'APIPermissionError',
    'APIResourceError',
    'APIValidationError',
    'APINotFoundError',
    'APIServerError',
    
    # Database
    'DatabaseError',
    'DatabaseConnectionError',
    'DatabaseQueryError',
    'DatabaseIntegrityError',
    'DatabaseTimeoutError',
    'DatabaseNotFoundError',
    
    # Validation
    'ValidationError',
    'InvalidInputError',
    'MissingRequiredFieldError',
    'InvalidFormatError',
    'InvalidValueError',
    'InvalidTypeError',
    
    # Business
    'BusinessError',
    'ResourceNotFoundError',
    'ResourceAlreadyExistsError',
    'ResourceInUseError',
    'OperationNotAllowedError',
    'LimitExceededError',
    
    # Auth
    'AuthenticationError',
    'AuthorizationError',
    'TokenExpiredError',
    'InvalidTokenError',
    'InvalidCredentialsError',
    'AccountLockedError',
    
    # File
    'FileError',
    'FileNotFoundError',
    'FilePermissionError',
    'FileFormatError',
    'FileSizeError',
    'FileUploadError',
    'FileDownloadError',
]

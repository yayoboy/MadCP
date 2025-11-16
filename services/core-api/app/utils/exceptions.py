"""
MadCP - Custom Exceptions

This module defines custom exceptions used throughout the MadCP application.
Each exception includes appropriate status codes and error messages.

Author: MadCP Team
License: MIT
"""

from typing import Any, Dict, Optional


class MadCPException(Exception):
    """
    Base exception for all MadCP errors.

    All custom exceptions should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize MadCP exception.

        Args:
            message: Human-readable error message
            status_code: HTTP status code
            error_code: Machine-readable error code
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


# ============================================================================
# Configuration Errors
# ============================================================================

class ConfigurationError(MadCPException):
    """Raised when there's a configuration error"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="CONFIGURATION_ERROR",
            details=details,
        )


# ============================================================================
# Authentication & Authorization Errors
# ============================================================================

class AuthenticationError(MadCPException):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(MadCPException):
    """Raised when user lacks required permissions"""

    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


# ============================================================================
# Resource Errors
# ============================================================================

class ResourceNotFoundError(MadCPException):
    """Raised when a requested resource is not found"""

    def __init__(self, resource_type: str, resource_id: Any, details: Optional[Dict[str, Any]] = None):
        message = f"{resource_type} with ID '{resource_id}' not found"
        if details is None:
            details = {}
        details.update({
            "resource_type": resource_type,
            "resource_id": str(resource_id),
        })
        super().__init__(
            message=message,
            status_code=404,
            error_code="RESOURCE_NOT_FOUND",
            details=details,
        )


class ResourceAlreadyExistsError(MadCPException):
    """Raised when trying to create a resource that already exists"""

    def __init__(self, resource_type: str, resource_id: Any, details: Optional[Dict[str, Any]] = None):
        message = f"{resource_type} with ID '{resource_id}' already exists"
        if details is None:
            details = {}
        details.update({
            "resource_type": resource_type,
            "resource_id": str(resource_id),
        })
        super().__init__(
            message=message,
            status_code=409,
            error_code="RESOURCE_ALREADY_EXISTS",
            details=details,
        )


# ============================================================================
# Validation Errors
# ============================================================================

class ValidationError(MadCPException):
    """Raised when input validation fails"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


# ============================================================================
# Database Errors
# ============================================================================

class DatabaseError(MadCPException):
    """Raised when a database operation fails"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details,
        )


# ============================================================================
# Code Analysis Errors
# ============================================================================

class CodeAnalysisError(MadCPException):
    """Raised when code analysis fails"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="CODE_ANALYSIS_ERROR",
            details=details,
        )


class ParsingError(MadCPException):
    """Raised when code parsing fails"""

    def __init__(self, message: str, file_path: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if details is None:
            details = {}
        if file_path:
            details["file_path"] = file_path
        super().__init__(
            message=message,
            status_code=422,
            error_code="PARSING_ERROR",
            details=details,
        )


class UnsupportedLanguageError(MadCPException):
    """Raised when trying to analyze unsupported language"""

    def __init__(self, language: str, supported_languages: list):
        super().__init__(
            message=f"Language '{language}' is not supported",
            status_code=422,
            error_code="UNSUPPORTED_LANGUAGE",
            details={
                "language": language,
                "supported_languages": supported_languages,
            },
        )


# ============================================================================
# LLM & Embedding Errors
# ============================================================================

class LLMError(MadCPException):
    """Raised when LLM API call fails"""

    def __init__(self, message: str, provider: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if details is None:
            details = {}
        if provider:
            details["provider"] = provider
        super().__init__(
            message=message,
            status_code=500,
            error_code="LLM_ERROR",
            details=details,
        )


class EmbeddingError(MadCPException):
    """Raised when embedding generation fails"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="EMBEDDING_ERROR",
            details=details,
        )


# ============================================================================
# Vector Database Errors
# ============================================================================

class VectorDBError(MadCPException):
    """Raised when vector database operation fails"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="VECTOR_DB_ERROR",
            details=details,
        )


# ============================================================================
# Plugin Errors
# ============================================================================

class PluginError(MadCPException):
    """Raised when plugin operation fails"""

    def __init__(self, message: str, plugin_name: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if details is None:
            details = {}
        if plugin_name:
            details["plugin_name"] = plugin_name
        super().__init__(
            message=message,
            status_code=500,
            error_code="PLUGIN_ERROR",
            details=details,
        )


class PluginNotFoundError(MadCPException):
    """Raised when plugin is not found"""

    def __init__(self, plugin_name: str):
        super().__init__(
            message=f"Plugin '{plugin_name}' not found",
            status_code=404,
            error_code="PLUGIN_NOT_FOUND",
            details={"plugin_name": plugin_name},
        )


# ============================================================================
# Rate Limiting Errors
# ============================================================================

class RateLimitExceededError(MadCPException):
    """Raised when rate limit is exceeded"""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        if details is None:
            details = {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
        )


# ============================================================================
# File & Storage Errors
# ============================================================================

class FileError(MadCPException):
    """Raised when file operation fails"""

    def __init__(self, message: str, file_path: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if details is None:
            details = {}
        if file_path:
            details["file_path"] = file_path
        super().__init__(
            message=message,
            status_code=500,
            error_code="FILE_ERROR",
            details=details,
        )


class FileTooLargeError(MadCPException):
    """Raised when file exceeds size limit"""

    def __init__(self, file_size: int, max_size: int, details: Optional[Dict[str, Any]] = None):
        if details is None:
            details = {}
        details.update({
            "file_size": file_size,
            "max_size": max_size,
        })
        super().__init__(
            message=f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)",
            status_code=413,
            error_code="FILE_TOO_LARGE",
            details=details,
        )


# ============================================================================
# Timeout Errors
# ============================================================================

class TimeoutError(MadCPException):
    """Raised when an operation times out"""

    def __init__(self, operation: str, timeout: int, details: Optional[Dict[str, Any]] = None):
        if details is None:
            details = {}
        details.update({
            "operation": operation,
            "timeout": timeout,
        })
        super().__init__(
            message=f"Operation '{operation}' timed out after {timeout} seconds",
            status_code=408,
            error_code="TIMEOUT_ERROR",
            details=details,
        )


# ============================================================================
# External Service Errors
# ============================================================================

class ExternalServiceError(MadCPException):
    """Raised when external service call fails"""

    def __init__(self, service_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        if details is None:
            details = {}
        details["service_name"] = service_name
        super().__init__(
            message=f"{service_name} error: {message}",
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
        )


# ============================================================================
# Export
# ============================================================================

__all__ = [
    "MadCPException",
    "ConfigurationError",
    "AuthenticationError",
    "AuthorizationError",
    "ResourceNotFoundError",
    "ResourceAlreadyExistsError",
    "ValidationError",
    "DatabaseError",
    "CodeAnalysisError",
    "ParsingError",
    "UnsupportedLanguageError",
    "LLMError",
    "EmbeddingError",
    "VectorDBError",
    "PluginError",
    "PluginNotFoundError",
    "RateLimitExceededError",
    "FileError",
    "FileTooLargeError",
    "TimeoutError",
    "ExternalServiceError",
]

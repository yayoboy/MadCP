"""
MadCP - Configuration Management

This module handles all application configuration using Pydantic Settings.
It supports loading configuration from:
- Environment variables
- .env files
- YAML configuration files
- Default values

Author: MadCP Team
License: MIT
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.

    Attributes are automatically populated from environment variables
    with the same name (case-insensitive).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ========================================================================
    # Application Settings
    # ========================================================================
    APP_NAME: str = Field(default="MadCP", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    APP_ENV: str = Field(default="development", description="Environment (development, production, testing)")
    DEBUG: bool = Field(default=True, description="Debug mode")

    # ========================================================================
    # Server Configuration
    # ========================================================================
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=1, description="Number of worker processes")

    # ========================================================================
    # CORS Configuration
    # ========================================================================
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="Allowed hosts"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from comma-separated string or list"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v

    # ========================================================================
    # Database - PostgreSQL
    # ========================================================================
    DATABASE_URL: str = Field(
        default="postgresql://madcp:madcp_password@localhost:5432/madcp",
        description="PostgreSQL connection string"
    )
    DB_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="Max overflow for connection pool")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Connection pool timeout")
    DB_POOL_RECYCLE: int = Field(default=3600, description="Connection pool recycle time")

    # ========================================================================
    # Redis
    # ========================================================================
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string"
    )
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_MAX_CONNECTIONS: int = Field(default=50, description="Redis max connections")
    CACHE_TTL: int = Field(default=3600, description="Default cache TTL in seconds")

    # ========================================================================
    # Vector Database - Qdrant
    # ========================================================================
    QDRANT_URL: str = Field(
        default="http://localhost:6333",
        description="Qdrant connection URL"
    )
    QDRANT_COLLECTION_NAME: str = Field(
        default="madcp_embeddings",
        description="Qdrant collection name"
    )
    QDRANT_VECTOR_SIZE: int = Field(default=1536, description="Vector dimension size")

    # ========================================================================
    # LLM Configuration
    # ========================================================================
    LLM_PROVIDER: str = Field(
        default="openai",
        description="LLM provider (openai, anthropic, local)"
    )

    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", description="OpenAI model")
    OPENAI_MAX_TOKENS: int = Field(default=4096, description="Max tokens for OpenAI")
    OPENAI_TEMPERATURE: float = Field(default=0.7, description="Temperature for OpenAI")

    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="Anthropic API key")
    ANTHROPIC_MODEL: str = Field(
        default="claude-3-opus-20240229",
        description="Anthropic model"
    )

    # ========================================================================
    # Embeddings
    # ========================================================================
    EMBEDDING_PROVIDER: str = Field(
        default="openai",
        description="Embedding provider (openai, huggingface, local)"
    )
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model"
    )
    EMBEDDING_BATCH_SIZE: int = Field(default=100, description="Batch size for embeddings")

    # ========================================================================
    # Security
    # ========================================================================
    JWT_SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        description="JWT secret key"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration in minutes"
    )

    # OAuth2
    OAUTH2_ENABLED: bool = Field(default=False, description="Enable OAuth2")
    OAUTH2_CLIENT_ID: Optional[str] = Field(default=None, description="OAuth2 client ID")
    OAUTH2_CLIENT_SECRET: Optional[str] = Field(default=None, description="OAuth2 client secret")

    # ========================================================================
    # Code Analysis
    # ========================================================================
    SUPPORTED_LANGUAGES: List[str] = Field(
        default=["python", "javascript", "typescript", "go", "java"],
        description="Supported programming languages"
    )
    MAX_FILE_SIZE_MB: int = Field(default=10, description="Max file size in MB")
    ANALYSIS_TIMEOUT: int = Field(default=300, description="Analysis timeout in seconds")

    @field_validator("SUPPORTED_LANGUAGES", mode="before")
    @classmethod
    def parse_languages(cls, v):
        """Parse supported languages from comma-separated string or list"""
        if isinstance(v, str):
            return [lang.strip() for lang in v.split(",")]
        return v

    # ========================================================================
    # Plugins
    # ========================================================================
    PLUGINS_ENABLED: bool = Field(default=True, description="Enable plugins")
    PLUGINS_DIR: str = Field(default="./plugins", description="Plugins directory")
    PLUGINS_AUTO_RELOAD: bool = Field(default=True, description="Auto-reload plugins")

    # ========================================================================
    # Observability
    # ========================================================================
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json, text)")

    PROMETHEUS_ENABLED: bool = Field(default=True, description="Enable Prometheus metrics")

    SENTRY_ENABLED: bool = Field(default=False, description="Enable Sentry error tracking")
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN")

    # ========================================================================
    # Storage
    # ========================================================================
    STORAGE_BACKEND: str = Field(
        default="local",
        description="Storage backend (local, s3, minio)"
    )
    STORAGE_LOCAL_PATH: str = Field(
        default="/app/data/storage",
        description="Local storage path"
    )

    # ========================================================================
    # Performance
    # ========================================================================
    MAX_CONCURRENT_REQUESTS: int = Field(
        default=100,
        description="Max concurrent requests"
    )
    REQUEST_TIMEOUT: int = Field(default=30, description="Request timeout in seconds")

    # ========================================================================
    # Feature Flags
    # ========================================================================
    FEATURE_SEMANTIC_SEARCH: bool = Field(default=True, description="Enable semantic search")
    FEATURE_CODE_ANALYSIS: bool = Field(default=True, description="Enable code analysis")
    FEATURE_AI_ASSISTANCE: bool = Field(default=True, description="Enable AI assistance")
    FEATURE_PLANNING: bool = Field(default=True, description="Enable planning features")

    # ========================================================================
    # Methods
    # ========================================================================

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.APP_ENV.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.APP_ENV.lower() == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.APP_ENV.lower() == "testing"

    def get_database_url(self, hide_password: bool = False) -> str:
        """
        Get database URL with optional password masking.

        Args:
            hide_password: If True, mask the password in the URL

        Returns:
            Database URL string
        """
        if not hide_password:
            return self.DATABASE_URL

        # Mask password in URL
        import re
        return re.sub(r':([^:@]+)@', ':***@', self.DATABASE_URL)


# ============================================================================
# Cache Settings Instance
# ============================================================================

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    This function uses lru_cache to ensure settings are only loaded once
    and reused across the application.

    Returns:
        Settings instance
    """
    return Settings()


# ============================================================================
# Utility Functions
# ============================================================================

def reload_settings():
    """
    Force reload of settings.
    Useful for testing or when configuration changes.
    """
    get_settings.cache_clear()
    return get_settings()


# ============================================================================
# Validation
# ============================================================================

def validate_settings():
    """
    Validate critical settings at startup.
    Raises exceptions if required settings are missing or invalid.
    """
    settings = get_settings()

    # Check required API keys based on provider
    if settings.LLM_PROVIDER == "openai" and not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")

    if settings.LLM_PROVIDER == "anthropic" and not settings.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic provider")

    # Check database URL
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL is required")

    # Warn about development secrets in production
    if settings.is_production:
        if settings.JWT_SECRET_KEY == "dev-secret-key-change-in-production":
            raise ValueError(
                "You must set a secure JWT_SECRET_KEY in production! "
                "Current value is the default development secret."
            )

        if settings.DEBUG:
            import warnings
            warnings.warn(
                "DEBUG is enabled in production. This should be disabled for security.",
                UserWarning
            )

    return True


# ============================================================================
# Export
# ============================================================================

__all__ = [
    "Settings",
    "get_settings",
    "reload_settings",
    "validate_settings",
]

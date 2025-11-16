"""
MadCP - Logging Configuration

Configures structured logging for the application with support for:
- JSON and text formats
- Different log levels per environment
- Request tracing
- Performance logging

Author: MadCP Team
License: MIT
"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict

import structlog
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that adds additional context to log records.
    """

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any]
    ) -> None:
        """
        Add custom fields to the log record.

        Args:
            log_record: The log record dict to modify
            record: The original logging.LogRecord
            message_dict: Message dictionary
        """
        super().add_fields(log_record, record, message_dict)

        # Add timestamp
        if not log_record.get("timestamp"):
            log_record["timestamp"] = datetime.utcnow().isoformat()

        # Add log level
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname

        # Add logger name
        log_record["logger"] = record.name

        # Add module and function info
        log_record["module"] = record.module
        log_record["function"] = record.funcName

        # Add line number
        log_record["line"] = record.lineno


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """
    Setup logging configuration for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json or text)
    """
    from app.config import get_settings

    settings = get_settings()

    # Get log level from settings if not provided
    if not log_level:
        log_level = settings.LOG_LEVEL

    # Get log format from settings if not provided
    if not log_format:
        log_format = settings.LOG_FORMAT

    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    root_logger.handlers = []

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)

    # Set formatter based on format type
    if log_format.lower() == "json":
        # JSON formatter for structured logging
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s",
            rename_fields={
                "levelname": "level",
                "name": "logger",
            }
        )
    else:
        # Text formatter for human-readable logs
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Configure structlog (for structured logging)
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Set log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.INFO)

    # Log initial message
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured - Level: {log_level}, Format: {log_format}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# ============================================================================
# Performance Logging
# ============================================================================

def log_performance(func):
    """
    Decorator to log function execution time.

    Usage:
        @log_performance
        def my_function():
            pass
    """
    import functools
    import time

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()

        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(
                f"Function {func.__name__} executed in {execution_time:.4f}s",
                extra={
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "module": func.__module__,
                }
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Function {func.__name__} failed after {execution_time:.4f}s: {str(e)}",
                extra={
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "error": str(e),
                    "module": func.__module__,
                },
                exc_info=True
            )
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(
                f"Function {func.__name__} executed in {execution_time:.4f}s",
                extra={
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "module": func.__module__,
                }
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Function {func.__name__} failed after {execution_time:.4f}s: {str(e)}",
                extra={
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "error": str(e),
                    "module": func.__module__,
                },
                exc_info=True
            )
            raise

    # Return appropriate wrapper based on function type
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# ============================================================================
# Export
# ============================================================================

__all__ = [
    "setup_logging",
    "get_logger",
    "log_performance",
]

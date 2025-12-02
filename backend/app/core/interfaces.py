"""Core interfaces for Result pattern."""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, TypeVar, Generic


class ResultStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"


T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    """Result pattern for explicit error handling.

    Usage:
        result = service.do_something()
        if result.is_success:
            data = result.value
        else:
            handle_error(result.error)
    """
    status: ResultStatus
    value: Optional[T] = None
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    @property
    def is_success(self) -> bool:
        return self.status == ResultStatus.SUCCESS

    @property
    def is_error(self) -> bool:
        return self.status != ResultStatus.SUCCESS

    @classmethod
    def success(cls, value: T, details: Optional[Dict[str, Any]] = None) -> "Result[T]":
        return cls(status=ResultStatus.SUCCESS, value=value, details=details)

    @classmethod
    def failure(cls, error: str, details: Optional[Dict[str, Any]] = None) -> "Result[T]":
        return cls(status=ResultStatus.ERROR, error=error, details=details)

    @classmethod
    def validation_error(cls, error: str, details: Optional[Dict[str, Any]] = None) -> "Result[T]":
        return cls(status=ResultStatus.VALIDATION_ERROR, error=error, details=details)

    @classmethod
    def not_found(cls, error: str = "Resource not found") -> "Result[T]":
        return cls(status=ResultStatus.NOT_FOUND, error=error)

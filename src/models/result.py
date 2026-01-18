"""Result type for success/failure handling."""
from typing import TypeVar, Generic, Optional

T = TypeVar('T')
E = TypeVar('E')


class Result(Generic[T, E]):
    """
    Simple result type for success/failure handling.

    Usage:
        result = Result.ok(value)  # Success
        result = Result.err(error)  # Failure

        if result.is_ok():
            value = result.unwrap()
        else:
            error = result.unwrap_err()
    """

    def __init__(self, value: Optional[T] = None, error: Optional[E] = None, is_success: bool = True):
        self._value = value
        self._error = error
        self._is_success = is_success

    @staticmethod
    def ok(value: T) -> 'Result[T, E]':
        """Create a successful result with the given value."""
        return Result(value=value, error=None, is_success=True)

    @staticmethod
    def err(error: E) -> 'Result[T, E]':
        """Create a failure result with the given error."""
        return Result(value=None, error=error, is_success=False)

    def is_ok(self) -> bool:
        """Return True if this is a successful result."""
        return self._is_success

    def is_err(self) -> bool:
        """Return True if this is a failure result."""
        return not self._is_success

    def unwrap(self) -> T:
        """
        Return the success value.

        Raises:
            ValueError: If this is an error result.
        """
        if not self._is_success:
            raise ValueError(f"Called unwrap() on an error result: {self._error}")
        return self._value

    def unwrap_err(self) -> E:
        """
        Return the error value.

        Raises:
            ValueError: If this is a success result.
        """
        if self._is_success:
            raise ValueError(f"Called unwrap_err() on a success result: {self._value}")
        return self._error

    def unwrap_or(self, default: T) -> T:
        """Return the success value or a default if this is an error."""
        return self._value if self._is_success else default

    def __repr__(self) -> str:
        if self._is_success:
            return f"Ok({self._value!r})"
        return f"Err({self._error!r})"

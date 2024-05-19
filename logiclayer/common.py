import inspect
from typing import Any, Awaitable, Callable, Coroutine, TypeVar, Union

T = TypeVar("T")
CallableMayReturnAwaitable = Callable[..., Union[T, Awaitable[T]]]
CallableMayReturnCoroutine = Callable[..., Union[T, Coroutine[Any, Any, T]]]

LOGICLAYER_METHOD_ATTR = "_llmethod"


class LogicLayerException(Exception):
    """Common base class for exceptions in the LogicLayer package."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


async def _await_for_it(check: CallableMayReturnAwaitable[Any]) -> Any:
    """Wraps a function, which might be synchronous or asynchronous, into an
    asynchronous function, which returns the value wrapped in a coroutine.
    """
    result = check()
    if inspect.isawaitable(result):
        return await result
    return result

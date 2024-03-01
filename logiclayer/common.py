import inspect
from typing import Any, Awaitable, Callable, Coroutine, TypeVar, Union

T = TypeVar("T")
CallableMayReturnAwaitable = Callable[..., Union[T, Awaitable[T]]]
CallableMayReturnCoroutine = Callable[..., Union[T, Coroutine[Any, Any, T]]]

LOGICLAYER_METHOD_ATTR = "_llmethod"


async def _await_for_it(check: CallableMayReturnAwaitable[Any]) -> Any:
    """Wraps a function, which might be synchronous or asynchronous, into an
    asynchronous function, which returns the value wrapped in a coroutine.
    """
    result = check()
    if inspect.isawaitable(result):
        return await result
    return result

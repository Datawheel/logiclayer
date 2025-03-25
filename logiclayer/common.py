from __future__ import annotations

import inspect
from collections.abc import Awaitable, Coroutine
from typing import Any, Callable, TypeVar, Union

from typing_extensions import ParamSpec

T = TypeVar("T")
C = TypeVar("C", bound=Callable)
P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)

CallableMayReturnAwaitable = Callable[P, Union[R_co, Awaitable[R_co]]]
CallableMayReturnCoroutine = Callable[P, Union[R_co, Coroutine[Any, Any, R_co]]]

LOGICLAYER_METHOD_ATTR = "_llmethod"


class LogicLayerException(Exception):
    """Common base class for exceptions in the LogicLayer package."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


async def _await_for_it(
    check: Callable[P, R_co | Awaitable[R_co]],
    *args: P.args,
    **kwargs: P.kwargs,
) -> R_co:
    """Wrap any function, sync or async, into an async function.

    Wraps a function, which might be synchronous or asynchronous, into an
    asynchronous function, which returns the value wrapped in a coroutine.
    """
    result = check(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result

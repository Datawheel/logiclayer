from __future__ import annotations

from collections.abc import Sequence
from typing import Callable, Optional, TypeVar

from fastapi.params import Depends
from fastapi.responses import Response

from .common import LOGICLAYER_METHOD_ATTR
from .module import MethodType, ModuleMethod

C = TypeVar("C", bound=Callable)


def exception_handler(exc: type[Exception], *, debug: bool = False) -> Callable[[C], C]:
    """Decorate a function to flag it as an exception handler for the Module."""

    def exception_handler_decorator(fn: C) -> C:
        method = ModuleMethod(
            MethodType.EXCEPTION_HANDLER,
            debug_only=debug,
            func=fn,
            kwargs={"exception": exc},
        )
        setattr(fn, LOGICLAYER_METHOD_ATTR, method)
        return fn

    return exception_handler_decorator


def healthcheck(func: C) -> C:
    """Decorate a function to flag it as a healthcheck for the module."""
    method = ModuleMethod(MethodType.HEALTHCHECK, func=func)
    setattr(func, LOGICLAYER_METHOD_ATTR, method)
    return func


def on_startup(func: C | None, *, debug: bool = False) -> Callable[[C], C]:
    """Decorate a function to flag it as a startup handler."""

    def startup_decorator(fn: C) -> C:
        method = ModuleMethod(MethodType.EVENT_STARTUP, debug_only=debug, func=fn)
        setattr(fn, LOGICLAYER_METHOD_ATTR, method)
        return fn

    return startup_decorator if func is None else startup_decorator(func)


def on_shutdown(func: C | None, *, debug: bool = False) -> Callable[[C], C]:
    """Decorate a function to flag it as a shutdown handler."""

    def shutdown_decorator(fn: C) -> C:
        method = ModuleMethod(MethodType.EVENT_SHUTDOWN, debug_only=debug, func=fn)
        setattr(fn, LOGICLAYER_METHOD_ATTR, method)
        return fn

    return shutdown_decorator if func is None else shutdown_decorator(func)


def route(
    methods: str | set[str] | Sequence[str],
    path: str,
    *,
    debug: bool = False,
    dependencies: Optional[Sequence[Depends]] = None,
    deprecated: Optional[bool] = None,
    description: Optional[str] = None,
    include_in_schema: bool = True,
    name: Optional[str] = None,
    response_class: Optional[type[Response]] = None,
    status_code: Optional[int] = None,
    summary: Optional[str] = None,
    **kwargs,
) -> Callable[[C], C]:
    """Decorate a function to flag it as a route of the module."""
    kwargs.update(
        methods={methods} if isinstance(methods, str) else set(methods),
        dependencies=dependencies,
        deprecated=deprecated,
        description=description,
        include_in_schema=include_in_schema,
        name=name,
        status_code=status_code,
        summary=summary,
    )

    if response_class is not None:
        kwargs["response_class"] = response_class

    def route_decorator(fn: C) -> C:
        method = ModuleMethod(MethodType.ROUTE, debug_only=debug, func=fn, kwargs=kwargs, path=path)
        setattr(fn, LOGICLAYER_METHOD_ATTR, method)
        return fn

    return route_decorator

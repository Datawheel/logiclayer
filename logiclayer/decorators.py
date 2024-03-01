from typing import Any, Callable, Optional, Sequence, Set, Type, TypeVar, Union

from fastapi.params import Depends
from fastapi.responses import Response

from .common import LOGICLAYER_METHOD_ATTR, CallableMayReturnCoroutine
from .module import MethodType, ModuleMethod

C = TypeVar("C", bound=Callable[..., Any])


def exception_handler(exc: Type[Exception], *, debug: bool = False):
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


def healthcheck(func: CallableMayReturnCoroutine[bool]):
    method = ModuleMethod(MethodType.HEALTHCHECK, func=func)
    setattr(func, LOGICLAYER_METHOD_ATTR, method)
    return func


def on_startup(func: Optional[C], *, debug: bool = False):
    def startup_decorator(fn: C) -> C:
        method = ModuleMethod(MethodType.EVENT_STARTUP, debug_only=debug, func=fn)
        setattr(fn, LOGICLAYER_METHOD_ATTR, method)
        return fn

    return startup_decorator if func is None else startup_decorator(func)


def on_shutdown(func: Optional[C], *, debug: bool = False):
    def shutdown_decorator(fn: C) -> C:
        method = ModuleMethod(MethodType.EVENT_SHUTDOWN, debug_only=debug, func=fn)
        setattr(fn, LOGICLAYER_METHOD_ATTR, method)
        return fn

    return shutdown_decorator if func is None else shutdown_decorator(func)


def route(
    methods: Union[str, Set[str], Sequence[str]],
    path: str,
    *,
    debug: bool = False,
    dependencies: Optional[Sequence[Depends]] = None,
    deprecated: Optional[bool] = None,
    description: Optional[str] = None,
    include_in_schema: bool = True,
    name: Optional[str] = None,
    response_class: Optional[Type[Response]] = None,
    status_code: Optional[int] = None,
    summary: Optional[str] = None,
    **kwargs,
):
    kwargs.update(
        methods=set([methods]) if isinstance(methods, str) else set(methods),
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
        method = ModuleMethod(
            MethodType.ROUTE, debug_only=debug, func=fn, kwargs=kwargs, path=path
        )
        setattr(fn, LOGICLAYER_METHOD_ATTR, method)
        return fn

    return route_decorator

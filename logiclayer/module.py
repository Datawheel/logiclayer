from __future__ import annotations

import dataclasses as dcls
from collections import defaultdict
from collections.abc import Generator
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Union

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from .auth import AuthProvider, VoidAuthProvider
from .common import LOGICLAYER_METHOD_ATTR, CallableMayReturnCoroutine

if TYPE_CHECKING:
    from .logiclayer import LogicLayer


class MethodType(Enum):
    EVENT_SHUTDOWN = auto()
    EVENT_STARTUP = auto()
    EXCEPTION_HANDLER = auto()
    HEALTHCHECK = auto()
    ROUTE = auto()


@dcls.dataclass
class ModuleMethod:
    kind: MethodType
    func: CallableMayReturnCoroutine[..., Any]
    debug_only: bool = False
    kwargs: dict[str, Any] = dcls.field(default_factory=dict)
    path: str = ""

    def bound_to(self, instance: LogicLayerModule) -> CallableMayReturnCoroutine[..., Any]:
        """Retrieve the function bound to the LogicLayerModule.

        Returns the function bound to the instance of the LogicLayerModule subclass
        that matches the name of the original function. This bound function doesn't
        contain the 'self' parameter in its arguments.
        """
        name = self.func.__name__
        func = getattr(instance, name)

        if func.__func__ != self.func:
            msg = (f"Bound function '{name}' doesn't match the original method of the Module",)
            raise ValueError(msg)

        return func


class ModuleMeta(type):
    """Base LogicLayer Module Metaclass."""

    def __new__(
        cls,
        clsname: str,
        supercls: tuple[type, ...],
        attrdict: dict[str, Any],
    ):
        methods: defaultdict[MethodType, list[ModuleMethod]] = defaultdict(list)
        for item in attrdict.values():
            try:
                method: ModuleMethod = getattr(item, LOGICLAYER_METHOD_ATTR)
                methods[method.kind].append(method)
            except AttributeError:  # noqa: PERF203
                pass

        attrdict["_llexceptions"] = {
            item.kwargs["exception"]: item for item in methods[MethodType.EXCEPTION_HANDLER]
        }
        attrdict["_llhealthchecks"] = tuple(methods[MethodType.HEALTHCHECK])
        attrdict["_llroutes"] = tuple(methods[MethodType.ROUTE])
        attrdict["_llshutdown"] = tuple(methods[MethodType.EVENT_SHUTDOWN])
        attrdict["_llstartup"] = tuple(methods[MethodType.EVENT_STARTUP])

        return super(ModuleMeta, cls).__new__(cls, clsname, supercls, attrdict)


class LogicLayerModule(metaclass=ModuleMeta):
    """Base class for LogicLayer Modules.

    Modules must inherit from this class to be used in LogicLayer.
    Routes can be set using the provided decorators on any instance method.
    """

    auth: AuthProvider
    router: APIRouter
    _llexceptions: dict[type[Exception], ModuleMethod]
    _llhealthchecks: tuple[ModuleMethod, ...]
    _llroutes: tuple[ModuleMethod, ...]
    _llshutdown: tuple[ModuleMethod, ...]
    _llstartup: tuple[ModuleMethod, ...]

    def __init__(self, *, auth: AuthProvider | None = None, debug: bool = False, **kwargs):
        self.auth = auth or VoidAuthProvider()
        self.debug = debug
        self.router = APIRouter(**kwargs, tags=[self.name])

    @property
    def name(self) -> str:
        """Return the name of this module."""
        return type(self).__name__

    @property
    def route_paths(self) -> Generator[str, None, None]:
        """Yields the route paths configured in this module."""
        return (item.path for item in self._llroutes)

    def include_into(self, layer: LogicLayer, **kwargs) -> None:
        """Configure this Module instance into the provided LogicLayer."""
        app = layer.app
        router = self.router

        for exc_cls, method in self._llexceptions.items():
            app.add_exception_handler(exc_cls, method.bound_to(self))

        for item in self._llhealthchecks:
            layer.add_check(item.bound_to(self))

        router.on_startup.extend(item.bound_to(self) for item in self._llstartup)
        router.on_shutdown.extend(item.bound_to(self) for item in self._llshutdown)

        for item in self._llroutes:
            if item.debug_only and not self.debug:
                continue
            router.add_api_route(item.path, item.bound_to(self), **item.kwargs)

        app.include_router(router, **kwargs)


class ModuleStatus(BaseModel):
    """Common class to describe the status of the resources related to a Module."""

    model_config = ConfigDict(extra="allow", frozen=True)

    module: str
    version: str
    debug: Union[bool, dict[str, Any]]
    status: str

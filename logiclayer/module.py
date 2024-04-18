import dataclasses as dcls
from collections import defaultdict
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Type, Union

from fastapi import APIRouter

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
    func: CallableMayReturnCoroutine[Any]
    debug_only: bool = False
    kwargs: Dict[str, Any] = dcls.field(default_factory=dict)
    path: str = ""

    def bound_to(self, instance: "LogicLayerModule") -> CallableMayReturnCoroutine[Any]:
        """Returns the bound function belonging to the instance of the
        LogicLayerModule subclass that matches the name of the original function.

        This bound function doesn't contain the 'self' parameter in its arguments.
        """
        name = self.func.__name__
        func = getattr(instance, name)
        if func.__func__ != self.func:
            raise ValueError(
                f"Bound function '{name}' doesn't match the original method of the Module"
            )
        return func


class ModuleMeta(type):
    """Base LogicLayer Module Metaclass."""

    def __new__(
        cls, clsname: str, supercls: Tuple[type, ...], attrdict: Dict[str, Any]
    ):
        methods: defaultdict[MethodType, list[ModuleMethod]] = defaultdict(list)
        for item in attrdict.values():
            try:
                method: ModuleMethod = getattr(item, LOGICLAYER_METHOD_ATTR)
                methods[method.kind].append(method)
            except AttributeError:
                pass

        attrdict["_llexceptions"] = {
            item.kwargs["exception"]: item
            for item in methods[MethodType.EXCEPTION_HANDLER]
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
    _llexceptions: Dict[Type[Exception], ModuleMethod]
    _llhealthchecks: Tuple[ModuleMethod, ...]
    _llroutes: Tuple[ModuleMethod, ...]
    _llshutdown: Tuple[ModuleMethod, ...]
    _llstartup: Tuple[ModuleMethod, ...]

    def __init__(
        self, *, auth: Optional[AuthProvider] = None, debug: bool = False, **kwargs
    ):
        self.auth = auth or VoidAuthProvider()
        self.debug = debug
        self.router = APIRouter(**kwargs)

    @property
    def name(self):
        return type(self).__name__

    @property
    def route_paths(self):
        return (item.path for item in self._llroutes)

    def include_into(self, layer: "LogicLayer", **kwargs):
        app = layer.app
        router = self.router

        for exc_cls, method in self._llexceptions.items():
            app.add_exception_handler(exc_cls, method.bound_to(self))

        for item in self._llhealthchecks:
            layer.add_check(item.bound_to(self))

        router.on_startup.extend(item.bound_to(self) for item in self._llstartup)
        router.on_shutdown.extend(item.bound_to(self) for item in self._llshutdown)

        for item in self._llroutes:
            router.add_api_route(item.path, item.bound_to(self), **item.kwargs)

        app.include_router(router, **kwargs)


@dcls.dataclass
class ModuleStatus:
    module: str
    version: str
    debug: Union[bool, dict]
    extras: dict

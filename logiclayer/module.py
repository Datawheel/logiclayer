import dataclasses
from collections import defaultdict
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Dict, Tuple, Type

from fastapi import APIRouter

from .common import LOGICLAYER_METHOD_ATTR, CallableMayReturnCoroutine

if TYPE_CHECKING:
    from .logiclayer import LogicLayer


class MethodType(Enum):
    EVENT_SHUTDOWN = auto()
    EVENT_STARTUP = auto()
    EXCEPTION_HANDLER = auto()
    HEALTHCHECK = auto()
    ROUTE = auto()


@dataclasses.dataclass
class ModuleMethod:
    kind: MethodType
    func: CallableMayReturnCoroutine[Any]
    debug: bool = False
    kwargs: Dict[str, Any] = dataclasses.field(default_factory=dict)
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

    _llexceptions: Dict[Type[Exception], ModuleMethod]
    _llhealthchecks: Tuple[ModuleMethod, ...]
    _llroutes: Tuple[ModuleMethod, ...]
    _llshutdown: Tuple[ModuleMethod, ...]
    _llstartup: Tuple[ModuleMethod, ...]

    def __init__(self, debug: bool = False, **kwargs):
        router = APIRouter(**kwargs)

        router.on_startup.extend(item.bound_to(self) for item in self._llstartup)
        router.on_shutdown.extend(item.bound_to(self) for item in self._llshutdown)

        for item in self._llroutes:
            func = item.bound_to(self)
            router.add_api_route(item.path, func, **item.kwargs)

        self.debug = debug
        self.router = router

    @property
    def route_paths(self):
        return (item.path for item in self._llroutes)

    @property
    def exception_handlers(self):
        return (
            (exc_cls, method.bound_to(self))
            for exc_cls, method in self._llexceptions.items()
        )

    async def _llhealthcheck(self) -> bool:
        try:
            gen = (_await_for_it(item.func) for item in self._llhealthchecks)
            result = await asyncio.gather(*gen)
            return all(item is True for item in result)
        except Exception:
            return False

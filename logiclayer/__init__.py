"""LogicLayer module."""

__title__ = "logiclayer"
__description__ = (
    "A framework to quickly compose and use multiple functionalities as endpoints."
)
__version__ = "0.4.0"

__all__ = (
    "AuthProvider",
    "AuthToken",
    "AuthTokenType",
    "exception_handler",
    "healthcheck",
    "LogicLayer",
    "LogicLayerException",
    "LogicLayerModule",
    "ModuleStatus",
    "NotAuthorized",
    "on_shutdown",
    "on_startup",
    "route",
)

from .auth import AuthProvider, AuthToken, AuthTokenType, NotAuthorized
from .common import LogicLayerException
from .decorators import exception_handler, healthcheck, on_shutdown, on_startup, route
from .logiclayer import LogicLayer
from .module import LogicLayerModule, ModuleStatus

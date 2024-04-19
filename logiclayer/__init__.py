"""LogicLayer module."""

__title__ = "logiclayer"
__description__ = (
    "A framework to quickly compose and use multiple functionalities as endpoints."
)
__version__ = "0.3.3"

__all__ = (
    "AuthProvider",
    "AuthToken",
    "AuthTokenType",
    "exception_handler",
    "healthcheck",
    "LogicLayer",
    "LogicLayerModule",
    "ModuleStatus",
    "on_shutdown",
    "on_startup",
    "route",
)

from .auth import AuthProvider, AuthToken, AuthTokenType
from .decorators import exception_handler, healthcheck, on_shutdown, on_startup, route
from .logiclayer import LogicLayer
from .module import LogicLayerModule, ModuleStatus

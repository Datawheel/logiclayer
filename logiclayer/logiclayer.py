"""LogicLayer class module.

Contains the main definitions for the LogicLayer class.
"""

import asyncio
from inspect import isawaitable
from typing import Any, Callable, Coroutine, Dict, List, Union

from fastapi import APIRouter, FastAPI
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

from logiclayer.exceptions import HealthCheckError
from logiclayer.logging import logger
from logiclayer.module import LogicLayerModule


CheckCallable = Callable[..., Union[bool, Coroutine[Any, Any, bool]]]


class LogicLayer:
    """LogicLayer class"""

    app: ASGIApp
    checks: List[CheckCallable]
    is_ready: bool
    modules: Dict[str, "LogicLayerModule"]
    routes: Dict[str, Callable[..., Coroutine[Any, Any, Response]]]

    def __init__(self):
        self.checks = []
        self.is_ready = False
        self.modules = {}
        self.routes = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """This method converts the :class:`LogicLayer` instance into an ASGI
        compatible callable.

        It also does the asynchonous setup of the modules on the first request.
        """
        if not hasattr(self, "app"):
            self.app = await self.setup()
        await self.app(scope, receive, send)

    @property
    def route_list(self):
        """Returns a set with the routes registered in this LogicLayer instance."""
        return set().union(self.modules.keys(), self.routes.keys())

    def add_check(self, func: CheckCallable):
        """Stores a function to be constantly run as a healthcheck for the app.

        Arguments:
            func :Callable[..., Coroutine[Any, Any, Response]]:
        """
        logger.debug(f"Check added: {func.__name__}")
        self.checks.append(func)

    def add_module(self, module: "LogicLayerModule", prefix: str):
        """Stores a module instance in the current LogicLayer setup.

        Modifications can be done to module instance properties at any point
        before the call of the main setup() method.

        Arguments:
            module :LogicLayerModule:
            prefix :str:
        """
        logger.debug(f"Module added on path {prefix}: {type(module).__name__}")
        self.modules[prefix] = module

    def add_route(self, path: str, func: Callable[..., Coroutine[Any, Any, Response]]):
        """Stores a function to be used in the execution of a specific path.

        The function to be executed at a specific path can be changed at any
        point before the call of the main setup() method.

        Arguments:
            path :str: -
        """
        logger.debug(f"Route added on path {path}: {func.__name__}")
        self.routes[path] = func

    async def setup(self, healthcheck=True) -> ASGIApp:
        """Initializes a FastAPI app using the current LogicLayer setup."""
        logger.debug(
            f"Setting up LogicLayer instance: {len(self.checks)} healthchecks, "
            f"{len(self.modules)} modules, and {len(self.routes)} individual routes"
        )
        app = FastAPI()

        if healthcheck and len(self.checks) > 0:
            run_checks = setup_healthcheck(self.checks)
            app.add_api_route("/_health", run_checks, name="healthcheck")

        await asyncio.gather(
            *(setup_module(app, path, module) for path, module in self.modules.items())
        )

        for path, func in self.routes.items():
            app.add_api_route(path, endpoint=func)

        return app


async def setup_module(app: FastAPI, path: str, module: LogicLayerModule):
    router = APIRouter()

    result = module.setup(router)
    if isawaitable(result):
        await result

    app.include_router(router, prefix=path)


def setup_healthcheck(checks: List[CheckCallable]):
    async def run_checks():
        try:
            await asyncio.gather(*(hc_coro_wrapper(check) for check in checks))
        except Exception as exc:
            logger.error(exc)

        return Response("", status_code=204)

    return run_checks


async def hc_coro_wrapper(check: CheckCallable) -> None:
    """Wraps a function, which might be synchronous or asynchronous, into an
    asynchronous function, which returns the value wrapped in a coroutine.
    """
    result = check()
    if isawaitable(result):
        result = await result

    if result is not True:
        raise HealthCheckError()

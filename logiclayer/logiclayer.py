"""LogicLayer class module.

Contains the main definitions for the LogicLayer class.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, List, Union

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse, Response
from starlette.status import HTTP_204_NO_CONTENT
from starlette.types import Receive, Scope, Send

from .module import CallableMayReturnCoroutine, LogicLayerModule, _await_for_it

logger = logging.getLogger("logiclayer")


class LogicLayer:
    """Main LogicLayer app handler

    Instances of this class act like ASGI callables."""

    app: FastAPI
    debug: bool
    healthchecks: List[CallableMayReturnCoroutine[bool]]

    def __init__(self, *, debug: bool = False, healthchecks: bool = True):
        self.app = FastAPI()
        self.debug = debug
        self.healthchecks = []

        if healthchecks:
            self.app.add_api_route(
                "/_health",
                endpoint=self.call_healthchecks,
                name="LogicLayer healthcheck",
            )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """This method converts the :class:`LogicLayer` instance into an
        ASGI-compatible callable.
        """
        await self.app(scope, receive, send)

    def add_check(self, func: CallableMayReturnCoroutine[bool]):
        """Stores a function to be constantly run as a healthcheck for the app.

        Arguments:
            func :Callable[..., Coroutine[Any, Any, Response]]:
        """
        logger.debug("Check added: %s", func.__name__)
        self.healthchecks.append(func)

    def add_module(self, prefix: str, module: LogicLayerModule, **kwargs):
        """Setups a module instance in the current LogicLayer instance.

        Arguments:
            prefix :str:
                The prefix path to all routes in the module.
                Must start, and not end, with `/`.
            module :logiclayer.LogicLayerModule:
                An instance of a subclass of :class:`logiclayer.LogicLayerModule`.

        Keyword arguments:
            {any from :func:`FastAPI.include_router` function}
        """

        logger.debug("Module added on path %s: %s", prefix, type(module).__name__)

        module.debug = self.debug
        self.app.include_router(module.router, prefix=prefix, **kwargs)
        self.add_check(module._llhealthcheck)

        for exc_cls, exc_handler in module.exception_handlers:
            self.app.add_exception_handler(exc_cls, exc_handler)

    def add_redirect(self, path: str, url: str, *, code: int = 307, headers=None):
        """"""
        func = lambda: RedirectResponse(url=url, status_code=code, headers=headers)
        self.add_route(path, func)

    def add_route(self, path: str, func: CallableMayReturnCoroutine[Any], **kwargs):
        """Setups a path function to be used directly in the root app.

        Arguments:
            path :str:
                The full path to the route this function will serve.
            func :Callable[..., Response] | Callable[..., Coroutine[Any, Any, Response]]:
                The function which will serve the content for the route.
        """
        logger.debug("Route added on path %s: %s", path, func.__name__)
        self.app.add_api_route(path, func, **kwargs)

    def add_static(self, path: str, target: Union[str, Path], *, html: bool = False):
        """Setups a static folder to serve the files inside it.

        Arguments:
            path :str:
                The full path to the route where the folder will be available.
            target :str: | :pathlib.Path:
                The path to the directory containing the static files to serve.
        Keyword Arguments:
            html :bool:
                HTML mode. Looks for an index.html file when the requested path
                is a directory, and serves it automatically.
        """
        target = (Path(target) if isinstance(target, str) else target).resolve()
        logger.debug("Static folder added on path %s")
        self.app.mount(path, StaticFiles(directory=target, html=html))

    async def call_startup(self):
        """Forces a call to all handlers registered for the 'startup' event."""
        await self.app.router.startup()

    async def call_shutdown(self):
        """Forces a call to all handlers registered for the 'shutdown' event."""
        await self.app.router.shutdown()

    async def call_healthchecks(self):
        try:
            gen = (_await_for_it(item) for item in self.healthchecks)
            await asyncio.gather(*gen)
        except Exception as exc:
            logger.error("Healthcheck failure", exc_info=exc)
        else:
            return Response(status_code=HTTP_204_NO_CONTENT)

        raise HTTPException(500, "One of the healthchecks failed.")

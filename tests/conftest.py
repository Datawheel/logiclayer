"""Test fixtures module.

This module provides the test suite with some parameters to work easily.
The return value is passed to the test function that requires it based on the
fixture name. Check the documentation for pytest on fixtures for more details.

* pytest fixtures: <https://docs.pytest.org/en/6.2.x/fixture.html>
"""

from dataclasses import dataclass
from random import randint

import httpx
import pytest
from fastapi.requests import Request
from fastapi.responses import JSONResponse, PlainTextResponse

import logiclayer as ll


@dataclass
class BodySchema:
    value: str


class EchoModule(ll.LogicLayerModule):
    def __init__(self, label: str, **kwargs):
        super().__init__(**kwargs)
        self.random = randint(0, 9)
        self.label = label

    @ll.healthcheck
    async def healthcheck(self):
        print("HEALTHCHECK")
        return True

    @ll.on_startup
    async def event_startup(self):
        print("STARTUP", self.label)

    @ll.on_shutdown
    def event_shutdown(self):
        print("SHUTDOWN", self.label)

    @ll.route("GET", "/", name="Index route for base")
    async def route_index(self):
        return {"label": self.label}

    @ll.route("GET", "/file.{ext}")
    def route_file(self, ext: str):
        return PlainTextResponse(f"Label: {self.label}\nExtension: {ext}")

    @ll.route("GET", "/error")
    def route_error(self):
        raise ValueError(self.label)

    @ll.route("GET", "/random")
    async def route_random(self):
        return {"random": self.random}

    @ll.route("GET", "/empty")
    def route_empty(self):
        return {}

    @ll.route("GET", "/number")
    async def route_query(self, value: int):
        return {"number": value}

    @ll.route("GET", "/string-{asdf}")
    def route_path(self, asdf: str):
        return {"string": asdf}

    @ll.route("GET", "/body")
    async def route_body(self, body: BodySchema):
        return body.value

    @ll.route("GET", "/debug", debug=True)
    def route_debug(self):
        return {"debug": True}

    @ll.exception_handler(ValueError)
    def exc_valueerror(self, request: "Request", exc: "ValueError"):
        return JSONResponse(
            {
                "label": self.label,
                "route": "exc_valueerror",
                "request": str(request.url),
                "exc": str(exc),
            },
            status_code=504,
        )


@pytest.fixture
def layer():
    echo = EchoModule("Hello")
    echo_debug = EchoModule("World", debug=True)

    layer = ll.LogicLayer()
    layer.add_module("/echo2", echo_debug)
    layer.add_module("/echo", echo)

    @layer.healthcheck
    async def route_check():
        async with httpx.AsyncClient() as client:
            res = await client.get("http://clients3.google.com/generate_204")
        return (res.status_code == 204) and (res.headers.get("Content-Length") == 0)

    @layer.route("/", response_model=ll.ModuleStatus)
    def route_status():
        return {
            "status": "ok",
            "module": "LogicLayer",
            "version": ll.__version__,
            "debug": True,
            "mode": "testing",
        }

    return layer

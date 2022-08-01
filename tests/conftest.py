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

import logiclayer as ll


@dataclass
class BodySchema:
    value: str


def route_check():
    res = httpx.get("http://clients3.google.com/generate_204")
    return (res.status_code == 204) and (res.headers.get("Content-Length") == 0)

def route_status():
    return {"status": "ok", "software": "LogicLayer", "version": ll.__version__}


class EchoModule(ll.LogicLayerModule):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.random = randint(0, 9)

    @ll.route("GET", "/random")
    async def route_random(self):
        return {"random": self.random}

    @ll.route("GET", "/empty")
    def route_empty():
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


@pytest.fixture
def layer():
    echo = EchoModule()

    layer = ll.LogicLayer()
    layer.add_check(route_check)
    layer.add_route("/", route_status)
    layer.add_module("/echo", echo)

    return layer

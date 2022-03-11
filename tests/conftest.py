"""Test fixtures module.

This module provides the test suite with some parameters to work easily.
The return value is passed to the test function that requires it based on the
fixture name. Check the documentation for pytest on fixtures for more details.

* pytest fixtures: <https://docs.pytest.org/en/6.2.x/fixture.html>
"""

import httpx
import pytest
from fastapi.testclient import TestClient

from logiclayer import LogicLayer
from logiclayer.echo import EchoModule


def create_test_app():
    echo = EchoModule()

    def online_check() -> bool:
        res = httpx.get("http://clients3.google.com/generate_204")
        return (res.status_code == 204) and (res.headers.get("Content-Length") == "0")

    layer = LogicLayer()
    layer.add_check(online_check)
    layer.add_module(echo, prefix="/echo")

    return layer


@pytest.fixture(autouse=True)
def test_client():
    app = create_test_app()
    client = TestClient(app)
    return client

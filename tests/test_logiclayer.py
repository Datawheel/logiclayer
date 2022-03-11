"""
"""

import uuid
from fastapi.testclient import TestClient


def test_module_echo(test_client: TestClient):
    """Tests a simple demo app setup."""

    nonce = uuid.uuid4()
    response = test_client.get("/echo", params={"msg": str(nonce)})
    assert response.status_code == 200

    root = response.json()
    assert root["status"] == "ok"
    assert root["data"] == "eyJlbmNvZGluZyI6ImJhc2U2NCJ9"
    assert root["echo"] == str(nonce)


def test_checks(test_client: TestClient):
    """Tests the proper execution of healthchecks."""

    response = test_client.get("/_health")
    assert response.status_code == 204
    assert response.text == ""

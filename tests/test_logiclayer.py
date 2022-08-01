from fastapi.testclient import TestClient

import logiclayer as ll


def test_route_check(layer: ll.LogicLayer):
    with TestClient(app=layer) as client:
        res = client.get("/_health")

    assert res.status_code == 204
    assert res.text == ""

def test_route_status(layer: ll.LogicLayer):
    with TestClient(app=layer) as client:
        res = client.get("/")

    assert res.status_code == 200
    assert res.json() == {
        "status": "ok",
        "software": "LogicLayer",
        "version": ll.__version__,
    }

def test_route_random(layer: ll.LogicLayer):
    with TestClient(app=layer) as client:
        res1 = client.get("/echo/random")
        res2 = client.get("/echo/random")

    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res1.json() == res2.json()

def test_route_empty(layer: ll.LogicLayer):
    with TestClient(app=layer) as client:
        res = client.get("/echo/empty")

    assert res.status_code == 200
    assert res.json() == {}

def test_route_query(layer: ll.LogicLayer):
    with TestClient(app=layer) as client:
        res = client.get("/echo/number?value=10")

    assert res.status_code == 200
    assert res.json() == {"number": 10}

def test_route_path(layer: ll.LogicLayer):
    with TestClient(app=layer) as client:
        res = client.get("/echo/string-beta")

    assert res.status_code == 200
    assert res.json() == {"string": "beta"}

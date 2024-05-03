from fastapi.testclient import TestClient

import logiclayer as ll


def test_route_status(layer: ll.LogicLayer):
    with TestClient(app=layer) as client:
        res = client.get("/")

    assert res.status_code == 200
    assert res.json() == {
        "status": "ok",
        "module": "LogicLayer",
        "version": ll.__version__,
        "debug": True,
        "mode": "testing",
    }


def test_route_check(layer: ll.LogicLayer):
    with TestClient(app=layer) as client:
        res = client.get("/_health")

    assert res.status_code == 204
    assert res.text == ""


def test_route_index(layer: ll.LogicLayer):
    with TestClient(app=layer) as client:
        res = client.get("/echo/")

    assert res.status_code == 200
    assert res.json() == {"label": "Hello"}


def test_route_file(layer: ll.LogicLayer):
    with TestClient(app=layer) as client:
        res = client.get("/echo/file.asdf")

    assert res.status_code == 200
    assert res.text == "Label: Hello\nExtension: asdf"


def test_route_error(layer: ll.LogicLayer):
    with TestClient(app=layer, base_url="http://demoserver/") as client:
        res = client.get("/echo/error")

    assert res.status_code == 504
    assert res.json() == {
        "label": "Hello",
        "route": "exc_valueerror",
        "request": "http://demoserver/echo/error",
        "exc": "Hello",
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

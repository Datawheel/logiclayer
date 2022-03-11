from fastapi.params import Query

from .module import LogicLayerModule


class EchoModule(LogicLayerModule):
    """Echo Module for LogicLayer

    This is just a test module, to check basic functionality.
    """

    data = "eyJlbmNvZGluZyI6ImJhc2U2NCJ9"

    def setup(self, router):

        @router.get("/")
        def route_index(message: str = Query(..., alias="msg")):
            return {
                "status": "ok",
                "data": self.data,
                "echo": message
            }

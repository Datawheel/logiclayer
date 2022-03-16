from logiclayer import LogicLayer


class GeoserviceModule(LogicLayer):
    """Geoservice LogicLayer module class.

    This module contains the functions associated to the geoservice function.
    It requires the connection parameters to a configured Postgres server.
    """

    schema: str
    server: str

    def __init__(self, schema: str, server: str, **kwargs):
        super().__init__(**kwargs)
        self.schema = schema
        self.server = server

    def setup(self, router: APIRouter):
        server = self.server

        router.get("/neighbors/:geoId")
        def neighbors(self):
            pass

        router.get("/:op(within|intersects)")
        def intersects():
            pass

        router.get("/topojson/:level/:focusId")
        def topojson():
            pass

        router.get("/related/:geoId")
        def related(geoId):
            pass

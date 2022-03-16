"""Economic Complexity adapter for use in LogicLayer.

Contains a module to enable endpoints which return economic complexity
calculations, using a Tesseract OLAP server as data source.
"""

import os
import sys
from typing import Optional

import econplexity
from fastapi import APIRouter
from olap_client import Query, TesseractServer, Server

from logiclayer import LogicLayerModule


class EconomicComplexityModule(LogicLayerModule):
    """Economic Complexity calculations module class for LogicLayer.
    """

    server: "Server"

    def __init__(self,
                 server_url: Optional[str] = None,
                 server: Optional["Server"] = None):
        """Setups the server for this instance.
        """

        if server is not None:
            self.server = server
        elif server_url is not None:
            self.server = TesseractServer(server_url)
        else:
            raise ValueError("EconomicComplexityModule needs an olap_server Server or a server url")

    def setup(self):
        """Applies the configuration in the current instance to an `app`.
        """

        server = self.server

        async def hydrate_cube(
            cube_name: str = Query(...,
                alias="cube",
                title="Cube name",
                description="The name of the cube where the RCA parameters are available.",
            )
        ):
            """Transform a cube name from the query parameters into a OlapClient Cube.
            """

            cube = await server.fetch_cube(cube_name)
            return cube

        return (hydrate_cube, )

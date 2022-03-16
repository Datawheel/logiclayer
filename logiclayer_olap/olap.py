from io import StringIO
from typing import Optional, Union

from fastapi import APIRouter, Depends, Path, Query
from olap_client import __version__ as olapclient_version
from olap_client.tesseract import (TesseractCube, TesseractDataFormat,
                                   TesseractServer)
from starlette.responses import StreamingResponse

from logiclayer import LogicLayerModule

from .exceptions import InvalidFormatHTTPError, InvalidParameterHTTPError
from .hydrate import hydrate_query
from .remote import (fetch_all_cubes, fetch_all_members, fetch_query,
                     fetch_single_cube)


class OlapModule(LogicLayerModule):
    """Demo module for Tesseract OLAP on LogicLayer.

    For now it is just a proof of concept.
    """

    server: TesseractServer

    def __init__(self, server: Union[str, TesseractServer]):
        if isinstance(server, str):
            server = TesseractServer(server)

        self.server = server

    def setup(self, router: APIRouter):
        server = self.server

        async def on_cube(
            cube_name: str = Query(..., alias="cube"),
            locale: str = Query(...)
        ):
            cube = await fetch_single_cube(server, cube_name, locale)
            return cube

        def on_extension(extension: str = Path("csv")):
            if extension in ("jsonrecords", "jsonarrays", "csv"):
                return extension
            raise InvalidFormatHTTPError(extension)

        def on_level(
            cube: TesseractCube = Depends(on_cube),
            level_name: str = Query(..., alias="level")
        ):
            try:
                level = cube.get_level(level_name)
            except StopIteration:
                raise InvalidParameterHTTPError("level")
            finally:
                return level

        @router.get("/")
        def route_status():
            return {
                "status": "ok",
                "software": "Tesseract OLAP Proxy",
                "version": olapclient_version,
            }

        @router.get("/cubes")
        async def route_cubes(
            locale: Optional[str] = Query(None),
        ):
            cubes = await fetch_all_cubes(server, locale)
            return cubes

        @router.get("/cubes/{cube_name}")
        async def route_cube(
            cube_name: str = Path(..., ),
            locale: Optional[str] = Query(None),
        ):
            cube = await fetch_single_cube(server, cube_name, locale)
            return cube

        @router.get("/members.{extension}")
        async def route_members(
            cube_name: str = Query(..., alias="cube"),
            level_name: str = Query(..., alias="level"),
            extension: str = Depends(on_extension),
            locale: Optional[str] = Query(None),
        ):
            members = await fetch_all_members(server, cube_name, level_name, locale)
            if extension == "csv":
                return members.to_csv()
            if extension in ("jsonarrays", "jsonrecords"):
                return members.to_json()

        @router.get("/query.{extension}")
        async def route_query(
            drilldown: str,
            measure: str,
            cube: TesseractCube = Depends(on_cube),
            extension: str = Depends(on_extension),
            locale: Optional[str] = Query(None),
        ):
            query = hydrate_query(
                cube,
                drilldowns=drilldown.split(","),
                measures=measure.split(","),
                cuts=[],
                extension=TesseractDataFormat.DATAFRAME,
                locale=locale,
            )
            df = await fetch_query(server, query)
            buf = StringIO()
            df.to_csv(buf)

            def iterfile():
                with open(buf, "rb") as thefile:
                    yield from thefile

            return StreamingResponse(iterfile(), media_type="text/csv")

"""Remote request module.

This module contains functions to fetch data from a Tesseract server.
That is their main purpose, though also can do modifications to the data they
output too. They also intercept foreign and raise internal exceptions, to avoid
data leaks about the origin server.
"""

import functools
from typing import Optional

import pandas as pd
from httpx import HTTPStatusError
from olap_client import InvalidFormatError
from olap_client.tesseract import (TesseractDataFormat, TesseractQuery,
                                   TesseractServer)

from .exceptions import InvalidFormatHTTPError, UpstreamUnavailableHTTPError


async def fetch_all_cubes(
    server: TesseractServer,
    locale: str,
):
    """Returns a list of TesseractCube."""
    cubes = await server.fetch_all_cubes()
    return cubes


async def fetch_single_cube(
    server: TesseractServer,
    cube_name: str,
    locale: str,
):
    """Returns a single TesseractCube, determined by its name."""
    cube = await server.fetch_cube(cube_name, locale=locale)
    return cube


async def fetch_all_members(
    server: TesseractServer,
    cube_name: str,
    level_name: str,
    locale: Optional[str] = None,
) -> pd.DataFrame:
    """Returns all the members belonging to a level."""

    try:
        members = await server.fetch_members(
            cube_name=cube_name,
            level_name=level_name,
            locale=locale,
            extension=TesseractDataFormat.DATAFRAME,
        )
    except HTTPStatusError as exc:
        # TODO: Log the request as unavailable for later analysis
        raise UpstreamUnavailableHTTPError() from exc
    else:
        return members


async def fetch_query(
    server: TesseractServer,
    query: TesseractQuery,
) -> pd.DataFrame:
    """Returns the resulting data for a specified query."""
    return server.exec_query(query)

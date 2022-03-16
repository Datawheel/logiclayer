import os
from enum import Enum
from typing import Optional

from fastapi import Query
from olap_client.tesseract import TesseractServer

from .exceptions import MalformedParameterException


class MethodArgument(str, Enum):
    SUBNATIONAL = "subnational"
    RELATEDNESS = "relatedness"

def parse_rca_tuple(
    rca: str = Query(...,
        title="RCA parameters",
        description="A tuple of \"Level,Level,Measure\" from the datasource. The first level is usually a location level, the second is a category level, and the measure represents the values used for the calculation. For Levels you can use unique names or full names.",
    )
):
    """Separates the RCA calculation components."""
    params = rca.split(",")
    if len(params) != 3:
        raise MalformedParameterException("rca")


def parse_common_args(
    # alias: str,
    eci_threshold: Optional[str],
    method: Optional[MethodArgument] = None,
    iterations: Optional[int] = 20,
    # options
    # ranking
    # threshold
    # filter_*
    **kwargs
):
    return {
        "eci_threshold": eci_threshold,
        "method": method,
        "iterations": iterations,
    }

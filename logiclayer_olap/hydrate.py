from typing import List
from olap_client.tesseract import TesseractCube


def hydrate_query(
    cube: TesseractCube,
    measures: List[str],
    drilldowns: List[str],
    cuts: List[str],
):
    query = cube.new_query()

    return query

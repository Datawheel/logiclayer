"""Endpoint: RCA
"""

from typing import Tuple

from fastapi import Query, Depends

from .dependencies import parse_common_args, parse_rca_tuple


def get_rca(
    cube,
    rca: Tuple[str, str, str] = Depends(parse_rca_tuple),
    common: dict = Depends(parse_common_args)
):

    df = self.load_step()
    df = self.transform_step(df, [self.dd1, self.dd2], self.rca_measure)
    self.base.to_output(df)

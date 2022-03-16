"""OLAP Module for LogicLayer.

Replicates the functionality of a Tesseract OLAP server as a set of routes for
a LogicLayer application.
"""

from .olap import OlapModule

__all__ = (
    "OlapModule",
)

__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)

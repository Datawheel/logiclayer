import logging.config
import os

import httpx

from logiclayer import LogicLayer
from logiclayer import __version__ as logiclayer_version
from logiclayer_geoservice import GeoserviceModule
from logiclayer_olap import OlapModule

# https://www.datadoghq.com/blog/python-logging-best-practices/
config_filepath = os.environ.get("LOGICLAYER_LOGGING_CONFIG", "logging.ini")
logging.config.fileConfig(config_filepath, disable_existing_loggers=False)


# DEFINE A CHECK
def online_check():
    res = httpx.get("http://clients3.google.com/generate_204")
    return (res.status_code == 204) and (res.headers.get("Content-Length") == 0)


# DEFINE A SIMPLE ROUTE
def status_route():
    return {"status": "ok", "software": "LogicLayer", "version": logiclayer_version}


# DEFINE A MODULE INSTANCE
geoservice = GeoserviceModule(schema="./geoservice.xml",
                              server="postgresql://user:pass@localhost:5432/mexico_geo")

olap = OlapModule("https://api.oec.world/tesseract/")


def run():
    # CREATE A LOGICLAYER INSTANCE
    layer = LogicLayer()

    # ADD PLUGINS
    layer.add_check(online_check)
    layer.add_route("/", status_route)
    layer.add_module(olap, prefix="/tesseract")

    return layer

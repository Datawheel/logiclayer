import logging
import logging.config
import os

# https://www.datadoghq.com/blog/python-logging-best-practices/
config_filepath = os.environ.get("LOGICLAYER_LOGGING_CONFIG", "logging.ini")
logging.config.fileConfig(config_filepath, disable_existing_loggers=False)

logger = logging.getLogger("logiclayer")

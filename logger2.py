from logging_config import set_up_logger
import logging

logger = logging.getLogger(__name__)
set_up_logger(logger)

logger.info("An info")
logger.warning("A warning")
from logging_config import get_logger

logger = get_logger(__name__)

logger.debug("An debug")
logger.info("An info")
logger.warning("A warning")
logger.error("A error")
logger.critical("A critical error")
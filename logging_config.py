# source: https://betterstack.com/community/guides/logging/python/python-logging-best-practices/
# https://docs.python.org/3/howto/logging.html
# https://stackoverflow.com/questions/7507825/where-is-a-complete-example-of-logging-config-dictconfig
# https://stackoverflow.com/questions/1343227/can-pythons-logging-format-be-modified-depending-on-the-message-log-level/56944275#56944275

import logging
#from pythonjsonlogger import jsonlogger

from datetime import datetime
import uuid
import os


class Colors:
  grey = "\x1b[0;37m"
  green = "\x1b[1;32m"
  yellow = "\x1b[1;33m"
  red = "\x1b[1;31m"
  purple = "\x1b[1;35m"
  blue = "\x1b[1;34m"
  light_blue = "\x1b[1;36m"
  reset = "\x1b[0m"
  blink_red = "\x1b[5m\x1b[1;31m"

class CustomFormatter(logging.Formatter):
  """Logging Formatter to add colors and count warning / errors"""

  bold_red = "\x1b[31;1m"

  format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

  FORMATS = {
    logging.DEBUG: Colors.grey + format + Colors.reset,
    logging.INFO: Colors.light_blue + '%(message)s' + Colors.reset,
    logging.WARNING: Colors.yellow + format + Colors.reset,
    logging.ERROR: Colors.red + format + Colors.reset,
    logging.CRITICAL: bold_red + format + Colors.reset
  }

  def format(self, record):
    log_fmt = self.FORMATS.get(record.levelno)
    formatter = logging.Formatter(log_fmt)
    return formatter.format(record)


def get_logger(log_name, add_date=True, add_uuid=True, log_dir='logs'):
  logger = logging.getLogger(log_name)
  logger.propagate = False
  logger.setLevel(logging.DEBUG) # the least offensive level that will be taken into account

  filename_ending = ''
  if add_date:
    filename_ending += datetime.now().strftime("_%Y_%m_%d_%H_%M_%S")
  if add_uuid:
    filename_ending += f'_{uuid.uuid4()}.log'

  # create console handler with a higher log level
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)
  ch.setFormatter(CustomFormatter())
  logger.addHandler(ch)

  # create console handler with a higher log level
  for fname, level in (('log', logging.INFO), ('error', logging.WARNING)):
    filename = log_name + '_' + fname + filename_ending
    if log_dir:
      filename = os.path.join(log_dir, filename)
    ch = logging.FileHandler(filename=filename, mode='a')
    ch.setLevel(level)
    logger.addHandler(ch)

  return logger

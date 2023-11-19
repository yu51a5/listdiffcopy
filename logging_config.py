# source: https://betterstack.com/community/guides/logging/python/python-logging-best-practices/
# https://docs.python.org/3/howto/logging.html
# https://stackoverflow.com/questions/7507825/where-is-a-complete-example-of-logging-config-dictconfig
# https://stackoverflow.com/questions/1343227/can-pythons-logging-format-be-modified-depending-on-the-message-log-level/56944275#56944275
# https://stackoverflow.com/questions/67241111/python-colored-text-to-the-terminal
# https://tforgione.fr/posts/ansi-escape-codes/

from datetime import datetime
import uuid
import os
import logging

class ConsoleFormatter(logging.Formatter):
  """Logging Formatter to add colors and count warning / errors"""

  bold_red =    "\x1B[38;2;255;0;0;7m"
  bold_orange = "\x1B[38;2;255;135;0;7m"
  bold_yellow = "\x1B[38;2;255;255;0;7m"
  grey = "\x1b[0;37m"
  yellow = "\x1b[1;33m"
  # blink_red = "\x1b[5m\x1b[1;31m"
  reset = "\x1b[0m"

  format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

  FORMATS = {
    logging.DEBUG: yellow + format + reset,
    logging.INFO: grey + '%(message)s' + reset,
    logging.WARNING: bold_yellow + format + reset,
    logging.ERROR: bold_orange + format + reset,
    logging.CRITICAL: bold_red + format + reset
  }

  def format(self, record):
    log_fmt = self.FORMATS[record.levelno]
    formatter = logging.Formatter(log_fmt)
    print(dir(record))
    return formatter.format(record)


def get_logger(log_name, add_date=True, add_uuid=True, log_dir='logs'):
  logger = logging.getLogger(log_name)
  logger.propagate = False
  logger.setLevel(logging.DEBUG) # the least offensive level that will be taken into account
  
  filename_date = datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") if add_date else ''
  filename_uuid = f'_{uuid.uuid4()}' if add_uuid else ''

  # create console handler with a higher log level
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)
  ch.setFormatter(ConsoleFormatter())
  logger.addHandler(ch)

  # create console handler with a higher log level
  for fname, level in (('log', logging.INFO), ('error', logging.WARNING)):
    filename = log_name + filename_date + '_' + fname + filename_uuid + '.log'
    if log_dir:
      filename = os.path.join(log_dir, filename)
    ch = logging.FileHandler(filename=filename, mode='a')
    ch.setLevel(level)
    logger.addHandler(ch)

  return logger

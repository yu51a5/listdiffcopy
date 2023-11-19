# source: https://betterstack.com/community/guides/logging/python/python-logging-best-practices/
# https://docs.python.org/3/howto/logging.html
# https://stackoverflow.com/questions/7507825/where-is-a-complete-example-of-logging-config-dictconfig

import logging.config
#from pythonjsonlogger import jsonlogger

from datetime import datetime
import uuid

now_uuid_log = datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + f'_{uuid.uuid4()}.log'

class CustomFormatter(logging.Formatter):
  """Logging Formatter to add colors and count warning / errors"""

  grey = "\x1b[38;21m"
  yellow = "\x1b[33;21m"
  red = "\x1b[31;21m"
  bold_red = "\x1b[31;1m"
  reset = "\x1b[0m"
  format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

  FORMATS = {
      logging.DEBUG: grey + format + reset,
      logging.INFO: grey + format + reset,
      logging.WARNING: yellow + format + reset,
      logging.ERROR: red + format + reset,
      logging.CRITICAL: bold_red + format + reset
  }

  def format(self, record):
      log_fmt = self.FORMATS.get(record.levelno)
      formatter = logging.Formatter(log_fmt)
      return formatter.format(record)


def set_up_logger(logger):
  logger.propagate = False
  logger.setLevel(logging.DEBUG)
  
  # create console handler with a higher log level
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)
  ch.setFormatter(CustomFormatter()) 
  logger.addHandler(ch)

  # create console handler with a higher log level
  ch = logging.FileHandler(filename='logs/error'+now_uuid_log, mode='a')
  ch.setLevel(logging.WARNING) 
  logger.addHandler(ch)

  # create console handler with a higher log level
  ch = logging.FileHandler(filename='logs/log'+now_uuid_log, mode='a')
  ch.setLevel(logging.DEBUG) 
  logger.addHandler(ch)



#cf = CustomFormatter()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
      #'console' : { 'class': "ColoredFormatter"}
    },
    "handlers": {
        "stdout": {
            'level': 'DEBUG',
            "class": "logging.StreamHandler",
            #"stream": "ext://sys.stdout",
            "formatter": '',
        },
      'error_file_handler': {
          'level': 'ERROR',
          'formatter': '',
          'class': 'logging.FileHandler',
          'filename': 'logs/error'+now_uuid_log,
          'mode': 'a',
      },
      'file_handler': {
          'level': 'DEBUG',
          'formatter': '',
          'class': 'logging.FileHandler',
          'filename': 'logs/log'+now_uuid_log,
          'mode': 'a',
      },
    },
    "loggers": {"": {"handlers": ["stdout", 'error_file_handler', 'file_handler']}},
}
#
#logging.root.handlers = []
#logging.config.dictConfig(LOGGING)

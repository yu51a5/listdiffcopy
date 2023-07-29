import os
from datetime import datetime

from dry_run import is_dry_run
from settings import only_print_basename, log_file

log_object = None
level_start_times_dirnames = []

def reset_level():
  global level_start_times_dirnames
  level_start_times = []

def log_entering_directory(dirname, message_to_print=''):
  global level_start_times_dirnames
  now_ = datetime.now()
  level_start_times_dirnames.append((now_, dirname))
  log_print(message_to_print + ' dir ', dirname, ' at', now_)

def log_exiting_directory():
  global level_start_times_dirnames
  now_ = datetime.now()
  time_elapsed = now_ - level_start_times_dirnames[-1][0]
  log_print('exited dir ', level_start_times_dirnames[-1][1], ' at', now_, 'time elapsed:', time_elapsed)
  level_start_times_dirnames.pop(-1)

def create_logging_object():
  global log_object
  log_object = open(log_file, "w")
  return log_object

def log_print(message0, name, *args):
  global level_start_times_dirnames
  level = len(level_start_times_dirnames)

  prefix = '╟──── '
  if 'dir' in message0:
    prefix = prefix.replace('─', '═')
    prefix = ('╚' if 'exit' in message0.lower() else ('╠' if 'DELETED' in message0 else '╔')) + prefix[1:]
  # boxy symbols https://www.ncbi.nlm.nih.gov/staff/beck/charents/unicode/2500-257F.html
  prefix = '║' * (level - 1) + prefix
  if is_dry_run():
    prefix += 'would have '
  string_ = prefix + message0 + '`' + (os.path.basename(name) if (only_print_basename and (level != 1)) else name) + '`' + ' '.join([str(a) for a in args])
  log_object.write(string_+'`\n')
  print(string_)
  
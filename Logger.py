import os
from datetime import datetime
import pandas as pd

from settings import only_print_basename, log_file

#################################################################################

def add_sizes(size_so_far, addition):
  if (size_so_far is None) or (addition is None):
    return size_so_far
  return size_so_far + addition

#################################################################################

singleton_logger = None

#################################################################################
class Logger():

  ###############################################################################
  def __init__(self, title, storages_dirs_that_must_exist, log_filename=log_file):
    self.log_object = open(log_filename, "w")
    self.level_start_times_dirnames = []
   

    global singleton_logger
    if singleton_logger is not None:
      raise Exception("logger already exists")
    singleton_logger = self

    self.log_print_basic(title)

    self.__dirs_dont_exist = False

    for storage, dir_to_check in storages_dirs_that_must_exist:
      if not storage.check_directory_exists(dir_to_check):
        self.log_print_basic(f"Skipping because {storage.str(dir_to_check)} does not exist")
        self.__dirs_dont_exist = True
    
  ###############################################################################
  def __enter__(self):
    return self

  ###############################################################################
  def __exit__(self, type, value, traceback):
    self.log_object.close()
    
    global singleton_logger 
    singleton_logger = None

  ###############################################################################
  def dir_exists(self):
    return not self.__dirs_dont_exist

  ###############################################################################
  def log_enter_level(self, dirname, message_to_print, message2):
    now_ = datetime.now()
    self.level_start_times_dirnames.append((now_, dirname))
    self.log_print(message_to_print + ' dir ', dirname, message2, 'at', now_)

  ###############################################################################
  def log_exit_level(self, dir_details):
    now_ = datetime.now()
    time_elapsed = now_ - self.level_start_times_dirnames[-1][0]
    dir_details_df = pd.DataFrame(dir_details,
                                  index=["Total", "First level"], 
                                  columns=["Size", "Files qty", "Dirs qty"])
    self.log_print('exited dir ', self.level_start_times_dirnames[-1][1], 'at', now_, 'time elapsed:', time_elapsed, dir_details_df)
    self.level_start_times_dirnames.pop(-1)

  ###############################################################################
  def log_print_basic(self, message):
    self.log_object.write(message + '\n')
    print(message)

  ###############################################################################
  def log_print(self, message0, name, *args):

    level = len(self.level_start_times_dirnames)
  
    prefix = '╟──── '
    if 'dir' in message0:
      prefix = prefix.replace('─', '═')
      prefix = ('╚' if 'exit' in message0.lower() else ('╠' if 'DELETED' in message0 else '╔')) + prefix[1:]
    if message0 == 'exited dir ':
      prefix = prefix[:-2] + '╦ ' 
      dir_details_df = args[-1]
      args_to_use = args[:-1]
    else:
      dir_details_df = None
      args_to_use = args
    # boxy symbols https://www.ncbi.nlm.nih.gov/staff/beck/charents/unicode/2500-257F.html

    string_ = '║' * (level - 1) + prefix + message0 + '`' + (os.path.basename(name) if (only_print_basename and (level != 1)) else name) + '` ' + ' '.join([str(a) for a in args_to_use if a])
    
    self.log_print_basic(string_)

    if dir_details_df is not None:
      dir_details_str = dir_details_df.to_string().split('\n')
      prefix_dir_details = '║' * (level - 1) + ' ' * (len(prefix) - 2) + '╠═'
      for i, dir_details_str_ in enumerate(dir_details_str):
        if i == (len(dir_details_str) - 1):
          prefix_dir_details = prefix_dir_details[:-2] + '╚═'
        string_ = prefix_dir_details + dir_details_str_
        self.log_print_basic(string_)
    
###############################################################################
def log_print(message0, name, *args):
  global singleton_logger 
  if singleton_logger is None:
    raise Exception("logger does not exist")
  singleton_logger.log_print(message0, name, *args)
  
###############################################################################
def log_enter_level(*args, **kwargs):
  global singleton_logger 
  if singleton_logger is None:
    raise Exception("logger does not exist")
  singleton_logger.log_enter_level(*args, **kwargs)

###############################################################################
def log_exit_level(*args, **kwargs):
  global singleton_logger 
  if singleton_logger is None:
    raise Exception("logger does not exist")
  singleton_logger.log_exit_level(*args, **kwargs)
        
import os
from datetime import datetime
import math

from settings import log_file

#################################################################################
class Logger():

  ###############################################################################
  def __init__(self, title, storages_dirs_that_must_exist, log_filename=log_file):
    self.log_object = open(log_filename, "w")
    self.level_start_times_dirnames = []

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

  ###############################################################################
  def dir_exists(self):
    return not self.__dirs_dont_exist

  ###############################################################################
  def log_enter_level(self, dirname, message_to_print, message2=''):
    now_ = datetime.now()
    self.level_start_times_dirnames.append((now_, dirname))
    self.log_print(message_to_print + ' directory ', dirname, message2, 'at', now_)

  ###############################################################################
  def log_exit_level(self, dir_details_df):
    now_ = datetime.now()
    time_elapsed = now_ - self.level_start_times_dirnames[-1][0]
    self.log_print('exited directory ', self.level_start_times_dirnames[-1][1], 'at', now_, 'time elapsed:', time_elapsed, dir_details_df)
    self.level_start_times_dirnames.pop(-1)

  ###############################################################################
  def log_print_basic(self, message):
    self.log_object.write(message + '\n')
    print(message)

  ###############################################################################
  def log_print_df(self, df, extra_prefix, last_chars_last_prefix=''):
    if df.index.empty:
      return
    df_str = df.to_string().split('\n')
    level = len(self.level_start_times_dirnames)
    prefix = '║' * (level - 1) + extra_prefix
    for i, df_str_ in enumerate(df_str):
        if i == (len(df_str) - 1) and last_chars_last_prefix:
          prefix = prefix[:-len(last_chars_last_prefix)] + last_chars_last_prefix
        self.log_print_basic(prefix + df_str_)

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

    string_ = '║' * (level - 1) + prefix + message0 + '`' + name + '` ' + ' '.join([str(a) for a in args_to_use if a])
    
    self.log_print_basic(string_)

    if dir_details_df is not None:
      self.log_print_df(df=dir_details_df, extra_prefix=' ' * (len(prefix) - 2) + '╠═ ', last_chars_last_prefix='╚═ ')

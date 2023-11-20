from logging_config import get_logger
from utils import put_together_framed_message
from datetime import datetime

logger = get_logger(__name__)

logger.debug("An debug")
logger.info("An info")
logger.warning("A warning")
logger.error("A error")
logger.critical("A critical error")

#################################################################################
class Logger:

  ###############################################################################
  def _check_storage_or_type(storage, StorageType, kwargs):
    errors = []
    if (storage is None) == (StorageType is None):
      errors.append(f"storage_from {storage} and StorageFromType {StorageType} mustn't be both None or both not None")
    if (StorageType is None) and kwargs:
      errors.append(f"StorageFromType is not provided, but arguments {kwargs} are")
    return errors

  ###############################################################################
  def log_print_framed(self, message, char):
    msg = put_together_framed_message(message=message, char=char)
    self.log_info(msg)

  ###############################################################################
  def __init__(self, name=""):

    

  ###############################################################################
  def get_errors_count(self):
    return self.__error_count

  ###############################################################################
  def log_critical(self, message):
    self.__logger.critical(message)
    self.__error_count += 1
    #assert "stopping here to show the full call stack"
  
  ###############################################################################
  def log_error(self, message):
    self.__logger.error(message)
    self.__error_count += 1
    #assert "stopping here to show the full call stack"

  ###############################################################################
  def log_warning(self, message):
    self.__logger.warning(message)

  ###############################################################################
  def log_info(self, message):
    self.__logger.info(message)
  
  ###############################################################################
  def log_enter_level(self, dirname, message_to_print, message2=''):
    now_ = datetime.now()
    self.__level_start_times_dirnames.append((now_, dirname))
    self.__log_print(message_to_print + ' directory ', dirname, message2, 'at', now_)

  ###############################################################################
  def log_exit_level(self, dir_details_df=None):
    now_ = datetime.now()
    start_time, dirname_ = self.__level_start_times_dirnames.pop(-1)
    time_elapsed = now_ - start_time
    self.__log_print('exited directory ', dirname_, 'at', now_, 'time elapsed:', time_elapsed, 
                   dir_details_df=dir_details_df)
   

  ###############################################################################
  def _df_to_str(self, df, extra_prefix, last_chars_last_prefix=''):
    result = ''
    if (df is None) or df.index.empty:
      return result
    df_str = df.to_string().split('\n')
    level = len(self.__level_start_times_dirnames)
    prefix = '║' * (level - 1) + extra_prefix
    for i, df_str_ in enumerate(df_str):
      if i == (len(df_str) - 1) and last_chars_last_prefix:
        prefix = prefix[:-len(last_chars_last_prefix)] + last_chars_last_prefix
      result += prefix + df_str_
    return result

  ###############################################################################
  def __log_print(self, message0, name, *args, dir_details_df=None):

    level = len(self.level_start_times_dirnames)

    prefix = '╟──── '
    if 'dir' in message0:
      prefix = prefix.replace('─', '═')
      prefix = ('╚' if 'exit' in message0.lower() else ('╠' if 'DELETED' in message0 else '╔')) + prefix[1:]
      if message0.lower().startswith('exited') and (dir_details_df is not None):
        prefix = prefix[:-2] + '╦ ' 

    # boxy symbols https://www.ncbi.nlm.nih.gov/staff/beck/charents/unicode/2500-257F.html
    string_ = '║' * (level - 1) + prefix + message0 + '`' + name + '` ' + ' '.join([str(a) for a in args if a])
    string_ += self._df_to_str(df=dir_details_df, extra_prefix=' ' * (len(prefix) - 2) + '╠═ ', last_chars_last_prefix='╚═ ')

    self.log_info(string_)

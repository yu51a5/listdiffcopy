import pandas as pd
from enum import Enum

from utils import put_together_framed_message
from logging_config import get_logger, LoggerExtra


#################################################################################
class FDStatus(Enum):
  LeftOnly_or_New = 0
  RightOnly_or_Deleted = 1
  Different_or_Updated = 2
  Identical = 3
  Error = 4

#################################################################################
_size_plus = {4: [' L', ' R'], 3: [''], 2: [''], 1: []}

class LoggerObj:
  status_names = None
  columns_df = pd.MultiIndex.from_tuples([["Files",  "Size"],  ["Files", "How Many"], ["Directories", "How Many"]])
  columns_files_df = {i : ['File Name'] + ['File Size' + j for j in _size_plus[i]] + (['File Status'] if i > 2 else []) for i in (1, 2, 3, 4)}
  index_listing_df = ["First level", "Total"]

  default_logger_extra = (get_logger(name="log"), LoggerExtra())

###################################################################################
  def __init__(self, logger_name=None, objects_to_sync_logger_with=[]):
    
    if logger_name is not None:
      self.__logger = get_logger(name=logger_name)
      self.__logger_extra = LoggerExtra()
    elif not objects_to_sync_logger_with:
      self.__logger = LoggerObj.default_logger_extra[0]
      self.__logger_extra = LoggerObj.default_logger_extra[1]
    else:
      self.__logger = None
      self.__logger_extra = None
    
    LoggerObj.sync_loggers(*([self] + objects_to_sync_logger_with))

  #################################################################################
  def sync_loggers(*args):
    not_owl = [arg for arg in args if not isinstance(arg, LoggerObj)]
    assert not not_owl, f"{not_owl} don't derive from LoggerObj"
    existing_loggers = [i for i, arg in enumerate(args) if arg.has_logger()]
    assert existing_loggers
    first_with_logger = args[existing_loggers[0]]

    errors = []
    for i, arg in enumerate(args):
      if arg.__logger is None:
        arg.__logger = first_with_logger.__logger 
        arg.__logger_extra = first_with_logger.__logger_extra 
      else:
        if not first_with_logger.is_my_logger_same_as(arg.__logger):
          errors.append(f"Loggers in argument {existing_loggers[0]}, {first_with_logger} and argument {i}, {arg}, are not the same")

    assert not errors, '/n'.join(errors)
    #return errors

  #################################################################################
  def has_logger(self):
    return self.__logger is not None

  #################################################################################
  def is_my_logger_same_as(self, another_logger):
    assert isinstance(self, LoggerObj)
    l = self.__logger
    return l is another_logger

  #################################################################################
  def log_title(self, title):
    msg = put_together_framed_message(message=title, char='*')
    self.log_info(msg)

  ###############################################################################
  def get_errors_count(self):
    return self.__logger_extra.get_errors_count()

  ###############################################################################
  def clear_errors_count(self):
    self.__logger_extra.clear_errors_count()

  ###############################################################################
  def log_critical(self, message):
    self.__logger.critical(message)
    self.__logger_extra.increment_errors_count()

  ###############################################################################
  def log_error(self, message):
    self.__logger.error(message)
    self.__logger_extra.increment_errors_count()

  ###############################################################################
  def log_warning(self, message):
    self.__logger.warning(message)

  ###############################################################################
  def log_info(self, message):
    self.__logger.info(message)

  ###############################################################################
  def log_debug(self, message):
    self.__logger.debug(message)
    
  ###############################################################################
  def log_mention_directory(self, dirname, message_to_print, message2):
    at_now = LoggerExtra.get_time_now()
    self.__log_print(f'{message_to_print} directory `{dirname}` {message2} {at_now}')
  
  ###############################################################################
  def log_enter_level(self, dirname, message_to_print, message2=''):
    at_now = self.__logger_extra.log_enter_level(dirname=dirname)
    self.__log_print(f'{message_to_print} directory `{dirname}` {message2} {at_now}')

  ###############################################################################
  def log_exit_level(self, dir_details_df=None):
    dirname_, at_now, time_elapsed = self.__logger_extra.log_exit_level()
    self.__log_print(f'exited directory `{dirname_}` {at_now}, time elapsed: {time_elapsed}', 
                       dir_details_df=dir_details_df)

  ###############################################################################
  def _df_to_str(self, df, extra_prefix, last_chars_last_prefix=''):
    if (df is None) or df.index.empty:
      return ''
    df_str = df.to_string().split('\n')
    level = self.__logger_extra.get_level_depth()
    prefix = '║' * level + extra_prefix
    result = []
    for i, df_str_ in enumerate(df_str):
      if i == (len(df_str) - 1) and last_chars_last_prefix:
        prefix = prefix[:-len(last_chars_last_prefix)] + last_chars_last_prefix
      result += [prefix + df_str_]
    return '\n'.join(result)

  ###############################################################################
  def __log_print(self, message, dir_details_df=None):

    level = self.__logger_extra.get_level_depth()

    prefix = ('╚' if (message.lower().startswith('exit') or message.lower().startswith('completed'))
                      else ('╠' if message.lower().startswith('delet') else '╔')) + '════ '
    if message.lower().startswith('exit'):
      level += 1
      if (dir_details_df is not None):
        prefix = prefix[:-2] + '╦ '

    # boxy symbols https://www.ncbi.nlm.nih.gov/staff/beck/charents/unicode/2500-257F.html
    string_ = '║' * (level - 1) + prefix + message
    if dir_details_df is not None:
      string_ += '\n' +  self._df_to_str(df=dir_details_df, extra_prefix=' ' * (len(prefix) - 2) + '╠═ ', last_chars_last_prefix='╚═ ')

    self.log_info(string_)

  ###############################################################################
  def start_file(self, path, message_to_print, message2=''):
    at_now, at_now_str = LoggerExtra.get_time_now2()
    self.__log_print(f'{message_to_print} file `{path}` {(message2 + " ") if message2 else ""}{at_now_str}')
    return at_now

  ###############################################################################
  def print_complete_file(self, data, when_started):
    self.print_files_df(data=data)
    at_now, at_now_str = LoggerExtra.get_time_now2()
    self.__log_print(f'Completed {at_now_str}, time elapsed {at_now - when_started}')

  ###############################################################################
  def print_files_df(self, data):
    if not data:
      return
    
    _data = data if isinstance(data[0], list) else [data]
    extra_prefix = '──── ' if isinstance(data[0], list) else '║ '
    
    how_many_columns = len(_data[0])
    if isinstance(_data[0][-1], FDStatus):
      for row_ in _data:
        row_[-1] = self.status_names_complete[row_[-1].value]
    df_files = pd.DataFrame(_data, columns=self.columns_files_df[how_many_columns])
    df_str = self._df_to_str(df_files, extra_prefix=extra_prefix)
    self.log_info(df_str)

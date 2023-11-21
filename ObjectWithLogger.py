import pandas as pd
from enum import Enum

from utils import creates_multi_index, put_together_framed_message
from logging_config import get_logger, LoggerExtra

#################################################################################
class FDStatus(Enum):
  LeftOnly_or_New = 0
  RightOnly_or_Deleted = 1
  Different_or_Updated = 2
  Identical = 3
  Error = 4

#################################################################################
class ObjectWithLogger:

  status_names = None
  columns_df = pd.MultiIndex.from_tuples([["Files",  "Size"],  ["Files", "How Many"], ["Directories", "How Many"]])
  columns_files_df = {i : ['File Name'] + ['File Size' + j for j in ([''] * (i - 2) if (i < 4) else [' L', ' R'])]+ (['File Status'] if i > 1 else []) for i in (1, 2, 3, 4)}
  index_listing_df = ["First level", "Total"]

###################################################################################
  def __init__(self, logger_name=None, objects_to_sync_logger_with=[], title=None):
    assert bool(logger_name) or bool(objects_to_sync_logger_with), "You must specify either a logger name or objects to sync it with"

    if logger_name is not None:
      self.__logger = get_logger(name=logger_name)
      self.__logger_extra = LoggerExtra()
    else:
      self.__logger = None
      self.__logger_extra = None
    
    ObjectWithLogger.sync_loggers(*([self] + objects_to_sync_logger_with))

    if title:
      self.log_title(title)
    if self.status_names:
      self.index_totals_df = pd.MultiIndex.from_tuples(creates_multi_index(self.index_listing_df, self.status_names))

  #################################################################################
  def sync_loggers(*args):
    not_owl = [arg for arg in args if not isinstance(arg, ObjectWithLogger)]
    assert not not_owl, f"{not_owl} don't derive from ObjectWithLogger"
    existing_loggers = [i for i, arg in enumerate(args) if arg.has_logger()]
    assert existing_loggers
    first_with_logger = args[existing_loggers[0]]

    for arg in args:
      if arg.__logger is None:
        arg.__logger = first_with_logger.__logger 
        arg.__logger_extra = first_with_logger.__logger_extra 
      else:
        assert first_with_logger.is_my_logger_same_as(arg.__logger)

  #################################################################################
  def has_logger(self):
    return self.__logger is not None

  #################################################################################
  def is_my_logger_same_as(self, another_logger):
    assert isinstance(self, ObjectWithLogger)
    l = self.__logger
    return l is another_logger, f'{l} {another_logger}'

  #################################################################################
  def log_title(self, title):
    msg = put_together_framed_message(message=title, char='*')
    self.log_info(msg)

  ###############################################################################
  def get_errors_count(self):
    return self.__logger_extra.get_errors_count()

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
    #message_lines = message.split('\n')
    #for ml in message_lines:
    self.__logger.info(message)

  ###############################################################################
  def log_enter_level(self, dirname, message_to_print, message2=''):
    at_now = self.__logger_extra.log_enter_level(dirname=dirname)
    self.__log_print(message_to_print + ' directory ', dirname, message2, at_now)

  ###############################################################################
  def log_exit_level(self, dir_details_df=None):
    dirname_, at_now, time_elapsed = self.__logger_extra.log_exit_level()
    self.__log_print('exited directory ', dirname_, at_now, 'time elapsed:', time_elapsed, 
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
  def __log_print(self, message0, name, *args, dir_details_df=None):

    level = self.__logger_extra.get_level_depth()

    prefix = '╟──── '
    if 'dir' in message0:
      prefix = prefix.replace('─', '═')
      prefix = ('╚' if 'exit' in message0.lower() else ('╠' if 'DELETED' in message0 else '╔')) + prefix[1:]
      if message0.lower().startswith('exited'):
        level += 1
        if (dir_details_df is not None):
          prefix = prefix[:-2] + '╦ '

    # boxy symbols https://www.ncbi.nlm.nih.gov/staff/beck/charents/unicode/2500-257F.html
    string_ = '║' * (level - 1) + prefix + message0 + '`' + name + '` ' + ' '.join([str(a) for a in args if a])
    df_str = self._df_to_str(df=dir_details_df, extra_prefix=' ' * (len(prefix) - 2) + '╠═ ', last_chars_last_prefix='╚═ ')
    if df_str:
      string_ += '\n' + df_str

    self.log_info(string_)

  ###############################################################################
  def print_files_df(self, data):
    if not data:
      return
    how_many_columns = len(data[0])
    if isinstance(data[0][-1], FDStatus):
      for row_ in data:
        row_[-1] = self.status_names[row_[-1].value]
    df_files = pd.DataFrame(data, columns=self.columns_files_df[how_many_columns])
    df_str = self._df_to_str(df_files, extra_prefix='──── ')
    self.log_info(df_str)

import os
import math
import pandas as pd
import numpy as np

from Logger import Logger, FDStatus
from utils import creates_multi_index

#################################################################################
class ObjectWithLogger:

  status_names = None
  columns_df = pd.MultiIndex.from_tuples([["Files",  "Size"],  ["Files", "How Many"], ["Directories", "How Many"]])
  columns_files_df = {i : ['File Name'] + ['File Size' + j for j in ([''] * (i - 2) if (i < 4) else [' L', ' R'])]+ (['File Status'] if i > 1 else []) for i in (1, 2, 3, 4)}
  index_listing_df = ["First level", "Total"]

###################################################################################
  def __init__(self, logger=None, objects_to_sync_logger_with=[], title=None):
    if logger is not None:
      assert isinstance(logger, Logger) or (logger is None), f'{type(logger)}, {logger} is not an instance of Logger'

    self.__logger = logger
    if Logger.DO_ERROR_THROWING_NOT_LOGGING:
      return
    ObjectWithLogger.sync_loggers(*([self] + objects_to_sync_logger_with))
      
    if title:
      self.log_title(title)
    if self.status_names:
      self.index_totals_df = pd.MultiIndex.from_tuples(creates_multi_index(self.index_listing_df, self.status_names))

  #################################################################################
  def sync_loggers(*args):
    not_owl = [arg for arg in args if not isinstance(arg, ObjectWithLogger)]
    assert not not_owl, f'{not_owl}'
    existing_loggers = [i for i, arg in enumerate(args) if arg.has_logger()]
    assert existing_loggers
    first_with_logger = args[existing_loggers[0]]
    first_with_logger.__logger.flush()
    for arg in args:
      if arg.__logger is None:
        arg.__logger = first_with_logger.__logger 
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
  def get_errors_count(self):
    return  self.__logger.get_errors_count()
    
  #################################################################################
  def log_title(self, title):
    self.__logger.log_print_framed(message=title, char='*')
    
  #################################################################################
  def log_warning(self, message):
    self.__logger.log_warning(message)

  #################################################################################
  def log_error(self, message):
    if Logger.DO_ERROR_THROWING_NOT_LOGGING:
      raise Exception(message)
    self.__logger.log_error(message)

  #################################################################################
  def log_print_basic(self, message):
    self.__logger.log_print_basic(message)

  #################################################################################
  def log_enter_level(self, *args, **kwargs):
    self.__logger.log_enter_level(*args, **kwargs)

  ###############################################################################
  def log_exit_level(self, *args, **kwargs):
    self.__logger.log_exit_level(*args, **kwargs)

  ###############################################################################
  def log_print_df(self, *args, **kwargs):
    self.__logger.log_print_df(*args, **kwargs)
  
  ###############################################################################
  def print_files_df(self, data):
    if not data:
      return
    how_many_columns = len(data[0])
    if isinstance(data[0][-1], FDStatus):
      for row_ in data:
        row_[-1] = self.status_names[row_[-1].value]
    df_files = pd.DataFrame(data, columns=self.columns_files_df[how_many_columns])
    self.log_print_df(df_files, extra_prefix='╟──── ')

  ###############################################################################
  def _list_files_directories_recursive(self, storage, dir_to_list, enforce_size_fetching, message2=''):
  
    self.log_enter_level(dirname=dir_to_list, message_to_print='Listing', message2=message2)
    
    files_, dirs_ = storage.get_filenames_and_directories(dir_to_list)

    df =  [[os.path.basename(f), storage.fetch_file_size(f)] for f in files_] if enforce_size_fetching \
    else [[os.path.basename(f)] for f in files_]
    self.print_files_df(data =df)

    total_size_first_level = sum([dfr[1] for dfr in df]) if enforce_size_fetching else math.nan
    totals = np.array([total_size_first_level, len(files_), len(dirs_)])
    
    dirs_dict = {}  
    for dir_ in dirs_:
      dir_totals, dir_files, dir_dirs_dict = self._list_files_directories_recursive(storage=storage, dir_to_list=dir_, enforce_size_fetching=enforce_size_fetching)
      totals += dir_totals
      dirs_dict[dir_] = (dir_files, dir_dirs_dict)
    
    table_stats = [[total_size_first_level, len(files_), len(dirs_)], 
                   totals.tolist()]

    kwargs = {}
    if enforce_size_fetching or dirs_:
      kwargs['dir_details_df'] = pd.DataFrame(table_stats, index=self.index_listing_df, columns=self.columns_df)
    self.log_exit_level(**kwargs)
  
    return totals, files_, dirs_dict
    
###############################################################################
  def _list_a_file(self, storage, file_path, enforce_size_fetching):
    file_info = storage.fetch_file_info(filename=file_path, enforce_size_fetching=enforce_size_fetching)
    self.print_files_df(data = [[os.path.basename(file_path), file_info['size']]] if enforce_size_fetching 
                          else [[os.path.basename(file_path)] ])
        
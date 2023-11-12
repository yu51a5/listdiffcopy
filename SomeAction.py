import os

import pandas as pd
import numpy as np

from SomeActionLogger import Logger
from StorageBase import FDStatus

#################################################################################
def creates_multi_index(index_1, index_2):
  index_1_expanded = [i1  for i1 in index_1 for _ in index_2]
  index_2_expanded = index_2 * len(index_1)
  result = list(map(list, zip(index_1_expanded, index_2_expanded)))
  return result

#################################################################################
class SomeAction(Logger):

  status_names = None
  columns_df = pd.MultiIndex.from_tuples([["Files",  "Size"],  ["Files", "How Many"], ["Directories", "How Many"]])
  columns_files_df = {i : ['File Name'] + ['File Size' + j for j in ([''] * (i - 2) if (i < 4) else [' L', ' R'])]+ ['File Status'] for i in (3, 4)}
  index_listing_df = ["First level", "Total"]

  ###############################################################################
  def __init__(self, **kwargs):
    if self.status_names:
      self.index_totals_df = pd.MultiIndex.from_tuples(creates_multi_index(self.index_listing_df, self.status_names))
    super().__init__(**kwargs)

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
    
    files_, dirs_ = storage.get_filenames_and_directories(dir_to_list, enforce_size_fetching=enforce_size_fetching)
    total_size_first_level = sum([storage.fetch_file_size(f) for f in files_])
    totals = np.array([total_size_first_level, len(files_), len(dirs_)])
  
    self.print_files_df(data = [[os.path.basename(f), storage.get_file_info(f, 'size')] for f in files_] if enforce_size_fetching 
                          else [[os.path.basename(f)] for f in files_])
    
    dirs_dict = {}  
    for dir_ in dirs_:
      dir_totals, dir_files, dir_dirs_dict = self._list_files_directories_recursive(storage=storage, dir_to_list=dir_, enforce_size_fetching=enforce_size_fetching)
      totals += dir_totals
      dirs_dict[dir_] = (dir_files, dir_dirs_dict)
    
    table_stats = [[total_size_first_level, len(files_), len(dirs_)], 
                   totals.tolist()]
    
    self.log_exit_level(dir_details_df=pd.DataFrame(table_stats, index=self.index_listing_df, columns=self.columns_df))
  
    return totals, files_, dirs_dict
    
###############################################################################
  def _list_a_file(self, storage, file_path, enforce_size_fetching):
    file_info = storage.fetch_file_info(filename=file_path, enforce_size_fetching=enforce_size_fetching)
    self.print_files_df(data = [[os.path.basename(file_path), file_info['size']]] if enforce_size_fetching 
                          else [[os.path.basename(file_path)] ])
        
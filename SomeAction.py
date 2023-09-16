import os
import pandas as pd
import numpy as np
from SomeActionLogger import Logger

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
  columns_files_df = ['File Name', 'File Size', 'File Status']
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
    if how_many_columns == 3:
      for row_ in data:
        row_[-1] = self.status_names[row_[-1]]
    df_files = pd.DataFrame(data, columns=self.columns_files_df[:how_many_columns])
    self.log_print_df(df_files, extra_prefix='╟──── ')

  ###############################################################################
  def _list_files_directories_recursive(self, storage, dir_to_list, enforce_size_fetching, message2=''):
  
    self.log_enter_level(dirname=dir_to_list, message_to_print='Listing', message2=message2)
    
    files_, dirs_, total_size_first_level = storage.get_filenames_and_directories(dir_to_list, enforce_size_fetching=enforce_size_fetching)
    totals = np.array([total_size_first_level, len(files_), len(dirs_)])
  
    self.print_files_df(data = [[os.path.basename(f), storage.get_file_info(f, 'size')] for f in files_] if enforce_size_fetching 
                          else [[os.path.basename(f)] for f in files_])
      
    for dir_ in dirs_:
      dir_totals = self._list_files_directories_recursive(storage=storage, dir_to_list=dir_, enforce_size_fetching=enforce_size_fetching)
      totals += dir_totals
    
    table_stats = [[total_size_first_level, len(files_), len(dirs_)], 
                   totals.tolist()]
    
    self.log_exit_level(dir_details_df=pd.DataFrame(table_stats, index=self.index_listing_df, columns=self.columns_df))
  
    return totals

###############################################################################
def list_contents(StorageType, dir_to_list, enforce_size_fetching=True, kwargs={}):
  with StorageType(**kwargs) as storage:
    with SomeAction(title=f'Listing {storage.str(dir_to_list)} ' + '*'*8,
                    storages_dirs_that_must_exist=((storage, dir_to_list),)) as sa:
      if sa.dir_exists():
        sa._list_files_directories_recursive(storage=storage, dir_to_list=dir_to_list, enforce_size_fetching=enforce_size_fetching) 
    
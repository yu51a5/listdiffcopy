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

###############################################################################
def list(StorageType, path, enforce_size_fetching=True, kwargs_storage={}):
  with StorageType(**kwargs_storage) as storage:
    with SomeAction(title=f'Listing {storage.str(path)}') as sa:
      path_exist_is_dir_not_file = storage.check_path_exist_is_dir_not_file(path)
      if path_exist_is_dir_not_file is True:
        sa._list_files_directories_recursive(storage=storage, dir_to_list=path, enforce_size_fetching=enforce_size_fetching)
      if path_exist_is_dir_not_file is False:
        sa._list_a_file(storage=storage, file_path=path, enforce_size_fetching=enforce_size_fetching)  
      elif path_exist_is_dir_not_file == "both":
        sa.log_error(f"{storage.str(path)} is both a file and a directory")
      else:
        sa.log_error(f"{storage.str(path)} does not exist")  

###############################################################################
def delete(StorageType, path, kwargs_storage={}):
  with StorageType(**kwargs_storage) as storage:
    with SomeAction(title=f'Deleting {storage.str(path)}') as sa:
      path_exist_is_dir_not_file = storage.check_path_exist_is_dir_not_file(path)
      if path_exist_is_dir_not_file is True:
        storage.delete_directory(path)
      elif path_exist_is_dir_not_file is False:
        storage.delete_file(path)
      elif path_exist_is_dir_not_file == "both":
        sa.log_error(f"{storage.str(path)} is both a file and a directory")
      else:
        sa.log_error(f"{storage.str(path)} does not exist")

###############################################################################
def create_directory(StorageType, dir_name, kwargs_storage={}):
  with StorageType(**kwargs_storage) as storage:
    with SomeAction(title=f'Creating {storage.str(dir_name)}') as sa:
      path_exist_is_dir_not_file = storage.check_path_exist_is_dir_not_file(path)
      if path_exist_is_dir_not_file is not None:
        sa.log_warning(message=f"Skipping because {storage.str(dir_name)} exists")
      else:
        storage.create_directory(dir_name)
        
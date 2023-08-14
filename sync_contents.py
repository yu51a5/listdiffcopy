import os
import pandas as pd

from Logger import Logger, log_enter_level, log_exit_level, log_print, add_sizes, creates_multi_index

columns_df = pd.MultiIndex.from_tuples([["Files",  "Size"],  ["Files", "How Many"], ["Directories", "How Many"]])
index_listing_df = ["First level", "Total"]
index_sync_df = pd.MultiIndex.from_tuples(creates_multi_index(["Created", "Updated", "Deleted"], index_listing_df))
index_comp_df = pd.MultiIndex.from_tuples(creates_multi_index(["Both", "Left Only", "Right Only"], index_listing_df))

###############################################################################
def _compare_files_directories_recursive(storage_from, storage_to, root_dir_from, root_dir_to, common_dir_appendix):

  log_enter_level(f'Comparing {common_dir_appendix} in {storage_from.str(root_dir_from)} against {storage_to.str(root_dir_to)}')
                               
  files_from, dirs_from, _ = storage_from.get_filenames_and_directories(os.path.join(root_dir_from, common_dir_appendix))
  files_to  , dirs_to  , _ = storage_to.get_filenames_and_directories(os.path.join(root_dir_to, common_dir_appendix))

  if_from = -len(files_from)
  if_to = -len(files_to)

  message2_to = f'; there is no equivalent in {storage_to.str(os.path.join(root_dir_to, common_dir_appendix))}'
  message2_from = f'; there is no equivalent in {storage_from.str(os.path.join(root_dir_from, common_dir_appendix))}'

  while (if_from < 0) or (if_to < 0):
    if if_from < 0:
      file_from = files_from[if_from]
      basename_from = os.path.basename(file_from)
    if if_to < 0:
      file_to   = files_to[  if_to]
      basename_to   = os.path.basename(file_to)
    if (if_to == 0) or (basename_from < basename_to):
      storage_from.list_file(file_from, message2=message2_to)
      if_from += 1
    if (if_from == 0) or (basename_to < basename_from):
      storage_to.list_file(file_to, message2=message2_from)
      if_to += 1  
    if (basename_from == basename_to):
      if_from += 1
      if_to += 1
      files_are_identical, extra_message, _ = storage_from.compare_files(my_filename=file_from, 
                                                                           source=storage_to, 
                                                                           source_filename=file_to)
      log_print('file', os.path.join(common_dir_appendix, basename_from), "is", 
                ("identical to" if files_are_identical else "different from"), 
                os.path.join(common_dir_appendix, basename_to), 
                extra_message)

  id_from = -len(dirs_from)
  id_to = -len(dirs_to)

  while (id_from < 0) or (id_to < 0):
    if id_from < 0:
      dir_from = dirs_from[id_from]
      basename_from = os.path.basename(dir_from)
    if id_to < 0:
      dir_to   = dirs_to[  id_to]
      basename_to   = os.path.basename(dir_to)
    if (id_to == 0) or (basename_from < basename_to):
      _list_files_directories_recursive(storage=storage_from, dir_to_list=dir_from, message2=message2_to) 
      id_from += 1
    if (id_from == 0) or (basename_to < basename_from):
      _list_files_directories_recursive(storage=storage_to, dir_to_list=dir_to, message2=message2_from) 
      id_to += 1  
    if (basename_from == basename_to):
      id_from += 1
      id_to += 1
      _compare_files_directories_recursive(storage_from, storage_to, 
                                           root_dir_from=root_dir_from, 
                                           root_dir_to=root_dir_to, 
                                           common_dir_appendix=os.path.join(common_dir_appendix, basename_from))

  log_exit_level(dir_details_df=pd.DataFrame(table_stats, index=index_comp_df, columns=columns_df))

  
###############################################################################
def compare_contents(StorageFromType, dir_from, StorageToType, dir_to, kwargs_from={}, kwargs_to={}):
  with StorageFromType(**kwargs_from) as storage_from:
    with StorageToType(**kwargs_to) as storage_to: 
      with Logger(f'Comparing {storage_from.str(dir_from)}, to {storage_to.str(dir_to)}',
                  ((storage_from, dir_from), (storage_to, dir_to))) as logger:
        if logger.dir_exists():
          _compare_files_directories_recursive(storage_from=storage_from, 
                                            storage_to=storage_to, 
                                            root_dir_from=dir_from, 
                                            root_dir_to=dir_to)

###############################################################################
def _sync_files_directories_recursive(storage_from, storage_to, current_directory_from, directory_to_root):

  to_dirname = os.path.join(directory_to_root, os.path.basename(current_directory_from))
  dir_to_exists = storage_to.check_directory_exists(path=to_dirname, create_if_doesnt_exist=True)
  log_enter_level(f"{'kept __' if (dir_to_exists != 'created') else 'CREATED'} {storage2.str(to_dirname)}")
                               
  files_from, dirs_from, _ = storage_from.get_filenames_and_directories(current_directory_from)
  files_to  , dirs_to  , _ = storage_to.get_filenames_and_directories(to_dirname)
  
  for to_filename in files_to:
    from_filename = os.path.join(current_directory_from, os.path.basename(to_filename))
    if from_filename not in files_from:
      storage_to.delete_file(to_filename)

  for from_filename in files_from:
    to_filename = os.path.join(to_dirname, os.path.basename(from_filename))
    if to_filename not in files_to:
      storage_to.create_file(my_filename=to_filename, 
                             source=storage_from, 
                             source_filename=from_filename)
    else:
      storage_to.compare_and_update_file(my_filename=to_filename, 
                                           source=storage_from, 
                                           source_filename=from_filename)

  for to_dirname_ in dirs_to:
    from_dirname = os.path.join(current_directory_from, os.path.basename(to_dirname_))
    if from_dirname not in dirs_from:
      storage_to.delete_directory(to_dirname_)

  for from_dirname in dirs_from:
    _sync_files_directories_recursive(storage_from=storage_from, 
                                      storage_to=storage_to, 
                                      current_directory_from=from_dirname, 
                                      directory_to_root=to_dirname)
  
  log_exit_level(dir_details_df=pd.DataFrame(table_stats, index=index_sync_df, columns=columns_df))

###############################################################################
def sync_contents(StorageFromType, dir_from, StorageToType, dir_to, kwargs_from={}, kwargs_to={}):
  with StorageFromType(**kwargs_from) as storage_from:
    with StorageToType(**kwargs_to) as storage_to: 
      with Logger(f'Synchronizing {storage_from.str(dir_from)} with {storage_to.str(dir_to)}',
                  ((storage_from, dir_from),)) as logger:
        if logger.dir_exists():
          _sync_files_directories_recursive(storage_from=storage_from, 
                                            storage_to=storage_to, 
                                            current_directory_from=dir_from, 
                                            directory_to_root=dir_to)

###############################################################################
def _list_files_directories_recursive(storage, dir_to_list, message2=''):

  log_enter_level(dirname=dir_to_list, message_to_print='list', message2=message2)
  
  files_, dirs_, total_size_first_level = storage.get_filenames_and_directories(dir_to_list)
  total_files_qty, total_size, total_dirs_qty = len(files_), total_size_first_level, len(dirs_)
  
  for file_ in files_:
    storage.list_file(file_)

  for dir_ in dirs_:
    d_files_size, d_files_qty, d_dirs_qty = _list_files_directories_recursive(storage=storage, dir_to_list=dir_)
    total_size = add_sizes(total_size, d_files_size)
    total_files_qty += d_files_qty
    total_dirs_qty += d_dirs_qty

  table_stats = [[total_size_first_level, len(files_),     len(dirs_)],
                 [total_size,             total_files_qty, total_dirs_qty],]
    
  log_exit_level(dir_details_df=pd.DataFrame(table_stats, index=index_listing_df, columns=columns_df))

  return table_stats[1]
  
###############################################################################
def list_contents(StorageType, dir_to_list, kwargs={}):
  with StorageType(**kwargs) as storage:
    with Logger(f'Listing {storage.str(dir_to_list)} ' + '*'*8,
                  ((storage, dir_to_list),)) as logger:
      if logger.dir_exists():
        _list_files_directories_recursive(storage=storage, dir_to_list=dir_to_list) 
  
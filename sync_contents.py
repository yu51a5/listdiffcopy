import os

from logging_printing import reset_level, log_entering_directory, log_exiting_directory
from dry_run import is_dry_run

###############################################################################
def _sync_files_directories_recursive(storage_from, storage_to, current_directory_from, directory_to_root):

  to_dirname = os.path.join(directory_to_root, os.path.basename(current_directory_from))
  dir_to_exists = storage_to.check_directory_exists(path=to_dirname, create_if_doesnt_exist=True)
  log_entering_directory(to_dirname, 'kept __' if (dir_to_exists != "created") else 'CREATED')
                               
  files_from, dirs_from = storage_from.get_filenames_and_directories(current_directory_from)
  files_to  , dirs_to   = storage_to.get_filenames_and_directories(to_dirname)
  
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
  
  log_exiting_directory()

###############################################################################
def sync_contents(StorageFromType, dir_from, StorageToType, dir_to, kwargs_from={}, kwargs_to={}):
  with StorageFromType(**kwargs_from) as storage_from:
    with StorageToType(**kwargs_to) as storage_to: 
      print(('Comparing' if is_dry_run() else 'Synchronizing from') + f' {type(storage_from).__name__}, folder `{dir_from}`, to {type(storage_to).__name__}, folder `{dir_to}`')
      reset_level()
      dir_from_exists = storage_from.check_directory_exists(path=dir_from, create_if_doesnt_exist=None)
      if dir_from_exists:
        _sync_files_directories_recursive(storage_from=storage_from, 
                                          storage_to=storage_to, 
                                          current_directory_from=dir_from, 
                                          directory_to_root=dir_to)

###############################################################################
def _list_files_directories_recursive(storage, dir_to_list):

  log_entering_directory(dir_to_list)
  
  files_, dirs_ = storage.get_filenames_and_directories(dir_to_list)
  
  for file_ in files_:
    storage.list_file(file_)

  for dir_ in dirs_:
    _list_files_directories_recursive(storage=storage, dir_to_list=dir_)
    
  log_exiting_directory()
  
###############################################################################
def list_contents(StorageType, dir_to_list, kwargs={}):
  with StorageType(**kwargs) as storage:
    print(f'Listing folder `{dir_to_list}`, {type(storage).__name__} ' + '*'*8)
    reset_level()
    dir_exists = storage.check_directory_exists(path=dir_to_list, create_if_doesnt_exist=None)
    if dir_exists:
      _list_files_directories_recursive(storage=storage, dir_to_list=dir_to_list) 
  
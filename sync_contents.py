import os

from StorageBase import reset_level, increment_level, decrement_level, unset_level, is_dry_run
from settings import skip_if_source_directory_doesnt_exist

###############################################################################
def _sync_files_directories_recursive(storage_from, storage_to, current_directory_from, current_directory_to):
                               
  files_from, dirs_from = storage_from.get_filenames_and_directories(current_directory_from)
  files_to  , dirs_to   = storage_to.get_filenames_and_directories(current_directory_to)      

  increment_level()
  
  for to_filename in files_to:
    from_filename = os.path.join(current_directory_from, os.path.basename(to_filename))
    if from_filename not in files_from:
      storage_to.delete_file(to_filename)

  for from_filename in files_from:
    to_filename = os.path.join(current_directory_to, os.path.basename(from_filename))
    if to_filename not in files_to:
      storage_to.create_file(my_filename=to_filename, 
                             source=storage_from, 
                             source_filename=from_filename)
    else:
      storage_to.compare_and_update_file(my_filename=to_filename, 
                                           source=storage_from, 
                                           source_filename=from_filename)

  for to_dirname in dirs_to:
    from_dirname = os.path.join(current_directory_from, os.path.basename(to_dirname))
    if from_dirname not in dirs_from:
      storage_to.delete_directory(to_dirname)

  for from_dirname in dirs_from:
    to_dirname = os.path.join(current_directory_to, os.path.basename(from_dirname))
    if to_dirname not in dirs_to:
      storage_to.create_directory(to_dirname)
    else:
      storage_to.log_entering_directory(to_dirname)
    files_directories_recursive(storage_from=storage_from, 
                                storage_to=storage_to, 
                                current_directory_from=from_dirname, 
                                current_directory_to=to_dirname)
  decrement_level()

###############################################################################
def sync_contents(StorageFromType, dir_from, StorageToType, dir_to, kwargs_from={}, kwargs_to={}):
  with StorageFromType(**kwargs_from) as storage_from:
    with StorageToType(**kwargs_to) as storage_to: 
      print(('Comparing' if is_dry_run() else 'Synchronizing from') + f' {type(storage_from).__name__}, folder `{dir_from}`, to {type(storage_to).__name__}, folder `{dir_to}`')
      
      dir_from_exists = storage_from.check_directory_exists(path=dir_from, create_if_doesnt_exist=False)
      if skip_if_source_directory_doesnt_exist and (not dir_from_exists):
        print(f"Skipping because there is no folder `{dir_from}` in  {type(storage_from).__name__}")
      else:
        reset_level()
        dir_to_exists = storage_to.check_directory_exists(path=dir_to, create_if_doesnt_exist=True)
        if dir_to_exists != "created":
          storage_to.log_entering_directory(dir_to)
        _sync_files_directories_recursive(storage_from=storage_from, 
                                          storage_to=storage_to, 
                                          current_directory_from=dir_from, 
                                          current_directory_to=dir_to) 
        unset_level()

###############################################################################
def _list_files_directories_recursive(storage, dir_to_list):
  files_, dirs_ = storage.get_filenames_and_directories(dir_to_list)      

  increment_level()
  
  for file_ in files_:
    storage.list_file(file_)

  for dir_ in dirs_:
    storage.list_directory(dir_)
    _list_files_directories_recursive(storage=storage, dir_to_list=dir_)
    
  decrement_level()
  
###############################################################################
def list_contents(StorageType, dir_to_list, kwargs={}):
  with StorageType(**kwargs) as storage:
    print(f'Listing folder `{dir_to_list}`, {type(storage).__name__} ' + '*'*8)
    reset_level()
    dir_exists = storage.check_directory_exists(path=dir_to_list, create_if_doesnt_exist=False)
    if not dir_exists:
      print(f"Skipping because there is no folder `{dir_to_list}` in {type(storage).__name__}")
    else:
      storage.list_directory(dir_to_list)
      _list_files_directories_recursive(storage=storage, dir_to_list=dir_to_list) 
    unset_level()
  
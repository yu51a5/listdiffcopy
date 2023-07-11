import os

from StorageBase import reset_level, increment_level, decrement_level, unset_level

###############################################################################
def files_directories_recursive(storage_from, storage_to, current_directory_from, current_directory_to):

  increment_level()
                                  
  files_from, dirs_from = storage_from.get_filenames_and_directories(current_directory_from)
  files_to  , dirs_to   = storage_to.get_filenames_and_directories(current_directory_to)      
                                  
  for to_filename in files_to:
    from_filename = os.path.join(current_directory_from, os.path.basename(to_filename))
    if from_filename not in files_from:
      storage_to.delete_file(to_filename)

  for from_filename in files_from:
    to_filename = os.path.join(current_directory_to, os.path.basename(from_filename))
    if to_filename not in files_to:
      storage_to.create_a_file(my_filename=to_filename, 
                               source=storage_from, 
                               source_filename=from_filename)
    else:
      storage_to.compare_and_update_a_file(my_filename=to_filename, 
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
    files_directories_recursive(storage_from=storage_from, 
                                storage_to=storage_to, 
                                current_directory_from=from_dirname, 
                                current_directory_to=to_dirname)
  decrement_level()

###############################################################################
def sync_contents(storage_from__storage_to__folders, StorageFromType, StorageToType, kwargs_from={}, kwargs_to={}):
  with StorageFromType(**kwargs_from) as storage_from:
    with StorageToType(**kwargs_to) as storage_to: 
      for root_from_dir, root_to_dir in storage_from__storage_to__folders:
        reset_level()
        files_directories_recursive(storage_from=storage_from, 
                                    storage_to=storage_to, 
                                    current_directory_from=root_from_dir, 
                                    current_directory_to=root_to_dir) 
        storage_from.clean_cache()
        storage_to.clean_cache()
        
  unset_level()
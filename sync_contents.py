import os

###############################################################################
def files_directories_recursive(files_1, directories_1, storage_1, files_2, directories_2, storage_2, 
                                current_directory_1, current_directory_2, do_recursion_if_dir_not_found,
                                func_both_files_exist=None, func_file_1_not_found_in_2=None, func_directory_1_not_found_in_2=None):
                                  
  file_basenames_2 = [os.path.basename(f2) for f2 in files_2]
  for f1 in files_1:
    if os.path.basename(f1) not in file_basenames_2:
      if func_file_1_not_found_in_2:
        func_file_1_not_found_in_2(file_1_with_path=f1, 
                                  storage_1=storage_1, 
                                  root_directory_2=current_directory_2, 
                                  storage_2=storage_2)
    else:
      if func_both_files_exist:
        func_both_files_exist(file_1_with_path=f1, 
                              storage_1=storage_1, 
                              file_2_with_path=os.path.join(current_directory_2, os.path.basename(f1)), 
                              storage_2=storage_2)

  dir_basenames_2 = [os.path.basename(d2) for d2 in directories_2]                                
  for d1 in directories_1:
    full_path_dir_2 = os.path.join(current_directory_2, os.path.basename(d1))
    if os.path.basename(d1) not in dir_basenames_2:
      if func_directory_1_not_found_in_2:
        func_directory_1_not_found_in_2(directory_1_with_path=d1, 
                                        storage_1=storage_1, 
                                        root_directory_2=current_directory_2, 
                                        storage_2=storage_2)
      if not do_recursion_if_dir_not_found:
        continue
      directories_2[full_path_dir_2] = ([], {})
    files_directories_recursive(*directories_1[d1], storage_1, *directories_2[full_path_dir_2], storage_2, 
                                  current_directory_1=d1, 
                                  current_directory_2=full_path_dir_2,
                                  do_recursion_if_dir_not_found=do_recursion_if_dir_not_found,
                                  func_both_files_exist=func_both_files_exist, 
                                  func_file_1_not_found_in_2=func_file_1_not_found_in_2, 
                                  func_directory_1_not_found_in_2=func_directory_1_not_found_in_2)

###############################################################################
def sync_contents(storage_from__storage_to__folders, StorageFromType, StorageToType, kwargs_from={}, kwargs_to={}):
  with StorageFromType(**kwargs_from) as storage_from:
    with StorageToType(**kwargs_to) as storage_to:
    
      for root_from_dir, root_to_dir in storage_from__storage_to__folders:
        print('='*50)
        print(f'Synchronising: {StorageFromType} {root_from_dir} -> {StorageToType} {root_to_dir}')
        print('\nall_from_files')
        all_from_files, all_from_directories = storage_from.get_filenames_and_directories_and_cache(root=root_from_dir)
        print('\nall_to_files  ')
        all_to_files  , all_to_directories   =   storage_to.get_filenames_and_directories_and_cache(root=root_to_dir)
        print('='*50)

        # removing obsolete files ###########################################################################
        def del_file_in_storage_1(file_1_with_path, storage_1, root_directory_2, storage_2):
          storage_1.delete_file(file_1_with_path)
          
        def del_directory_storage_1(directory_1_with_path, storage_1, root_directory_2, storage_2):
          storage_1.delete_directory(directory_1_with_path)
  
        if all_to_files or all_to_directories:
          files_directories_recursive(files_1=all_to_files  , directories_1=  all_to_directories, storage_1=storage_to, 
                                      files_2=all_from_files, directories_2=all_from_directories, storage_2=None, 
                                      current_directory_1=root_to_dir, current_directory_2=root_from_dir,
                                      do_recursion_if_dir_not_found=False,
                                      func_file_1_not_found_in_2=del_file_in_storage_1, 
                                      func_directory_1_not_found_in_2=del_directory_storage_1)
          
        # fetch files info ###################################################################################
        storage_from.fetch_files_info()
        storage_to.fetch_files_info()

        # adding missing files ###############################################################################
        def create_file_in_storage_2(file_1_with_path, storage_1, root_directory_2, storage_2):
          storage_2.create_a_file(my_filename=os.path.join(root_directory_2, os.path.basename(file_1_with_path)), 
                                  another_source=storage_1, 
                                  another_source_filename=file_1_with_path)
        
        def update_file_in_storage_2(file_1_with_path, storage_1, file_2_with_path, storage_2):
          storage_2.compare_and_update_a_file(my_filename=file_2_with_path, another_source=storage_1, another_source_filename=file_1_with_path)
  
        def create_directory_in_storage_2(directory_1_with_path, storage_1, root_directory_2, storage_2):
          storage_2.create_directory(os.path.join(root_directory_2, os.path.basename(directory_1_with_path)))
  
        files_directories_recursive(files_1=all_from_files, directories_1=all_from_directories, storage_1=storage_from, 
                                    files_2=all_to_files  , directories_2=  all_to_directories, storage_2=storage_to, 
                                    current_directory_1=root_from_dir, current_directory_2=root_to_dir,
                                    do_recursion_if_dir_not_found=True,
                                    func_file_1_not_found_in_2=create_file_in_storage_2, 
                                    func_directory_1_not_found_in_2=create_directory_in_storage_2,
                                    func_both_files_exist=update_file_in_storage_2)
        
        # clean cache ##########################################################################################
        storage_from.clean_cache()  
        storage_to.clean_cache()  

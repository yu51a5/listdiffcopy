import os

def print_files_directories_recursive(files, directories):
  print('Files----')
  for f in files:
    print(f)
  
  for d, (fi, dir) in directories.items():
    print(f'Directory {d}----')
    print_files_directories_recursive(fi, dir)

###############################################################################
def files_directories_recursive(files_1, directories_1, storage_1, files_2, directories_2, storage_2, 
                                current_directory_1, current_directory_2, 
                                func_both_files_exist=None, func_file_1_not_found_in_2=None, func_directory_1_not_found_in_2=None):
  for f1 in files_1:
    if f1 not in files_2:
      if func_file_1_not_found_in_2:
        func_file_1_not_found_in_2(file_1_with_path=os.path.join(current_directory_1, f1), 
                                  storage_1=storage_1, 
                                  root_directory_2=current_directory_2, 
                                  storage_2=storage_2)
    else:
      if func_both_files_exist:
        func_both_files_exist(file_1_with_path=os.path.join(current_directory_1, f1), 
                              storage_1=storage_1, 
                              file_2_with_path=os.path.join(current_directory_2, f1), 
                              storage_2=storage_2)
  for d1 in directories_1:
    if d1 not in directories_2:
      if func_directory_1_not_found_in_2:
        func_directory_1_not_found_in_2(directory_1_with_path=os.path.join(current_directory_1, d1), 
                                        storage_1=storage_1, 
                                        root_directory_2=current_directory_2, 
                                        storage_2=storage_2)
    else:
      files_directories_recursive(*directories_1[d1], storage_1, *directories_2[d1], storage_2, 
                                  current_directory_1=os.path.join(current_directory_1, d1), 
                                  current_directory_2=os.path.join(current_directory_2, d1),
                                  func_both_files_exist=func_both_files_exist, 
                                  func_file_not_found=func_file_1_not_found_in_2, 
                                  func_directory_not_found=func_directory_1_not_found_in_2)

###############################################################################
def sync_contents(storage_from__storage_to__folders, StorageFromType, StorageToType, kwargs_from={}, kwargs_to={}):
  with StorageFromType(**kwargs_from) as storage_from:
    with StorageToType(**kwargs_to) as storage_to:
    
      for root_from_dir, root_to_dir in storage_from__storage_to__folders:
        print(f'Synchronising: {StorageFromType} {root_from_dir} -> {StorageToType} {root_to_dir}')
        all_from_files, all_from_directories = storage_from.get_filenames_and_directories_and_cache(root=root_from_dir)
        all_to_files  , all_to_directories   =   storage_to.get_filenames_and_directories_and_cache(root=root_to_dir)
  
        print('\nall_from_files')
        print_files_directories_recursive(all_from_files, all_from_directories)
        
        print('\nall_to_files  ')
        print_files_directories_recursive(all_to_files  , all_to_directories)

        continue
  
        def del_file_in_storage_1(file_1_with_path, storage_1, root_directory_2, storage_2):
          storage_1.delete_file(file_1_with_path)
          print('removed file ' + file_1_with_path)
          
        def del_directory_storage_1(directory_1_with_path, storage_1, root_directory_2, storage_2):
          storage_1.delete_directory(directory_1_with_path)
          print('removed directory ' + directory_1_with_path)
  
        if all_to_files is None:
          storage_to.create_directory(root_to_dir)
          all_to_files, all_from_directories = [], {}
        else:
          # removing the files in github repo that are no longer on SFTP server
          files_directories_recursive(files_1=all_to_files  , directories_1=  all_to_directories, storage_1=storage_to, 
                                      files_2=all_from_files, directories_2=all_from_directories, storage_2=None, 
                                      current_directory_1=root_to_dir, current_directory_2=root_from_dir,
                                      func_file_1_not_found_in_2=del_file_in_storage_1, 
                                      func_directory_1_not_found_in_2=del_directory_storage_1)
    
        def create_file_in_storage_2(file_1_with_path, storage_1, root_directory_2, storage_2):
          result_path = storage_1.create_file_in_another_storage(file_1_with_path, root_directory_2, storage_2)
          print('created file ' + result_path)
  
        def update_file_in_storage_2(file_1_with_path, storage_1, file_2_with_path, storage_2):
          result_path = storage_1.update_file_in_another_storage(file_1_with_path, file_2_with_path, storage_2)
          print('updated file ' + result_path)
  
        def create_directory_in_storage_2(directory_1_with_path, storage_1, root_directory_2, storage_2):
          result_path = storage_2.create_directory(os.path.join(root_directory_2, os.path.basename(directory_1_with_path)))
          print('created directory ' + result_path)
  
        # adding missing files
        files_directories_recursive(files_1=all_from_files, directories_1=all_from_directories, storage_1=storage_from, 
                                    files_2=all_to_files  , directories_2=  all_to_directories, storage_2=storage_to, 
                                    current_directory_1=root_from_dir, current_directory_2=root_to_dir,
                                    func_file_1_not_found_in_2=create_file_in_storage_2, 
                                    func_directory_1_not_found_in_2=create_directory_in_storage_2,
                                    func_both_files_exist=update_file_in_storage_2)
                
        storage_from.clean_cache()  
        storage_to.clean_cache()  

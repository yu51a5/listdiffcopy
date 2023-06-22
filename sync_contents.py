import os

###############################################################################
def files_directories_recursive(files_1, directories_1, storage_1, files_2, directories_2, storage_2, 
                                current_directory_1, current_directory_2,
                                func_both_files_exist, func_file_not_found=None, func_directory_not_found=None):
  for f1 in files_1:
    if f1 not in files_2:
      if func_file_not_found:
        func_file_not_found(f1, storage_1, storage_2, current_directory_1, current_directory_2)
    else:
      func_both_files_exist(os.path.join(current_directory_1, f1), os.path.join(current_directory_2, f1), storage_1, storage_2)
  for d1 in directories_1:
    if d1 not in directories_2:
      if func_directory_not_found:
        func_directory_not_found(d1, storage_1, storage_2, current_directory_1, current_directory_2)
    else:
      files_directories_recursive(*directories_1[d1], storage_1, *directories_2[d1], storage_2, 
                                  current_directory_1=os.path.join(current_directory_1, d1), 
                                  current_directory_2=os.path.join(current_directory_2, d1),
                                  check_files_are_the_same=check_files_are_the_same,
                                  func_file_not_found=func_file_not_found, 
                                  func_files_different=func_files_different, 
                                  func_directory_not_found=func_directory_not_found)

###############################################################################
def sync_contents(storage_from__storage_to__folders, storage_from, storage_to):
    for root_from_dir, root_to_dir in storage_from__storage_to__folders:
      print(f'Synchronising: {root_from_dir} -> {root_to_dir}')
      all_from_files, all_from_directories = storage_from.get_filenames_and_directories_and_cache(root=root_from_dir)
      all_to_files  , all_to_directories   =   storage_to.get_filenames_and_directories_and_cache(root=root_from_dir)

      print('all_from_files', all_from_files)
      print('all_to_files  ', all_to_files)

      def del_file_in_storage_1(f1, storage_1, storage_2, current_directory_1, current_directory_2):
        _filename = os.path.join(current_directory_1, f1)
        storage_1.delete_file(storage_filename)
        print('removed file ' + _filename)
        
      def del_directory_storage_1(d1, storage_1, storage_2, current_directory_1, current_directory_2):
        _dirname = os.path.join(current_directory_1, d1)
        storage_1.delete_directory(storage_filename)
        print('removed directory ' + _dirname)

      # removing the files in github repo that are no longer on SFTP server
      files_directories_recursive(files_1=all_to_files  , directories_1=  all_to_directories, storage_1=storage_to, 
                                  files_2=all_from_files, directories_2=all_from_directories, storage_2=None, 
                                  current_directory_1=root_to_dir, current_directory_2=root_from_dir, check_files_are_the_same=None,
                                  func_file_not_found=del_file_in_storage_1, func_files_different=None, func_directory_not_found=del_directory_storage_1)

      def create_file_in_storage_2(f1, storage_1, storage_2, current_directory_1, current_directory_2):

      def update_file_in_storage_2(full_path_1, full_path_2, storage_1, storage_2):

          
      # for all files on SFTP server ...
      for filename in all_sftp_files:
        storage_filename = storage_dir+'/'+filename
        sftp_filename = sftp_dir + "/" + filename
        # ... either create a new, if it's not on github ...
        if filename not in all_storage_files:
          with sftp_client.open(sftp_filename) as sftp_file:
            print(sftp_filename)
            storage.create_file(storage_filename, content=sftp_file.read())
          print('created ' + storage_filename)
        # ... or update an existing file ...
        elif storage.compare_stats_not_content():
          if storage.get_stats(storage_filename) != sftp_client.stats(sftp_filename):
            with sftp_client.open(sftp_filename) as sftp_file:
              storage.update_file(storage_filename, content=sftp_file.read())       
              print('updated ' + storage_filename)
        else:
          with sftp_client.open(sftp_filename) as sftp_file:
            sftp_contents = sftp_file.read() 
            if storage.get_contents(storage_filename) != sftp_contents: # ... but only if the new file is diffenent
              storage.update_file(storage_filename, content=sftp_contents)
              print('updated ' + storage_filename)
              
      storage.clean_cache()  

from storage_actions import backup_a_Medium_website
from StorageLocal import StorageLocal
from StoragePCloud import StoragePCloud
from StorageGitHub import StorageGitHub
from StorageBase import StorageBase

kwargs = dict(url_or_urls='https://medium.com/@real.zyxxy/about', 
             StorageType=StoragePCloud, 
             path='medium' 
             , kwargs_storage={'secret_name': "default_pcloud_secret"}
             ) #  medium_github_secret

backup_a_Medium_website(**kwargs, do_same_root_urls=False, check_other_urls=False)

if True:
  backup_a_Medium_website(**kwargs, check_other_urls=False)
  backup_a_Medium_website(**kwargs, do_same_root_urls=False)
  backup_a_Medium_website(**kwargs)
  

#print(', \n'.join(["'https://medium.com/" + u + "'" for u in urls if not u.startswith('https://')]))


['_LoggerObj__log_print', '_LoggerObj__logger', '_LoggerObj__logger_extra', '_StorageBase__cached_directories_flat', '_StorageBase__cached_filenames_flat', '_StorageBase__constructor_kwargs', '_StorageBase__please_override', '_StorageBase__txt_chrs', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__enter__', '__eq__', '__exit__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_check_directory_exists_or_create', '_check_storage_or_type', '_close', '_create_directory', '_create_file_given_content', '_create_file_in_another_source', '_delete', '_delete_directory', '_delete_file', '_df_to_str', '_fetch_file_size_efficiently', '_file_contents_is_text', '_filter_out_files', '_find_secret_components', '_get_default_root_dir_info', '_get_filenames_and_directories', '_list', '_list_a_file', '_list_files_directories_recursive', '_open', '_rename_directory', '_rename_file', '_update_file_given_content', 'check_directory_exists', 'check_file_exists', 'check_if_constructor_kwargs_are_the_same', 'check_path_exist_is_dir_not_file', 'columns_df', 'columns_files_df', 'create_directory', 'create_directory_in_existing_directory', 'create_file', 'create_file_given_content', 'default_logger_extra', 'delete', 'delete_directory', 'delete_file', 'file_contents_is_text', 'get_contents', 'get_dir_info', 'get_errors_count', 'get_file_info', 'get_file_size_or_contents', 'get_filenames_and_directories', 'get_init_path', 'has_logger', 'index_listing_df', 'inexistent_directories_are_empty', 'is_my_logger_same_as', 'list', 'log_critical', 'log_enter_level', 'log_error', 'log_exit_level', 'log_info', 'log_mention_directory', 'log_title', 'log_warning', 'print_files_df', 'rename_directory', 'rename_file', 'set_dir_info', 'set_file_info', 'split_path_into_dirs_filename', 'status_names', 'str', 'sync_loggers']

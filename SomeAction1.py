from SomeAction import SomeAction

#################################################################################
class SomeAction1(SomeAction):

  def __init__(self, title, StorageType, kwargs_storage, path):
    self.storage = StorageType(**kwargs_storage)
    super().__init__(title=title + ' ' + self.storage.str(path))

  ###############################################################################
  def __enter__(self):
    self.storage._open()
    self.storage._logger = self
    return self

  ###############################################################################
  def __exit__(self, type, value, traceback):
    super().__exit__(type, value, traceback)
    self.storage._close()

###############################################################################
def list(StorageType, path, enforce_size_fetching=True, kwargs_storage={}):
  with SomeAction1(title='Listing', StorageType=StorageType, kwargs_storage=kwargs_storage, path=path) as sa:
    path_exist_is_dir_not_file = sa.storage.check_path_exist_is_dir_not_file(path)
    if path_exist_is_dir_not_file is True:
      sa._list_files_directories_recursive(storage=sa.storage, dir_to_list=path, enforce_size_fetching=enforce_size_fetching)
    if path_exist_is_dir_not_file is False:
      sa._list_a_file(storage=sa.storage, file_path=path, enforce_size_fetching=enforce_size_fetching)  
    elif path_exist_is_dir_not_file == "both":
      sa.log_error(f"{sa.storage.str(path)} is both a file and a directory")
    else:
      sa.log_error(f"{sa.storage.str(path)} does not exist")  

###############################################################################
def delete(StorageType, path, kwargs_storage={}):
  with SomeAction1(title='Deleting', StorageType=StorageType, kwargs_storage=kwargs_storage, path=path) as sa:
    path_exist_is_dir_not_file = sa.storage.check_path_exist_is_dir_not_file(path)
    if path_exist_is_dir_not_file is True:
      sa.storage.delete_directory(path)
    elif path_exist_is_dir_not_file is False:
      sa.storage.delete_file(path)
    elif path_exist_is_dir_not_file == "both":
      sa.log_error(f"{sa.storage.str(path)} is both a file and a directory")
    else:
      sa.log_error(f"{sa.storage.str(path)} does not exist")

###############################################################################
def create_directory(StorageType, dir_name, kwargs_storage={}):
  with SomeAction1(title='Creating', StorageType=StorageType, kwargs_storage=kwargs_storage, path=dir_name) as sa:
    path_exist_is_dir_not_file = sa.storage.check_path_exist_is_dir_not_file(dir_name)
    if path_exist_is_dir_not_file is not None:
      sa.log_warning(message=f"Skipping because {sa.storage.str(dir_name)} exists")
    else:
      sa.storage.create_directory(dir_name)

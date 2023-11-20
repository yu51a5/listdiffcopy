from ObjectWithLogger2 import ObjectWithLogger
from Logger import Logger

#################################################################################
class Action1(ObjectWithLogger):

  def __init__(self, title, StorageType, kwargs_storage, storage, path, func, **func_kwargs):
    
    errors = Logger._check_storage_or_type(storage=storage, StorageType=StorageType, kwargs=kwargs_storage)

    assert not errors, '.\n'.join(['ERRORS:'] + errors)

    def inner_func(a1, path, func, storage_):
      super().__init__(title=title + ' ' + a1.storage.str(path), objects_to_sync_logger_with=[storage_])
      func(sa=a1, path=path, **func_kwargs)

    if StorageType:
      with StorageType(**kwargs_storage) as self.storage:
        inner_func(a1=self, path=path, func=func, storage_=self.storage)
    else:
      self.storage = storage
      inner_func(a1=self, path=path, func=func, storage_=self.storage)

###############################################################################
def list(path, storage=None, StorageType=None, kwargs_storage={}, enforce_size_fetching=True):

  def func(sa, path, enforce_size_fetching):
    path_exist_is_dir_not_file = sa.storage.check_path_exist_is_dir_not_file(path)
    if path_exist_is_dir_not_file is True:
      sa._list_files_directories_recursive(storage=sa.storage, dir_to_list=path, enforce_size_fetching=enforce_size_fetching)
    elif path_exist_is_dir_not_file is False:
      sa._list_a_file(storage=sa.storage, file_path=path, enforce_size_fetching=enforce_size_fetching)  
    elif path_exist_is_dir_not_file == "both":
      sa.log_error(f"{sa.storage.str(path)} is both a file and a directory")
    else:
      sa.log_error(f"{sa.storage.str(path)} does not exist")  

  Action1(title='Listing', StorageType=StorageType, kwargs_storage=kwargs_storage, storage=storage, path=path,
              func=func, enforce_size_fetching=enforce_size_fetching)

###############################################################################
def delete(path, storage=None, StorageType=None, kwargs_storage={}):
  def func_(sa, path):
    path_exist_is_dir_not_file = sa.storage.check_path_exist_is_dir_not_file(path)
    if path_exist_is_dir_not_file is True:
      sa.storage.delete_directory(path)
    elif path_exist_is_dir_not_file is False:
      sa.storage.delete_file(path)
    elif path_exist_is_dir_not_file == "both":
      sa.log_error(f"{sa.storage.str(path)} is both a file and a directory")
    else:
      sa.log_error(f"{sa.storage.str(path)} does not exist")
  Action1(title='Deleting', StorageType=StorageType, kwargs_storage=kwargs_storage, storage=storage, path=path, func=func)

###############################################################################
def create_directory(dir_name, storage=None, StorageType=None, kwargs_storage={}):
  def func_(sa, path):
    path_exist_is_dir_not_file = sa.storage.check_path_exist_is_dir_not_file(dir_name)
    if path_exist_is_dir_not_file is not None:
      sa.log_warning(message=f"Skipping because {sa.storage.str(dir_name)} exists")
    else:
      sa.storage.create_directory(dir_name)
  Action1(title='Creating', StorageType=StorageType, kwargs_storage=kwargs_storage, storage=storage, path=dir_name, func=func)

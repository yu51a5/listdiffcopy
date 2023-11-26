import math

from utils import partial_with_moving_back
from StorageWebMedium import StorageWebMedium
from StorageAction2 import Compare, Synchronize, Copy
from StorageBase import StorageBase
from LoggerObj import LoggerObj, FDStatus

#################################################################################
def one_storage_func(*args, StorageType=None, kwargs_storage={}, logger=None, return_if_error=None, attr_name=None, **kwargs):
  if logger is None:
    logger = LoggerObj() 
  
  errors = StorageBase._check_storage_or_type(storage=None, StorageType=StorageType, kwargs=kwargs_storage)
  if errors:
    logger.log_critical(errors)
    return return_if_error

  with StorageType(objects_to_sync_logger_with=[logger], **kwargs_storage) as storage_:
    return getattr(storage_, attr_name)(*args, **kwargs)

#################################################################################
def func_for_args_of_one_storage_func_to_move_back(a):
  if isinstance(a, type) and issubclass(a, StorageBase):
    return True
  return isinstance(a, (dict, LoggerObj))
  
#################################################################################
def alt_partial_one_storage_func(*args, **keywords):
  result = partial_with_moving_back(one_storage_func, func_for_args_of_one_storage_func_to_move_back, 
                                    ('StorageType', 'kwargs_storage', 'logger'), *args, **keywords) 
  return result

#################################################################################
#################################################################################
for name_return_if_error in ("get_content", ("get_size", math.nan), "list", "delete", 
                             "rename", "create_directory", "check_path_exist_is_dir_not_file", 
                             ("create_file_given_content", FDStatus.Error),
                             ("get_filenames_and_directories", (None, None))):
  if isinstance(name_return_if_error, str):
    name, return_if_error = name_return_if_error, None
  else:
    name, return_if_error = name_return_if_error[0], name_return_if_error[1]
  globals()[name] = alt_partial_one_storage_func(return_if_error=return_if_error, attr_name=name)

#################################################################################
# inspirations: https://gist.github.com/bgoonz/217ba804d2b3aabe8415c9c99d8f9224
# and           https://github.com/gunar/medium-parser/blob/master/src/processElement.js
#################################################################################
def backup_a_Medium_website(url_or_urls, path, storage=None, StorageType=None, kwargs_storage={}, do_same_root_urls=True, check_other_urls=True):

  swm = StorageWebMedium()

  external_urls = swm.url_or_urls_to_fake_directory(url_or_urls=url_or_urls, path=path, do_same_root_urls=do_same_root_urls, check_other_urls=check_other_urls)

  swm.list(path, enforce_size_fetching=False)
  if storage:
    storage.list(path, enforce_size_fetching=True)
  else:
    list(path, enforce_size_fetching=True, StorageType=StorageType, kwargs_storage=kwargs_storage)

  if check_other_urls:
    swm.log_title(f"Checking {len(external_urls)} URLs")
    swm.check_urls(external_urls, print_ok=True)

  s = synchronize(path_from=path, path_to=path, storage_from=swm, StorageToType=StorageType, kwargs_to=kwargs_storage)

  s.storage_to.list(path, enforce_size_fetching=True)
  if storage:
    storage._close()
    
  swm._close()

#################################################################################
def compare(*args, **kwargs):
  c = Compare(*args, **kwargs)
  return c

#################################################################################
def synchronize(*args, **kwargs):
  s = Synchronize(*args, **kwargs)
  return s

#################################################################################
def copy(*args, **kwargs):
  Copy(*args, **kwargs)

def copy_and_rename(*args, **kwargs):
  Copy(*args, **kwargs)

def move(*args, **kwargs):
  Copy(*args, **kwargs)

def move_and_rename(*args, **kwargs):
  Copy(*args, **kwargs)

#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.

def copy_file(*args, **kwargs):
  Copy(*args, **kwargs)

def copy_file_and_rename(*args, **kwargs):
  Copy(*args, **kwargs)

def move_file(*args, **kwargs):
  Copy(*args, **kwargs)

def move_file_and_rename(*args, **kwargs):
  Copy(*args, **kwargs)

#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.

def copy_directory(*args, **kwargs):
  with Copy(*args, **kwargs) as _:
    pass

def copy_directory_and_rename(*args, **kwargs):
  Copy(*args, **kwargs)

def move_directory(*args, **kwargs):
  Copy(*args, **kwargs)

def move_directory_and_rename(*args, **kwargs):
  Copy(*args, **kwargs)

 
from StorageWebMedium import StorageWebMedium
from StorageAction2 import synchronize
from StorageBase import StorageBase
from LoggerObj import LoggerObj

#################################################################################
def list(path, enforce_size_fetching=False, storage=None, StorageType=None, kwargs_storage={}):

  logger = LoggerObj()
  errors = StorageBase._check_storage_or_type(storage=storage, StorageType=StorageType, kwargs=kwargs_storage)
  if errors:
    logger.log_critical(errors)
    return
    
  if storage:
    storage.list(path=path, enforce_size_fetching=enforce_size_fetching)
  else:
    with StorageType(**kwargs_storage) as storage_:
      storage_.list(path=path, enforce_size_fetching=enforce_size_fetching)

#################################################################################
def delete(path, storage=None, StorageType=None, kwargs_storage={}):

  logger = LoggerObj()
  errors = StorageBase._check_storage_or_type(storage=storage, StorageType=StorageType, kwargs=kwargs_storage)
  if errors:
    logger.log_critical(errors)
    return

  if storage:
    storage.delete(path=path)
  else:
    with StorageType(**kwargs_storage) as storage_:
      storage_.delete(path=path)
      
#################################################################################
def rename(existing_path, new_path, storage=None, StorageType=None, kwargs_storage={}):
  pass

#################################################################################
# inspirations: https://gist.github.com/bgoonz/217ba804d2b3aabe8415c9c99d8f9224
# and           https://github.com/gunar/medium-parser/blob/master/src/processElement.js
#################################################################################
def backup_a_Medium_website(url_or_urls, path, storage=None, StorageType=None, kwargs_storage={}, do_same_root_urls=True, check_other_urls=True):

  swm = StorageWebMedium()
  only_one_url = isinstance(url_or_urls, str)

  swm.log_title(f"Analysing {1 if only_one_url else len(url_or_urls)} URL {'' if only_one_url else 's'} {'and other linked URLs' if do_same_root_urls else '' }")
  external_urls = swm.url_or_urls_to_fake_directory(url_or_urls=url_or_urls, path=path, do_same_root_urls=do_same_root_urls, check_other_urls=check_other_urls)

  swm.list(path, enforce_size_fetching=False)
  if storage:
    storage.list(path, enforce_size_fetching=True)
  else:
    list(path, enforce_size_fetching=True, StorageType=StorageType, kwargs_storage=kwargs_storage)

  if check_other_urls:
    swm.log_title(f"Checking {len(external_urls)} URLs")
    swm.check_urls(external_urls, print_ok=True)

  _, storage_to = synchronize(path_from=path, path_to=path, storage_from=swm, StorageToType=StorageType, kwargs_to=kwargs_storage)

  storage_to.list(path, enforce_size_fetching=True)
  if storage:
    storage._close()
    
  swm._close()

 
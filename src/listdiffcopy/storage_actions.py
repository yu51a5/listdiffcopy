from listdiffcopy.utils import partial_with_moving_back
from listdiffcopy.StorageWebMedium import StorageWebMedium
from listdiffcopy.StorageWeb import StorageWeb
from listdiffcopy.StorageAction2 import Compare, Synchronize, Copy, Move, CopyInto, MoveInto
from listdiffcopy.StorageBase import StorageBase
from listdiffcopy.LoggerObj import LoggerObj

#################################################################################
def one_storage_func(*args, return_if_error=None, attr_name=None, **kwargs):

  args_inputs = ((LoggerObj, 'logger'),
                 (StorageBase, 'storage'),
                 (None, 'StorageType'),
                 (dict, 'kwargs_storage'))

  constr_args = {an : kwargs[an] for type_, an in args_inputs if an in kwargs and kwargs[an] is not None}
  args2 = [a for a in args]

  if 'kwargs_storage' not in constr_args:
    constr_args['kwargs_storage'] = {}

  for type_, an in args_inputs:
    if an in constr_args:
      continue
    if type_ is None:
      _args = [a for a in args if isinstance(a, type) and issubclass(a, StorageBase)]
    else:
      _args = [a for a in args if isinstance(a, type_)]

    logger = constr_args['logger'] if 'logger' in constr_args else LoggerObj()

    if len(_args) > 1:
      logger.log_critical(f"{an} argument ambiguity: there are {len(_args)} unnamed arguments of type {type_} in the function call")
    elif len(_args) == 1:
      if (type_ is not dict) or ('StorageType' in constr_args):
        constr_args[an] = _args[0]
        args2 = [a for a in args2 if a != _args[0]] 
  
  errors = StorageBase._check_storage_or_type(storage=constr_args['storage'] if 'storage' in constr_args else None, 
                                              StorageType=constr_args['StorageType'] if 'StorageType' in constr_args else None, 
                                              kwargs=constr_args['kwargs_storage'] if 'kwargs_storage' in constr_args else {})
  if errors:
    logger.log_critical(errors)
    return return_if_error

  if 'storage' in constr_args:
    return getattr(constr_args['storage'], attr_name)(*args2, **kwargs)
    
  with constr_args['StorageType'](objects_to_sync_logger_with=[logger], 
                                  **constr_args['kwargs_storage'     ]) as storage_:
    return getattr(storage_, attr_name)(*args2, **kwargs)

#################################################################################
def func_for_args_of_one_storage_func_to_move_back(a):
  if isinstance(a, type) and issubclass(a, StorageBase):
    return True
  return isinstance(a, (dict, LoggerObj))
  
#################################################################################
def alt_partial_one_storage_func(*args, **keywords):
  result = partial_with_moving_back(one_storage_func, func_for_args_of_one_storage_func_to_move_back, 
                                    ('storage', 'StorageType', 'kwargs_storage', 'logger'), *args, **keywords) 
  return result

#################################################################################
#################################################################################
def __add_one_storage_action(name, return_if_error):
  globals()[name] = alt_partial_one_storage_func(return_if_error=return_if_error, attr_name=name)
  globals()[name+'_'] = alt_partial_one_storage_func(return_if_error=return_if_error, attr_name=name+'_')

StorageBase.loop_over_action_list(__add_one_storage_action)  

#################################################################################
def check_urls(url_or_urls, print_ok=True):

  backup_a_Medium_website(url_or_urls=url_or_urls, path='whatever', storage=None, StorageType=None, kwargs_storage={}, do_same_root_urls=False, check_other_urls=True, save_texts=False, save_assets=False, print_ok=print_ok)
  
#################################################################################
# inspirations: https://gist.github.com/bgoonz/217ba804d2b3aabe8415c9c99d8f9224
# and           https://github.com/gunar/medium-parser/blob/master/src/processElement.js
#################################################################################
def backup_a_Medium_website(url_or_urls, path, storage=None, StorageType=None, kwargs_storage={}, do_same_root_urls=True, check_other_urls=True, save_texts=True, save_assets=True, print_ok=True):

   with StorageWebMedium() as swm:

    external_urls = swm.url_or_urls_to_fake_directory(url_or_urls=url_or_urls, path=path, do_same_root_urls=do_same_root_urls, check_other_urls=check_other_urls, save_texts=save_texts, save_assets=save_assets)
  
    if False:
      swm.list(path, enforce_size_fetching=False)
      if storage:
        storage.list(path, enforce_size_fetching=True)
      else:
        list(path, enforce_size_fetching=True, StorageType=StorageType, kwargs_storage=kwargs_storage)
  
    if check_other_urls:
      swm.log_title(f"Checking {len(external_urls)} URLs")
      with StorageWeb() as sw:
        sw.check_urls(external_urls, print_ok=print_ok)
  
    s = copy(path_from=path, path_to=path, storage_from=swm, StorageToType=StorageType, kwargs_to=kwargs_storage)

    if False:
      list(path, StorageType, enforce_size_fetching=True)

#################################################################################
def generate_medium_toc(url):
  with StorageWebMedium() as swm:
    return swm.generate_toc(url=url)

#################################################################################
def compare(*args, **kwargs):
  c = Compare(*args, **kwargs)
  return c

#################################################################################
def synchronize(*args, **kwargs):
  result = Synchronize(*args, **kwargs)
  return result

#################################################################################
def copy(*args, **kwargs):
  result = Copy(*args, **kwargs)
  return result

def copy_into(*args, **kwargs):
  result = CopyInto(*args, **kwargs)
  return result
  
def move(*args, **kwargs):
  result = Move(*args, **kwargs)
  return result

def rename(*args, **kwargs):
  result = Move(*args, **kwargs)
  return result

def move_into(*args, **kwargs):
  result = MoveInto(*args, **kwargs)
  return result
 
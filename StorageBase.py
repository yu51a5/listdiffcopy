import os
import math
import pandas as pd
import numpy as np
from functools import partialmethod

from settings import ENFORCE_SIZE_FETCHING_WHEN_LISTING
from utils import is_equal_str_bytes
from LoggerObj import LoggerObj, FDStatus

#################################################################################
class StorageBase(LoggerObj):

  __txt_chrs = set([chr(i) for i in range(32, 127)] + list("\n\r\t\b"))

  ###############################################################################
  def loop_over_action_list(cllable):
    for name_return_if_error in  ("read_file", "write_file", "create_directory", 
                                   "list", "delete", "rename", 
                                   ("check_path_exist_is_dir_not_file", None),
                                   ("get_size", math.nan), 
                                   ("get_filenames_and_directories", (None, None))):
      if isinstance(name_return_if_error, str):
        name, return_if_error = name_return_if_error, FDStatus.Error
      else:
        name, return_if_error = name_return_if_error[0], name_return_if_error[1]
      cllable(name=name, return_if_error=return_if_error)

  ###############################################################################
  def _check_storage_or_type(storage, StorageType, kwargs, both_nones_ok=False):
    errors = []
    if storage and StorageType:
      errors.append(f"storage_from {storage} and StorageType {StorageType} mustn't be both defined")
    if not (storage or StorageType or both_nones_ok):
      errors.append(f"storage_from {storage} and StorageType {StorageType} mustn't be both undefined")
    if StorageType is None:
      if kwargs:
        errors.append(f"StorageType is not provided, but arguments {kwargs} are")
    elif not issubclass(StorageType, StorageBase):
      errors.append(f"StorageType {StorageType} is not a subclass of StorageBase")
    return errors

  #################################################################################
  def __init__(self, constructor_kwargs, logger_name=None, objects_to_sync_logger_with=[], connection_var_name=None):
    self.__constructor_kwargs = {k : v for k, v in constructor_kwargs.items()}
    super().__init__(logger_name=logger_name, objects_to_sync_logger_with=objects_to_sync_logger_with)
    self.__connection_var_name = connection_var_name
    self._connection_var_action(setattr, None)

  ###############################################################################
  def _connection_var_action(self, func, *args, reverse=False, **kwargs):
    if self.__connection_var_name:
      if isinstance(self.__connection_var_name, str):
        func(self, self.__connection_var_name, *args, **kwargs)
      else:
        for cvn in self.__connection_var_name[::(-1 if reverse else 1)]:
          func(self, cvn, *args, **kwargs)

  ###############################################################################
  def _get_connection_var(self):
    if self.__connection_var_name:
      cvn = self.__connection_var_name if isinstance(self.__connection_var_name, str) else self.__connection_var_name[-1]
      if hasattr(self, cvn):
        a = getattr(self, cvn)
        if a:
          return a
    cname = str(type(self).__name__)
    self.log_critical(f"{cname} connection not open, use `with {cname}(<>) as s` instead of `s = {cname}(<>)` ")

  ###############################################################################
  def check_if_constructor_kwargs_are_the_same(self, the_other_constructor_kwargs):
    return the_other_constructor_kwargs == self.__constructor_kwargs
    
  #################################################################################
  def _find_secret_components(self, how_many, secret_name=None):
    try:
      if secret_name is None:
        secret_name = 'default_' + type(self).__name__[len('Storage'):].lower() + '_secret'
      secret = os.getenv(secret_name)
      secret_components = secret.split('|') if secret else []
      if isinstance(how_many, int):
        assert len(secret_components) == how_many, f"There should be {how_many} {type(self).__name__} secret components in environment variable {secret_name}, but {len(secret_components)} are provided"
      else:
        assert len(secret_components) in how_many, f"There should be {' or '.join([str(h) for h in how_many])} {type(self).__name__} secret components in environment variable {secret_name}, but {len(secret_components)} are provided"
      return secret_components
    except Exception as e:
      self.log_error(f"Failed to find secret components for {type(self).__name__}, {e}")

  #################################################################################
  def path_to_str(self, path):
    return path
  
  def str(self, path):
    result = f'{type(self).__name__}(`{self.path_to_str(path)}`)'
    return result

  #################################################################################
  # source: stackoverflow.com/questions/1446549
  # 2048 bytes because of https://pypi.org/project/python-magic/
  def _file_contents_is_text(file_beginning):
    if not file_beginning:
      return None
    if isinstance(file_beginning, bytes):
      try:
        file_beginning_str = file_beginning.decode()
      except (UnicodeDecodeError, AttributeError):
        return False
    elif isinstance(file_beginning, str):
      file_beginning_str = file_beginning
    else:
      raise Exception(f'Cannot process {type(file_beginning)}')

    #s=open(filename).read(2048)
    if not file_beginning_str:
      # Empty files are considered text
      return True
    if "\0" in file_beginning_str:
      # Files with null bytes are likely binary
      return False
    # Get the non-text characters (maps a character to itself then
    # use the 'remove' option to get rid of the text characters.)
    
    booleans = [(i in StorageBase.__txt_chrs) for i in file_beginning_str]
    # If more than 30% non-text characters, then
    # this is considered a binary file
    return (sum(booleans)/len(file_beginning_str) >= .7)

  ###############################################################################
  def __enter__(self):
    self._open()
    return self

  ###############################################################################
  def __exit__(self, type, value, traceback):
    self._close()

  ###############################################################################
  def _open(self):
    pass

  ###############################################################################
  def _close(self):
    def _fc(self, vn):
      a = getattr(self, vn, None)
      a.close()
      a = None
    self._connection_var_action(_fc, reverse=True)

  ###############################################################################
  def __please_override(self):
     raise Exception("needs to be overriden", type(self))
      
  ###############################################################################
  def _get_filenames_and_directories(self, path: str):
    self.__please_override()
  
  ###############################################################################
  def _delete_file(self, path):
    self.__please_override()
    
  ###############################################################################
  def _delete_directory(self, path):
    self.__please_override()

  ###############################################################################
  def _create_directory_only(self, path):
    self.__please_override()

  ###############################################################################
  def _create_file_given_content(self, path, content):
    self.__please_override()

  ###############################################################################
  # default implementation
  def _update_file_given_content(self, path, content):
    self._create_file_given_content(path=path, content=content)
    
  ###############################################################################
  def _rename_file(self, path_to_existing_file, path_to_new_file):
    self.__please_override()
    
  ###############################################################################
  def _rename_directory(self, path_to_existing_dir, path_to_new_dir):
    self.__please_override()
    
  ###############################################################################
  def _read_file(self, path, length=None):
    self.__please_override()

  ###############################################################################
  def inexistent_directories_are_empty(self):
    return False
    
  ###############################################################################
  def get_init_path(self):
    return ''    

  ###############################################################################
  def split_path_into_dirs_filename(self, path):
    result = []
    while path:
      path, tail = os.path.split(path)
      result = [tail] + result   
    if (len(result) > 1) and (not result[-1]):
      result.pop(-1)
    if (len(result) > 1) and (result[0] == self.get_init_path()):
      result.pop(0)
    return result
    
  ###############################################################################
  def _create_directory(self, path, create_if_doesnt_exist=True):
    root_folders = self.split_path_into_dirs_filename(path=path)
    path_so_far = self.get_init_path() 
    was_created = False
    for rf in root_folders:
      _, directories_ = self.get_filenames_and_directories_(path=path_so_far)
      path_so_far = os.path.join(path_so_far, rf)
      if path_so_far in directories_:
        continue 
      if create_if_doesnt_exist:
        self._create_directory_only(path_so_far)
        was_created = True
        continue
      return False
    if create_if_doesnt_exist and (not was_created):
      pass # self.log_warning(message=f"Skipping because {self.str(path)} exists")
    return (not create_if_doesnt_exist) or was_created

  ###############################################################################
  def check_directory_exists(self, path):
    result = self._create_directory(path, create_if_doesnt_exist=False)
    return result
  
  ###############################################################################
  def check_file_exists(self, path):  
    dirname, _ = os.path.split(path)
    dir_exists = self.check_directory_exists(path=dirname)
    if dir_exists:
      files_, _ = self.get_filenames_and_directories_(path=dirname)
      return (path in files_)
    return False

  ###############################################################################
  def _check_path_exist_is_dir_not_file(self, path):
    is_file = self.check_file_exists(path)
    is_dir = self.check_directory_exists(path)
    if is_file: 
      return "both" if is_dir else False
    elif is_dir:
      return True
    else:
      return None

  ###############################################################################
  def _rename(self, existing_path, new_path):
    new_path_exists = self._check_path_exist_is_dir_not_file(new_path)
    if new_path_exists is not None:
      self.log_error(f"{self.str(new_path)} already exists")
      return
    
    path_exist_is_dir_not_file = self._check_path_exist_is_dir_not_file(existing_path)
    if path_exist_is_dir_not_file is True:
      return self._rename_directory(path_to_existing_dir=existing_path, 
                                    path_to_new_dir=new_path)
    elif path_exist_is_dir_not_file is False:
      return self._rename_file(path_to_existing_file=existing_path, 
                               path_to_new_file=new_path)
    elif path_exist_is_dir_not_file == "both":
      self.log_error(f"{self.str(existing_path)} is both a file and a directory")
    else:
      self.log_error(f"{self.str(existing_path)} does not exist")  
      
  ###############################################################################
  def _filter_out_files(self, files_):
    return files_
  
  ###############################################################################
  def get_filenames_and_directories(self, path):
      if not path:
        path = self.get_init_path()
      files_, directories_ = self.get_filenames_and_directories_(path=path)
      
      files_.sort(key=lambda x: x.lower())
      directories_.sort(key=lambda x: x.lower())
  
      files_ = self._filter_out_files(files_)
  
      return files_, directories_
      
  ###############################################################################
  def file_contents_is_text(self, path):
    file_beginning = self._read_file(path=path, length=2048)
    result = StorageBase._file_contents_is_text(file_beginning=file_beginning)
    return result

  ###############################################################################
  def _get_file_size_or_content(self, path):
    ffse = getattr(self, '_fetch_file_size_efficiently', None)
    if ffse is not None:
      my_contents = None
      my_file_size = self._fetch_file_size_efficiently(path)
    else:
      my_contents = self._read_file(path)
      my_file_size = len(my_contents)

    return my_file_size, my_contents

  ###############################################################################
  def _write_file(self, path, content, check_if_contents_is_the_same_before_writing=True):
      assert isinstance(content, (str, bytes)), f'Type of contents is {type(content)}'
      assert path, "Filename is not defined"
      path_exist_is_dir_not_file_to = self._check_path_exist_is_dir_not_file(path)
      if path_exist_is_dir_not_file_to is False: # it's a file
        if check_if_contents_is_the_same_before_writing:
          current_contents = self._read_file(path)
          if is_equal_str_bytes(content, current_contents):
            return FDStatus.Identical
        self._update_file_given_content(path=path, content=content)
        return FDStatus.Different_or_Updated
      elif path_exist_is_dir_not_file_to is None: # it does not exist
        self._create_directory(path=os.path.dirname(path))
        self._create_file_given_content(path=path, content=content)
        return FDStatus.LeftOnly_or_New
      else: # it's a folder or both
        self.log_error(f'{self.str(path)} exists, and it is a directory')
        return FDStatus.Error
  
  ###############################################################################
  def _get_file_size(self, path):
      ffse = getattr(self, '_fetch_file_size_efficiently', None)
      result = ffse(path=path) if ffse else len(self._read_file(path=path))
      return result

  ###############################################################################
  def _get_size(self, path):
    path_exist_is_dir_not_file = self._check_path_exist_is_dir_not_file(path)
    if path_exist_is_dir_not_file is True:
      files_, directories_ = self._get_filenames_and_directories(path=path)
      result = sum([self._get_file_size(f) for f in files_]) \
             + sum([self.get_size_(path=d) for d in directories_])
      return result
    elif path_exist_is_dir_not_file is False:
      return self._get_file_size(path=path)  
    elif path_exist_is_dir_not_file == "both":
      self.log_error(f"{self.str(path)} is both a file and a directory")
    else:
      self.log_error(f"{self.str(path)} does not exist")  
  
  ###############################################################################
  def _list_files_directories_recursive(self, path, enforce_size_fetching, message2=''):

    self.log_enter_level(dirname=path, message_to_print='Listing', message2=message2)

    files_, dirs_ = self.get_filenames_and_directories_(path)

    if enforce_size_fetching:
      df = [[os.path.basename(f), self._get_file_size(f)] for f in files_]
    else:
      df = [[os.path.basename(f)                         ] for f in files_]
    self.print_files_df(data =df)

    total_size_first_level = sum([dfr[1] for dfr in df]) if enforce_size_fetching else math.nan
    totals = np.array([total_size_first_level, len(files_), len(dirs_)])

    dirs_dict = {}  
    for dir_ in dirs_:
      dir_totals, dir_files, dir_dirs_dict = self._list_files_directories_recursive(path=dir_, enforce_size_fetching=enforce_size_fetching)
      totals += dir_totals
      dirs_dict[dir_] = (dir_files, dir_dirs_dict)

    table_stats = [[total_size_first_level, len(files_), len(dirs_)], 
                   totals.tolist()]

    kwargs = {}
    if enforce_size_fetching or dirs_:
      kwargs['dir_details_df'] = pd.DataFrame(table_stats, index=self.index_listing_df, columns=self.columns_df)
    self.log_exit_level(**kwargs)

    return totals, files_, dirs_dict

  ###############################################################################
  def _list(self, path, enforce_size_fetching=ENFORCE_SIZE_FETCHING_WHEN_LISTING):
    path_exist_is_dir_not_file = self._check_path_exist_is_dir_not_file(path)
    if path_exist_is_dir_not_file is True:
      result = self._list_files_directories_recursive(path=path, enforce_size_fetching=enforce_size_fetching)
      return result
    elif path_exist_is_dir_not_file is False:
      size_arr = [self.get_size(path=path)] if enforce_size_fetching else []
      result = self.print_files_df(data = [[os.path.basename(path)] + size_arr])
      return size_arr
    elif path_exist_is_dir_not_file == "both":
      self.log_error(f"{self.str(path)} is both a file and a directory")
    else:
      self.log_error(f"{self.str(path)} does not exist")  

###############################################################################
  def _delete(self, path):
    path_exist_is_dir_not_file = self._check_path_exist_is_dir_not_file(path)
    if path_exist_is_dir_not_file is True:
      self._delete_directory(path)
    elif path_exist_is_dir_not_file is False:
      self._delete_file(path)  
    elif path_exist_is_dir_not_file == "both":
      self.log_error(f"{self.str(path)} is both a file and a directory")
    else:
      self.log_error(f"{self.str(path)} does not exist")  

###############################################################################
###############################################################################
###############################################################################
# # source : https://gist.github.com/mgarod/09aa9c3d8a52a980bd4d738e52e5b97a
# https://stackoverflow.com/questions/533382

def add_StorageBase_method(name, return_if_error, title=None):
  def _inner_add_method(self, *args, add_print_title, **kwargs):
    title_ = title if title else name
    path = None
    if ('path' in kwargs) and ('existing_path' in kwargs):
      raise Exception("path and existing_path arguments are mutually exclusive")
    elif ('path' in kwargs) or ('existing_path' in kwargs):
      path = kwargs['path'] if ('path' in kwargs) else kwargs['existing_path']
    else:
      strs = [arg for arg in args if isinstance(arg, str)]
      if len(strs) == 1:
        path = strs[0]
      else:
        raise Exception(f"No path argument given, and {len(strs)} nameless string arguments given")
    try:
      title_ += " " + self.str(path)
      if add_print_title:
        self.log_title(title=title_)
      return getattr(self, "_"+name)( *args, **kwargs)
    except Exception as e:
      self.log_error(f'{title_} failed, exception {e}')
      return return_if_error

  setattr(StorageBase, name    , partialmethod(_inner_add_method, add_print_title=True))
  setattr(StorageBase, name+"_", partialmethod(_inner_add_method, add_print_title=False))
  
###############################################################################

_ = StorageBase.loop_over_action_list(cllable=add_StorageBase_method)

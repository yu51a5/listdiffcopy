import os
import math
import pandas as pd
import numpy as np
from functools import partialmethod, partial
from collections.abc import Iterable 

from listdiffcopy.settings import DEFAULT_SORT_KEY, ENFORCE_SIZE_FETCHING_WHEN_LISTING, PATH_FOR_RESUMING
from listdiffcopy.utils import is_equal_str_bytes
from listdiffcopy.LoggerObj import FDStatus, LoggerObj

#################################################################################
class StorageBase(LoggerObj):

  __txt_chrs = set([chr(i) for i in range(32, 127)] + list("\n\r\t\b"))
  inexistent_directories_are_empty = False
  _init_path = ''

  ###############################################################################
  def loop_over_action_list(cllable):
    for name_return_if_error in  (("read_file", None), "write_file", "create_directory", 
                                   ("list", (None, None)), "delete", "rename", 
                                   ("check_path_exist_is_dir_not_file", None),
                                   ("get_size", math.nan), 
                                   ("get_filenames_and_dirnames", (None, None))):
      if isinstance(name_return_if_error, str):
        name, return_if_error = name_return_if_error, FDStatus.Error
      else:
        name, return_if_error = name_return_if_error[0], name_return_if_error[1]
      cllable(name=name, return_if_error=return_if_error)

  ###############################################################################
  def _check_storage_or_type(storage, StorageType, kwargs, both_nones_ok=False):
    errors = []
    if storage and StorageType:
      errors.append(f"storage {storage} and StorageType {StorageType} mustn't be both defined")
    if not (storage or StorageType or both_nones_ok):
      errors.append(f"storage {storage} and StorageType {StorageType} mustn't be both undefined")
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
      a = getattr(self, cvn, None)
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
  def _delete_directory_contents(self, path):
    all_files, all_directories = self._get_filenames_and_dirnames(path=path)
    for f in all_files:
      self._delete_file(filename=f)
    for d in all_directories:
      self._delete_directory(path=d)

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
  def split_path_into_dirs_filename(self, path):
    result = []
    while path:
      path, tail = os.path.split(path)
      result = [tail] + result   
      if path is os.sep:
        result = [''] + result 
        break
    if (len(result) > 1) and (not result[-1]):
      result.pop(-1)
    if (len(result) > 1) and (result[0] == self._init_path):
      pass # result.pop(0)
    return result
    
  ###############################################################################
  def _create_directory(self, path, create_if_doesnt_exist=True):
    if path in ('', self._init_path):
      return True
    root_folders = self.split_path_into_dirs_filename(path=path)
    path_so_far = self._init_path
    was_created = False

    for rf in root_folders:
      _, directories_ = self._get_filenames_and_dirnames(path=path_so_far)
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
    if not dirname:
      dirname = self._init_path
    dir_exists = self.check_directory_exists(path=dirname)
    if dir_exists:
      files_, _ = self._get_filenames_and_dirnames(path=dirname)
      filename_to_check = os.path.join(dirname, os.path.basename(path))
      result = filename_to_check in files_
      return result
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
  def _method_with_check_path_exist_is_dir_not_file(self, path, mF, mT=None, mN=None):
    path_exist_is_dir_not_file = self._check_path_exist_is_dir_not_file(path)
    if path_exist_is_dir_not_file is True:
      if mT:
        return mT()
      else:
        self.log_error(f"{self.str(path)} is a directory")
        return FDStatus.Error
    elif path_exist_is_dir_not_file is False:
      return mF()
    elif path_exist_is_dir_not_file == "both":
      self.log_error(f"{self.str(path)} is both a file and a directory")
      return FDStatus.Error
    else:
      if mN:
        return mN()
      else:
        self.log_error(f"{self.str(path)} does not exist")  
        return FDStatus.Error

  ###############################################################################
  def _rename(self, path_from, path_to):
    new_path_exists = self._check_path_exist_is_dir_not_file(path_to)
    if new_path_exists is not None:
      self.log_error(f"{self.str(path_to)} already exists")
      return FDStatus.Error

    return self._method_with_check_path_exist_is_dir_not_file(
                   path=path_from,
                   mT=partial(self._rename_directory, 
                              path_to_existing_dir=path_from, 
                              path_to_new_dir=path_to),
                   mF=partial(self._rename_file, 
                              path_to_existing_file=path_from, 
                              path_to_new_file=path_to)
    )
      
  ###############################################################################
  def _filter_out_files(self, files_):
    return files_
  
  ###############################################################################
  def _get_filenames_and_dirnames(self, path, filenames_filter=[], sort_key=DEFAULT_SORT_KEY, sort_reverse=False, sort_resume=False):
    if (not path) and self._init_path:
      return self._get_filenames_and_dirnames(path=self._init_path, 
                                              filenames_filter=filenames_filter, 
                                              sort_key=sort_key, sort_reverse=sort_reverse, resume=resume)

    files_, dirs_ = self._get_filenames_and_directories(path=path)

    if filenames_filter:
      if isinstance(filenames_filter, Iterable):
        for ff in filenames_filter:
          files_ = ff(files_)
      else:
        files_ = filenames_filter(files_)

    if sort_key:
      files_.sort(key=sort_key, reverse=sort_reverse)
      dirs_.sort(key=sort_key, reverse=sort_reverse)

    if sort_resume:
      resume_path = PATH_FOR_RESUMING if sort_resume is True else resume
      with open(resume_path, "r") as fi:
        resume_from_path = os.path.join(path, fi.read())
      if sort_reverse:
        files_ = [f for f in files_ if sort_key(f) <= sort_key(resume_from_path)]
        dirs_  = [d for d in dirs_  if sort_key(d) <= sort_key(resume_from_path)]
      else:
        files_ = [f for f in files_ if sort_key(f) >= sort_key(resume_from_path)]
        dirs_  = [d for d in dirs_  if sort_key(d) >= sort_key(resume_from_path)]

    return files_, dirs_
      
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

    def mN():
      self._create_directory(path=os.path.dirname(path))
      self._create_file_given_content(path=path, content=content)
      return FDStatus.LeftOnly_or_New

    def mF():
      if check_if_contents_is_the_same_before_writing == 'pass':
        return FDStatus.Identical
      if check_if_contents_is_the_same_before_writing is not None:
        if check_if_contents_is_the_same_before_writing is False: # size only
          current_size, current_content = self._get_file_size_or_content(path)    
        else:
          current_content = self._read_file(path)
          current_size = None
        if current_size == len(content) or is_equal_str_bytes(content, current_content):
          return FDStatus.Identical

      self._update_file_given_content(path=path, content=content)
      return FDStatus.Different_or_Updated

    return self._method_with_check_path_exist_is_dir_not_file(
                                                path=path, mF=mF, mT=None, mN=mN)
  
  ###############################################################################
  def _get_file_size(self, path):
      ffse = getattr(self, '_fetch_file_size_efficiently', None)
      result = ffse(path=path) if ffse else len(self._read_file(path=path))
      return result

  ###############################################################################
  def _get_size(self, path):
    def _sum_up_sizes():
      files_, directories_ = self._get_filenames_and_dirnames(path=path)
      result = sum([self._get_file_size(f) for f in files_]) \
             + sum([self.get_size_(path=d) for d in directories_])
      return result

    return self._method_with_check_path_exist_is_dir_not_file(
                   path=path,
                   mT=_sum_up_sizes,
                   mF=partial(self._get_file_size, path=path)
    )
  
  ###############################################################################
  def _list_files_directories_recursive(self, path, enforce_size_fetching, 
                                        sort_key=DEFAULT_SORT_KEY, sort_reverse=False, resume=False,
                                        message2='', filenames_filter=[]):
    self.log_enter_level(dirname=path, message_to_print='Listing', message2=message2)

    files_, dirs_ = self._get_filenames_and_dirnames(path, filenames_filter=filenames_filter,
                                                     sort_key=sort_key, sort_reverse=sort_reverse, resume=resume)

    if enforce_size_fetching:
      df = [[os.path.basename(f), self._get_file_size(f)] for f in files_]
    else:
      df = [[os.path.basename(f)                        ] for f in files_]
    self.print_files_df(data =df, path=os.path.dirname(f), resume=resume)

    total_size_first_level = sum([dfr[1] for dfr in df]) if enforce_size_fetching else math.nan
    totals = np.array([total_size_first_level, len(files_), len(dirs_)])

    dirs_dict = {}  
    for dir_ in dirs_:
      dir_totals, dir_files, dir_dirs_dict = self._list_files_directories_recursive(path=dir_, 
                                                                                    enforce_size_fetching=enforce_size_fetching,
                                                                                    sort_key=sort_key, sort_reverse=sort_reverse, resume=resume, 
                                                                                    filenames_filter=filenames_filter)
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
  def _list(self, path, 
                  enforce_size_fetching=ENFORCE_SIZE_FETCHING_WHEN_LISTING, 
                  sort_key=DEFAULT_SORT_KEY, sort_reverse=False, resume=False,
                  filenames_filter=[]):
    def mF():
      data =  [[os.path.basename(path)] 
                 + ([self.get_size_(path=path)] if enforce_size_fetching else [])]
      self.print_files_df(data=data, path=os.path.dirname(path), resume=resume)
      return data, [path], {}
      
    return self._method_with_check_path_exist_is_dir_not_file(
                   path=path,
                   mT=partial(self._list_files_directories_recursive,
                              path=path, 
                              enforce_size_fetching=enforce_size_fetching, 
                              sort_key=sort_key, sort_reverse=sort_reverse, resume=resume,                                              
                              filenames_filter=filenames_filter),
                   mF=mF)

###############################################################################
  def _delete(self, path):
    def mN():
      return FDStatus.DidNotExist
    def mT():
      self._delete_directory(path=path)
      return FDStatus.Success
    def mF():
      self._delete_file(path=path)
      return FDStatus.Success
      
    return self._method_with_check_path_exist_is_dir_not_file(
                   path=path, mT=mT, mF=mF, mN=mN)

###############################################################################
###############################################################################
###############################################################################
# # source : https://gist.github.com/mgarod/09aa9c3d8a52a980bd4d738e52e5b97a
# https://stackoverflow.com/questions/533382

def add_StorageBase_method(name, return_if_error, title=None):
  def _inner_add_method(self, *args, add_print_title, **kwargs):
    title_ = title if title else name
    path = None
    if ('path' in kwargs) and ('path_from' in kwargs):
      raise Exception("path and path_from arguments are mutually exclusive")
    elif ('path' in kwargs) or ('path_from' in kwargs):
      path = kwargs['path'] if ('path' in kwargs) else kwargs['path_from']
    else:
      strs = [arg for arg in args if isinstance(arg, str)]
      if 1 <= len(strs) <= 2:
        path = strs[0]
      else:
        raise Exception(f"No path argument is given, and {len(strs)} nameless string arguments are given")
    try:
      should_be_dir_not_file = True if name in ("get_filenames_and_dirnames", "create_directory") \
                                 else (False if name in ("read_file", "write_file") else self._check_path_exist_is_dir_not_file(path))

      if should_be_dir_not_file is None:
        self.log_error(f"{self.str(path)} does not exist")
        return FDStatus.Error
      if should_be_dir_not_file == "both":
        self.log_error(f"{self.str(path)} is both a file and a directory")
        return FDStatus.Error
      title_ += " " + self.str(path)
      if add_print_title:
        if should_be_dir_not_file:
          self.log_title(title=title_)
          if name != "list":
            self.log_enter_level(dirname=path, message_to_print=name)
        else:
          when_started = self.start_file(path=path, 
             message_to_print=name, 
             message2="")
      
      result = getattr(self, "_"+name)( *args, **kwargs)
      
      if add_print_title:
        if should_be_dir_not_file:
          if name != "list":
            self.log_exit_level()
        else:
          this_file_status = result if isinstance(result, FDStatus) else FDStatus.Success
          size = math.nan
          if name == "read_file": 
            size = len(result)
          if name == "get_size":
            size = result
          if name == "write_file":
            if 'content' in kwargs:
              size = len(kwargs['content'])
            else:
              bytes_args = [arg for arg in args if isinstance(arg, bytes)]
              if len(bytes_args) == 1:
                size = len(bytes_args[0])
              else:
                str_args = [arg for arg in args if isinstance(arg, str)]
                if len(str_args) == 2:
                  size = len(bytes_args[-1])
          data = [os.path.basename(path), size, this_file_status]
          self.print_complete_file(data=data, when_started=when_started)
  
      return result
      
    except Exception as e:
      raise e # self.log_error(f'{title_} failed', e)
      return return_if_error
      
  setattr(StorageBase, name    , partialmethod(_inner_add_method, add_print_title=True))
  setattr(StorageBase, name+"_", partialmethod(_inner_add_method, add_print_title=False))
  
###############################################################################

_ = StorageBase.loop_over_action_list(cllable=add_StorageBase_method)

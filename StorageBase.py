import os
import math
import pandas as pd
import numpy as np

from settings import ENFORCE_SIZE_FETCHING_WHEN_LISTING
from utils import is_equal_str_bytes
from LoggerObj import LoggerObj, FDStatus

#################################################################################
class StorageBase(LoggerObj):

  __txt_chrs = set([chr(i) for i in range(32, 127)] + list("\n\r\t\b"))

  ###############################################################################
  def _check_storage_or_type(storage, StorageType, kwargs):
    errors = []
    if (storage is None) == (StorageType is None):
      errors.append(f"storage_from {storage} and StorageType {StorageType} mustn't be both None or both not None")
    if StorageType is None:
      if kwargs:
        errors.append(f"StorageType is not provided, but arguments {kwargs} are")
    elif not issubclass(StorageType, StorageBase):
      errors.append(f"StorageType {StorageType} is not a subclass of StorageBase")
    return errors

  #################################################################################
  def __init__(self, constructor_kwargs, logger_name=None, objects_to_sync_logger_with=[]):
    self.__constructor_kwargs = {k : v for k, v in constructor_kwargs.items()}
    super().__init__(logger_name=logger_name, objects_to_sync_logger_with=objects_to_sync_logger_with)

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
    pass

  ###############################################################################
  def __please_override(self):
     raise Exception("needs to be overriden", type(self))
      
  ###############################################################################
  def _get_filenames_and_directories(self, dir_name: str):
    self.__please_override()
  
  ###############################################################################
  def _delete_file(self, filename):
    self.__please_override()
    
  ###############################################################################
  def _delete_directory(self, dirname):
    self.__please_override()

  ###############################################################################
  def _create_directory(self, dirname):
    self.__please_override()

  ###############################################################################
  def _create_file_given_content(self, filename, content):
    self.__please_override()

  ###############################################################################
  def _update_file_given_content(self, filename, content):
    self.__please_override()
    
  ###############################################################################
  def _rename_file(self, path_to_existing_file, path_to_new_file):
    self.__please_override()
    
  ###############################################################################
  def _rename_directory(self, path_to_existing_dir, path_to_new_dir):
    self.__please_override()
    
  ###############################################################################
  def _get_content(self, filename, length=None):
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
  def create_directory_in_existing_directory(self, path):
    self._create_directory(path)
    
  ###############################################################################
  def _check_directory_exists_or_create(self, path, create_if_doesnt_exist):
    root_folders = self.split_path_into_dirs_filename(path=path)
    path_so_far = self.get_init_path() 
    was_created = False
    for rf in root_folders:
      _, directories_ = self.get_filenames_and_directories(dir_name=path_so_far)
      path_so_far = os.path.join(path_so_far, rf)
      if path_so_far in directories_:
        continue 
      if create_if_doesnt_exist:
        self.create_directory_in_existing_directory(path_so_far)
        was_created = True
        continue
      return False
    return (not create_if_doesnt_exist) or was_created

  ###############################################################################
  def check_directory_exists(self, path):
    result = self._check_directory_exists_or_create(path, create_if_doesnt_exist=False)
    return result
  
  ###############################################################################
  def check_file_exists(self, path):  
    dirname, filename = os.path.split(path)
    dir_exists = self.check_directory_exists(path=dirname)
    if dir_exists:
      files_, _ = self.get_filenames_and_directories(dir_name=dirname)
      return (path in files_)
    return False

  ###############################################################################
  def check_path_exist_is_dir_not_file(self, path):
    is_file = self.check_file_exists(path)
    is_dir = self.check_directory_exists(path)
    if is_file: 
      return "both" if is_dir else False
    elif is_dir:
      return True
    else:
      return None
  
  ###############################################################################
  def rename_file(self, path_to_existing_file, path_to_new_file):
    if self.check_file_exists(path=path_to_existing_file):
      return self._rename_file(path_to_existing_file=path_to_existing_file, 
                               path_to_new_file=path_to_new_file)
    else:
      raise Exception(f"{self.str(path_to_existing_file)} does not exist")
    
  ###############################################################################
  def rename_directory(self, path_to_existing_dir, path_to_new_dir):
    if self.check_directory_exists(path=path_to_existing_dir):
      return self._rename_directory(path_to_existing_dir=path_to_existing_dir, 
                                    path_to_new_dir=path_to_new_dir)
    else:
      raise Exception(f"{self.str(path_to_existing_dir)} does not exist")
      
  ###############################################################################
  def _filter_out_files(self, files_):
    return files_
  
  ###############################################################################
  def get_filenames_and_directories(self, dir_name):
    try:
      if not dir_name:
        dir_name = self.get_init_path()
      files_, directories_ = self._get_filenames_and_directories(dir_name=dir_name)
      
      files_.sort(key=lambda x: x.lower())
      directories_.sort(key=lambda x: x.lower())
  
      files_ = self._filter_out_files(files_)
  
      return files_, directories_
  
    except Exception as e:
      self.log_error(f'Filenames and directories in {self.str(dir_name)} could not be identified, {e}')
      return FDStatus.Error
      
  ###############################################################################
  def file_contents_is_text(self, filename):
    file_beginning = self.get_content(filename=filename, length=2048)
    result = StorageBase._file_contents_is_text(file_beginning=file_beginning)
    return result

  ###############################################################################
  def get_file_size_or_content(self, filename):
    ffse = getattr(self, '_fetch_file_size_efficiently', None)
    if ffse is not None:
      my_contents = None
      my_file_size = self._fetch_file_size_efficiently(filename)
    else:
      my_contents = self.get_content(filename)
      my_file_size = len(my_contents)

    return my_file_size, my_contents
  
  ###############################################################################
  def delete_file(self, filename):
    try:
      if self.check_file_exists(filename):
        self._delete_file(filename)
        return FDStatus.RightOnly_or_Deleted
      else:
        self.log_warning(f'{self.str(filename)} not found')
        return FDStatus.Error
    except Exception as e:
      self.log_error(f'{self.str(filename)} could not be deleted, {e}')
      return FDStatus.Error
    
  ###############################################################################
  def delete_directory(self, dirname):
    try:
      if self.check_directory_exists(dirname):
        self._delete_directory(dirname)
        return FDStatus.RightOnly_or_Deleted
      else:
        self.log_warning(f'{self.str(dirname)} not found')
        return FDStatus.Error
    except Exception as e:
      self.log_error(f'{self.str(dirname)} could not be deleted, {e}')
      return FDStatus.Error

  ###############################################################################
  def create_file_given_content(self, filename, content, check_if_contents_is_the_same_before_writing=True):
    try:
      assert filename, "Filename is not defined"
      path_exist_is_dir_not_file_to = self.check_path_exist_is_dir_not_file(filename)
      if path_exist_is_dir_not_file_to is False: # it's a file
        if check_if_contents_is_the_same_before_writing:
          current_contents = self.get_content(filename)
          if is_equal_str_bytes(content, current_contents):
            return FDStatus.Identical
        self._update_file_given_content(filename=filename, content=content)
        return FDStatus.Different_or_Updated
      elif path_exist_is_dir_not_file_to is None: # it does not exist
        self._check_directory_exists_or_create(path=os.path.dirname(filename), 
                                               create_if_doesnt_exist=True)
        self._create_file_given_content(filename=filename, content=content)
        return FDStatus.LeftOnly_or_New
      else: # it's a folder or both
        self.log_error(f'{self.str(filename)} exists, and it is a directory')
        return FDStatus.Error
    except Exception as e:
      self.log_error(f'Contents of {self.str(filename)} could not be set: {e}')
      return FDStatus.Error

  ###############################################################################
  def get_content(self, filename):
    try:
      result = self._get_content(filename=filename)
      return result
    except Exception as e:
      self.log_error(f'Contents of {self.str(filename)} could not be obtained, {e}')
      return math.nan
  
  ###############################################################################
  def fetch_file_size(self, filename):
    try:
      ffse = getattr(self, '_fetch_file_size_efficiently', None)
      if ffse:
        result = ffse(filename=filename)
      else:
        result = len(self.get_content(filename=filename))
      return result
    except Exception as e:
      self.log_error(f'Contents of {self.str(filename)} could not be set, {e}')
      return math.nan
        
    return FDStatus.LeftOnly_or_New
    return FDStatus.RightOnly_or_Deleted
    return FDStatus.Different_or_Updated
    return FDStatus.Identical
    return FDStatus.Error


  ###############################################################################
  def get_size(self, path):
    path_exist_is_dir_not_file = self.check_path_exist_is_dir_not_file(path)
    if path_exist_is_dir_not_file is True:
      files_, directories_ = self._get_filenames_and_directories(dir_name=path)
      result = sum([self.fetch_file_size(f) for f in files_]) \
             + sum([self.get_size(path=d) for d in directories_])
      return result
    elif path_exist_is_dir_not_file is False:
      return self.fetch_file_size(filename=path)  
    elif path_exist_is_dir_not_file == "both":
      self.log_error(f"{self.str(path)} is both a file and a directory")
    else:
      self.log_error(f"{self.str(path)} does not exist")  
  
  ###############################################################################
  def _list_files_directories_recursive(self, dir_to_list, enforce_size_fetching, message2=''):

    self.log_enter_level(dirname=dir_to_list, message_to_print='Listing', message2=message2)

    files_, dirs_ = self.get_filenames_and_directories(dir_to_list)

    if enforce_size_fetching:
      df = [[os.path.basename(f), self.fetch_file_size(f)] for f in files_]
    else:
      df = [[os.path.basename(f)                         ] for f in files_]
    self.print_files_df(data =df)

    total_size_first_level = sum([dfr[1] for dfr in df]) if enforce_size_fetching else math.nan
    totals = np.array([total_size_first_level, len(files_), len(dirs_)])

    dirs_dict = {}  
    for dir_ in dirs_:
      dir_totals, dir_files, dir_dirs_dict = self._list_files_directories_recursive(dir_to_list=dir_, enforce_size_fetching=enforce_size_fetching)
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
  def list(self, path, enforce_size_fetching=ENFORCE_SIZE_FETCHING_WHEN_LISTING):
    self.log_title(title=f'Listing {self.str(path)}')
    path_exist_is_dir_not_file = self.check_path_exist_is_dir_not_file(path)
    if path_exist_is_dir_not_file is True:
      result = self._list_files_directories_recursive(dir_to_list=path, enforce_size_fetching=enforce_size_fetching)
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
    path_exist_is_dir_not_file = self.check_path_exist_is_dir_not_file(path)
    if path_exist_is_dir_not_file is True:
      self.delete_directory(path)
    elif path_exist_is_dir_not_file is False:
      self.delete_file(path)  
    elif path_exist_is_dir_not_file == "both":
      self.log_error(f"{self.str(path)} is both a file and a directory")
    else:
      self.log_error(f"{self.str(path)} does not exist")  

###############################################################################
  def delete(self, path):
    self.log_title(title=f'Deleting {self.str(path)}')
    self._delete(path=path)

###############################################################################
  def create_directory(self, dir_name):
    self.log_title(title=f'Creating {self.str(dir_name)}')
    path_exist_is_dir_not_file = self.check_path_exist_is_dir_not_file(dir_name)
    if path_exist_is_dir_not_file is not None:
      self.log_warning(message=f"Skipping because {self.str(dir_name)} exists")
    else:
      self._check_directory_exists_or_create(dir_name, create_if_doesnt_exist=True)

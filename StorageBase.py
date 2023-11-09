import os
import math
from enum import Enum

#################################################################################
class FDStatus(Enum):
  LeftOnly_or_New  = 0
  RightOnly_or_Deleted = 1
  Different_or_Updated = 2
  Identical = 3
  Error     = 4

#################################################################################
class StorageBase():

  __txt_chrs = set([chr(i) for i in range(32, 127)] + list("\n\r\t\b"))

  #################################################################################
  def __init__(self, constructor_kwargs):
    self.__cached_filenames_flat, self.__cached_directories_flat = {}, self._get_default_root_dir_info()
    self.__constructor_kwargs = {k : v for k, v in constructor_kwargs.items()}

  ###############################################################################
  def get_constructor_kwargs(self):
    return self.__constructor_kwargs
    
  #################################################################################
  def _find_secret_components(self, how_many, secret_name=None):
    if secret_name is None:
      secret_name = 'default_' + type(self).__name__[len('Storage'):].lower() + '_secret'
    secret = os.getenv(secret_name)
    secret_components = secret.split('|') if secret else []
    if isinstance(how_many, int):
      assert len(secret_components) == how_many, f"There should be {how_many} {type(self).__name__} secret components in environment variable {secret_name}, but {len(secret_components)} are provided"
    else:
      assert len(secret_components) in how_many, f"There should be {' or '.join([str(h) for h in how_many])} {type(self).__name__} secret components in environment variable {secret_name}, but {len(secret_components)} are provided"
    return secret_components

  #################################################################################
  def str(self, dir_name):
    result = f'{type(self).__name__}(`{dir_name}`)'
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
  def get_file_info(self, filename, info_name):
    return self.__cached_filenames_flat[filename][info_name]

  ###############################################################################
  def set_file_info(self, filename, param_dict):
    if filename not in self.__cached_filenames_flat:
      self.__cached_filenames_flat[filename] = {}
    self.__cached_filenames_flat[filename].update(param_dict)

  ###############################################################################
  def get_dir_info(self, dirname, info_name):
    return self.__cached_directories_flat[dirname][info_name]

  ###############################################################################
  def set_dir_info(self, dirname, param_dict):
    if dirname not in self.__cached_directories_flat:
      self.__cached_directories_flat[dirname] = {}
    self.__cached_directories_flat[dirname].update(param_dict)
    
  ###############################################################################
  def get_contents(self, filename, length=None):
    self.__please_override()

  ###############################################################################
  def inexistent_directories_are_empty(self):
    return False
    
  ###############################################################################
  def get_init_path(self):
    return ''    

  ###############################################################################  
  def _get_default_root_dir_info(self):
    return {}

  ###############################################################################
  def split_path_into_dirs_filename(path):
    result = []
    while path:
      path, tail = os.path.split(path)
      result = [tail] + result   
    return result

  ###############################################################################
  def create_directory_in_existing_directory(self, path):
    info = self._create_directory(path)
    if info is None:
      info = {}
    self.set_dir_info(path, info)
    
  ###############################################################################
  def _check_directory_exists_or_create(self, path, create_if_doesnt_exist):
    root_folders = StorageBase.split_path_into_dirs_filename(path=path)
    if (len(root_folders) > 1) and (not root_folders[-1]):
      root_folders.pop(-1)
    path_so_far = self.get_init_path() 
    was_created = False
    for rf in root_folders:
      _, directories_ = self._get_filenames_and_directories(dir_name=path_so_far)
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
  def create_directory(self, path):
    dir_didnt_exist_before = self._check_directory_exists_or_create(path, create_if_doesnt_exist=True)
    return dir_didnt_exist_before
  
  ###############################################################################
  def check_file_exists(self, path):  
    dirname, filename = os.path.split(path)
    dir_exists = self.check_directory_exists(path=dirname)
    if dir_exists:
      files_, _ = self._get_filenames_and_directories(dir_name=dirname)
      return (path in files_)
    return False

  ###############################################################################
  def check_path_exist_is_dir_not_file(self, path):
    print('check_path_exist_is_dir_not_file', path)
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
  def get_filenames_and_directories(self, root, enforce_size_fetching=False):
    files_, directories_ = self._get_filenames_and_directories(dir_name=root)
    
    files_.sort(key=lambda x: x.lower())
    directories_.sort(key=lambda x: x.lower())

    files_ = self._filter_out_files(files_)

    if not enforce_size_fetching:
      return files_, directories_, math.nan

    #files_sizes = [[f, math.nan] for f in files_]
    total_size = 0
    for i, filename in enumerate(files_):
      file_info = self.fetch_file_info(filename, enforce_size_fetching=True)
      total_size += file_info['size']
    
    return files_, directories_, total_size

  ###############################################################################
  def fetch_file_info(self, filename, enforce_size_fetching=True):
    file_info = {}
    if enforce_size_fetching:
      file_size = self._fetch_file_size(filename)
      file_info['size'] = file_size
    self.set_file_info(filename, file_info)
    return file_info

  ###############################################################################
  def file_contents_is_text(self, filename):
    file_beginning = self.get_contents(filename=filename, length=2048)
    result = StorageBase._file_contents_is_text(file_beginning=file_beginning)
    return result
        
  ###############################################################################
  def _create_file_in_another_source(self, my_filename, source, source_filename):
    my_contents = self.get_contents(my_filename)
    source.create_file_given_content(filename=source_filename, content=my_contents)
    return len(my_contents)
  
  ###############################################################################
  def check_if_files_are_identical(self, my_filename, source, source_filename):
    
    definitely_different = False
    for info_name in ['size']: #, 'modified', 'textness'
      info_from = source.get_file_info(source_filename, info_name)
      info_to = self.get_file_info(my_filename, info_name)
      if (info_from is not None) and (info_to is not None) and ((info_from > info_to) if info_name == 'modified' else (info_from != info_to)):
        definitely_different = True
      
    if definitely_different:
      return False, None

    from_contents = source.get_contents(source_filename) 
    files_are_identical_ = self.get_contents(my_filename) == from_contents

    return files_are_identical_, from_contents
    
  ###############################################################################
  def create_file(self, my_filename, source, source_filename):
    try:
      size_contents = source._create_file_in_another_source(my_filename=source_filename, 
                                                      source=self, 
                                                      source_filename=my_filename)
      return size_contents
    except:
      self._logger.log_error(f'{self.str(my_filename)} could not be created from {source.str(source_filename)}')
      return math.nan
  
  ###############################################################################
  def delete_file(self, filename):
    try:
      if self.check_file_exists(filename):
        self._delete_file(filename)
        return FDStatus.RightOnly_or_Deleted
      else:
        self._logger.log_warning(f'{self.str(filename)} not found')
        return FDStatus.Error
    except:
      self._logger.log_error(f'{self.str(filename)} could not be deleted')
      return FDStatus.Error
    
  ###############################################################################
  def delete_directory(self, dirname):
    try:
      if self.check_directory_exists(dirname):
        self._delete_directory(dirname)
        return FDStatus.RightOnly_or_Deleted
      else:
        self._logger.log_warning(f'{self.str(dirname)} not found')
        return FDStatus.Error
    except:
      self._logger.log_error(f'{self.str(dirname)} could not be deleted')
      return FDStatus.Error

  ###############################################################################
  def create_file_given_content(self, filename, content, check_if_contents_is_the_same_before_writing=True):
    try:
      path_exist_is_dir_not_file_to = self.check_path_exist_is_dir_not_file(filename)
      if path_exist_is_dir_not_file_to is False: # it's a file
        if check_if_contents_is_the_same_before_writing:
          if content == self.get_contents(filename):
            return FDStatus.Identical
        self._update_file_given_content(filename=filename, content=content)
        return FDStatus.Different_or_Updated
      elif path_exist_is_dir_not_file_to is None: # it does not exist
        self._create_file_given_content(filename=filename, content=content)
        return FDStatus.LeftOnly_or_New
      else: # it's a folder or both
        self._logger.log_error(f'{self.str(filename)} exists, and it is a directory')
        return FDStatus.Error
    except:
      self._logger.log_error(f'Contents of {self.str(dirname)} could not be set')
      return FDStatus.Error


      return FDStatus.LeftOnly_or_New
      return FDStatus.RightOnly_or_Deleted
      return FDStatus.Different_or_Updated
      return FDStatus.Identical
      return FDStatus.Error
import os
import math

#################################################################################
class StorageBase():

  __txt_chrs = set([chr(i) for i in range(32, 127)] + list("\n\r\t\b"))

  #################################################################################
  def __init__(self):
    self.__cached_filenames_flat, self.__cached_directories_flat = {}, self._get_default_root_dir_info()

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
    return self

  ###############################################################################
  def __exit__(self, type, value, traceback):
    pass

  ###############################################################################
  def __please_override(self):
     raise Exception("needs to be overriden", type(self))
      
  ###############################################################################
  def _get_filenames_and_directories(self, root: str):
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
  def split_path_into_folders_filename(path):
    result = []
    while path:
      path, tail = os.path.split(path)
      result = [tail] + result   
    return result

  ###############################################################################
  def create_directory_in_existing_folder(self, path):
    info = self._create_directory(path)
    if info is None:
      info = {}
    self.set_dir_info(path, info)
    
  ###############################################################################
  def check_directory_exists(self, path, create_if_doesnt_exist=False):
    root_folders = StorageBase.split_path_into_folders_filename(path=path)
    if (len(root_folders) > 1) and (not root_folders[-1]):
      root_folders.pop(-1)
    path_so_far = self.get_init_path() 
    result = True
    for rf in root_folders:
      _, directories_ = self._get_filenames_and_directories(path_so_far=path_so_far)
      path_so_far = os.path.join(path_so_far, rf)
      
      if path_so_far in directories_:
        continue 
        
      if create_if_doesnt_exist:
        result = "created"
        self.create_directory_in_existing_folder(path_so_far)
        continue
      
      return False
      
    return result

  ###############################################################################
  def check_file_exists(self, path):  
    dirname, filename = os.path.split(path)
    dir_exists = self.check_directory_exists(path=dirname)
    if dir_exists:
      files_, _ = self._get_filenames_and_directories(path_so_far=dirname)
      return (path in files_)
    return False
    
  ###############################################################################
  def _filter_out_files(self, files_):
    return files_
  
  ###############################################################################
  def get_filenames_and_directories(self, root, enforce_size_fetching=False):
    files_, directories_ = self._get_filenames_and_directories(path_so_far=root)
    
    files_.sort(key=lambda x: x.lower())
    directories_.sort(key=lambda x: x.lower())

    files_ = self._filter_out_files(files_)

    if not enforce_size_fetching:
      return files_, directories_, math.nan

    #files_sizes = [[f, math.nan] for f in files_]
    total_size = 0
    for i, filename in enumerate(files_):
      file_size = self._fetch_file_size(filename)
      #files_sizes[i][1] = file_size
      self.set_file_info(filename, {'size' : file_size})
      total_size += file_size
    
    return files_, directories_, total_size

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
    size_contents = source._create_file_in_another_source(my_filename=source_filename, 
                                                    source=self, 
                                                    source_filename=my_filename)
    return size_contents

  ###############################################################################
  def delete_file(self, filename):
    self._delete_file(filename)
    #log_print('DELETED file ', filename)
    
  ###############################################################################
  def delete_directory(self, dirname):
    self._delete_directory(dirname)
    #log_print('DELETED dir ', dirname)

  ###############################################################################
  def create_file_given_content(self, filename, content):
    self._create_file_given_content(filename=filename, content=content)
    #log_print('CREATED file ', filename)

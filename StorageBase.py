import os
from settings import only_print_basename

level = None
dry_run = False

def reset_level():
  global level
  level = 0
  
def increment_level():
  global level
  level += 1
  
def decrement_level():
  global level
  level -= 1

def unset_level():
  global level
  level = None

def do_dry_run():
  global dry_run
  dry_run = True

def is_dry_run():
  global dry_run
  return dry_run
  
#################################################################################
class StorageBase():

  __txt_chrs = set([chr(i) for i in range(32, 127)] + list("\n\r\t\b"))
  
  def __init__(self):
    self.__cached_filenames_flat, self.__cached_directories_flat = {}, self._get_default_root_dir_info()

  def __log(message0, name, message1=''):
    global level
    global dry_run
    
    prefix = ''
    # boxy symbols https://www.ncbi.nlm.nih.gov/staff/beck/charents/unicode/2500-257F.html
    if level is not None:
      prefix = '│' * (level - 1) + ('┌' if 'dir' in message0 else '├─') + "─── "
    if dry_run:
      prefix += 'would '
    print(prefix + message0 + '`' + (os.path.basename(name) if (only_print_basename and (level != 0)) else name) + '`' + message1)

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
  def check_directory_exists(self, path, create_if_doesnt_exist=False):
    root_folders = StorageBase.split_path_into_folders_filename(path=path)
    if (len(root_folders) > 1) and (not root_folders[-1]):
      root_folders.pop(-1)
    path_so_far = self.get_init_path() 
    result = True
    for rf in root_folders:
      _, directories_ = self._get_filenames_and_directories(path_so_far=path_so_far)
      path_so_far = os.path.join(path_so_far, rf)
      if path_so_far not in directories_:
        if not create_if_doesnt_exist:
          return False
        self.create_directory(dirname=path_so_far)
        result = "created"
    return result

  ###############################################################################
  def check_file_exists(self, path, create_if_doesnt_exist=False):  
    dirname, filename = os.path.split(path)
    dir_exists = self.check_directory_exists(path=dirname, create_if_doesnt_exist=False)
    if dir_exists:
      files_, _ = self._get_filenames_and_directories(path_so_far=dirname)
      return (path in files_)
    return False
    
  ###############################################################################
  def _filter_out_files(self, files_):
    return files_
  
  ###############################################################################
  def get_filenames_and_directories(self, root: str):
    global dry_run
    if dry_run and (not self.check_file_exists(root)):
      return [], []
    files_, directories_ = self._get_filenames_and_directories(path_so_far=root)
    
    files_.sort(key=lambda x: x.lower())
    directories_.sort(key=lambda x: x.lower())

    files_ = self._filter_out_files(files_)
    
    for filename in files_:
      info = self._fetch_stats_one_file(filename)
      #info['textness'] = self.file_contents_is_text(filename=filename)
      self.set_file_info(filename, info)

    return files_, directories_

  ###############################################################################
  def file_contents_is_text(self, filename):
    file_beginning = self.get_contents(filename=filename, length=2048)
    result = StorageBase._file_contents_is_text(file_beginning=file_beginning)
    return result
        
  ###############################################################################
  def _create_file_in_another_source(self, my_filename, source, source_filename):
    my_contents = self.get_contents(my_filename)
    source.create_file_given_content(filename=source_filename, content=my_contents)
  
  ###############################################################################
  def compare_and_update_file(self, my_filename, source, source_filename):
    
    extra_messages = []
    
    definitely_different = False
    for info_name in ['size']: #, 'modified', 'textness'
      info_from = source.get_file_info(source_filename, info_name)
      info_to = self.get_file_info(my_filename, info_name)
      if (info_from is not None) and (info_to is not None) and ((info_from > info_to) if info_name == 'modified' else (info_from != info_to)):
        definitely_different = True
        extra_messages.append(f'{info_name}: {info_from if info_from is not None else "???"} -> {info_to if info_to is not None else "???"}')
      else:
        extra_messages.append(f'{info_name}: {info_from if info_from is not None else "???"} vs. {info_to if info_to is not None else "???"}')
      
    from_contents = source.get_contents(source_filename) 
    extra_message = f'{", ".join(extra_messages)}'
    if (not definitely_different) and (self.get_contents(my_filename) == from_contents):
      StorageBase.__log('keep __ file ', my_filename, f': identical contents, {extra_message}')
    else:
      self.update_file_given_content(filename=my_filename, content=from_contents, extra_message=': '+extra_message)

  ###############################################################################
  def create_file(self, my_filename, source, source_filename):
    source._create_file_in_another_source(my_filename=source_filename, 
                                                    source=self, 
                                                    source_filename=my_filename)

  ###############################################################################
  def delete_file(self, filename):
    global dry_run
    if not dry_run:
      self._delete_file(filename)
    StorageBase.__log('DELETED file ', filename)
    
  ###############################################################################
  def delete_directory(self, dirname):
    global dry_run
    if not dry_run:
      self._delete_directory(dirname)
    StorageBase.__log('DELETED dir ', dirname)

  ###############################################################################
  def create_file_given_content(self, filename, content):
    global dry_run
    if not dry_run:
      self._create_file_given_content(filename=filename, content=content)
    StorageBase.__log('CREATED file ', filename)

  ###############################################################################
  def update_file_given_content(self, filename, content, extra_message):
    global dry_run
    if not dry_run:
      self._update_file_given_content(filename=filename, content=content)
    StorageBase.__log('UPDATED file ', filename, extra_message)
  
  ###############################################################################
  def create_directory(self, dirname):
    global dry_run
    if not dry_run:
      info = self._create_directory(dirname)
      if info is None:
        info = {}
      self.set_dir_info(dirname, info)
    StorageBase.__log('CREATED dir ', dirname)
    
###############################################################################    
  def log_entering_directory(self, dirname):
    StorageBase.__log('kept __ dir ', dirname)

###############################################################################    
  def list_directory(self, dirname):
    StorageBase.__log('dir  ', dirname)

###############################################################################    
  def list_file(self, filename):
    StorageBase.__log('file ', filename)
    
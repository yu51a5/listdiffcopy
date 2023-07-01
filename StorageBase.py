import os

#################################################################################
class StorageBase():

  __txt_chrs = set([chr(i) for i in range(32, 127)] + list("\n\r\t\b"))
  
  def __init__(self, name):
    self.clean_cache()
    self.name = name

  def __log(message, *args):
    print(message, *args)

  #################################################################################
  # source: stackoverflow.com/questions/1446549
  # 2048 bytes because of https://pypi.org/project/python-magic/
  def __file_contents_is_text(file_beginning):
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
  def get_stats(self, filename):
    self.__please_override()

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
  def __print_files_directories_recursive(files, directories):
    StorageBase.__log(message='Files----')
    for f in files:
      StorageBase.__log(message=f)
    for d, (fi, dir) in directories.items():
      StorageBase.__log(message=f'Directory ---- {d}----')
      StorageBase.__print_files_directories_recursive(fi, dir)

  ###############################################################################
  def get_filenames_and_directories_and_cache(self, root: str):

    head = root
    root_folders = []
    while head:
      head, tail = os.path.split(head)
      root_folders = [tail] + root_folders

    path_so_far = self.get_init_path()
    self.cached_filenames, self.cached_directories = {}, {}
    self.cached_filenames_flat, self.cached_directories_flat = {}, {path_so_far : 0}
    for rf in root_folders:
      _, directories_ = self._get_filenames_and_directories(recursive=False, path_so_far=path_so_far)
      path_so_far = os.path.join(path_so_far, rf)
      if path_so_far not in directories_:
        if self.inexistent_directories_are_empty():
          return self.cached_filenames, self.cached_directories
        self.create_directory(dirname=path_so_far)
        _, directories_ = self._get_filenames_and_directories(recursive=False, path_so_far=os.path.dirname(path_so_far))
    
    self.cached_filenames, self.cached_directories = self._get_filenames_and_directories(recursive=True, path_so_far=root)
    StorageBase.__print_files_directories_recursive(files=self.cached_filenames, directories=self.cached_directories)
    return self.cached_filenames, self.cached_directories

  ###############################################################################
  def clean_cache(self):
    self.cached_filenames, self.cached_directories = None, None
    self.cached_filenames_flat, self.cached_directories_flat = None, None

  ###############################################################################
  def file_contents_is_text(self, filename):
    file_beginning = self.get_contents(filename=filename, length=2048)
    result = StorageBase.__file_contents_is_text(file_beginning=file_beginning)
    return result

  ###############################################################################
  def _get_definitely_different_and_textness(self, from_filename, to_source, to_filename):
    from_stats = self.get_stats(from_filename)
    to_stats = to_source.get_stats(to_filename)

    if from_stats['size'] != to_stats['size']:
      self.__log('sizes different')
      return True, None
    if from_stats['modified'] > to_stats['modified']:
      self.__log('sizes not right')
      return True, None
    
    from_is_text = self.file_contents_is_text(from_filename) 
    
    return from_is_text != to_source.file_contents_is_text(to_filename), from_is_text

  ###############################################################################
  def _compare_and_update_a_file_in_another_source(self, my_filename, another_source, another_source_filename):
    definitely_different, textness = self._get_definitely_different_and_textness(from_filename=my_filename, 
                                                                                 to_source=another_source, 
                                                                                 to_filename=another_source_filename)
    if (not definitely_different) and (not textness):
      print('definitely_different, textness', definitely_different, textness, my_filename)
      return
      
    my_contents = self.get_contents(my_filename) 
    if not definitely_different: 
      if another_source.get_contents(another_source_filename) == my_contents:
        print('same contents', my_filename)
        return
        
    another_source.update_file_given_content(filename=another_source_filename, content=my_contents)
        
  ###############################################################################
  def _create_a_file_in_another_source(self, my_filename, another_source, another_source_filename):
    my_contents = self.get_contents(my_filename)
    another_source.create_file_given_content(filename=another_source_filename, content=my_contents)
  
  ###############################################################################
  def compare_and_update_a_file(self, my_filename, another_source, another_source_filename):
    another_source._compare_and_update_a_file_in_another_source(my_filename=another_source_filename, 
                                                                another_source=self, 
                                                                another_source_filename=my_filename)
  
  ###############################################################################
  def create_a_file(self, my_filename, another_source, another_source_filename):
    another_source._create_a_file_in_another_source(my_filename=another_source_filename, 
                                                    another_source=self, 
                                                    another_source_filename=my_filename)

  ###############################################################################
  def delete_file(self, filename):
    self._delete_file(filename)
    StorageBase.__log(message='removed file ' + filename)
    
  ###############################################################################
  def delete_directory(self, dirname):
    self._delete_directory(dirname)
    StorageBase.__log(message='removed directory ' + dirname)

  ###############################################################################
  def create_file_given_content(self, filename, content):
    self._create_file_given_content(filename=filename, content=content)
    StorageBase.__log(message='created file ' + filename)

  ###############################################################################
  def update_file_given_content(self, filename, content):
    self._update_file_given_content(filename=filename, content=content)
    StorageBase.__log(message='updated file ' + filename)
  
  ###############################################################################
  def create_directory(self, dirname):
    self._create_directory(dirname)
    StorageBase.__log(message='created directory ' + dirname)
    
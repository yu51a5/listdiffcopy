import os

#################################################################################
class StorageBase():
  def __init__(self, name):
    self.cached_filenames = None
    self.name = name

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
  def get_contents(self, filename):
    self.__please_override()
    
  ###############################################################################
  def compare_stats_not_content(self):
    return True

  ###############################################################################
  def inexistent_directories_are_empty(self):
    return False
    
  ###############################################################################
  def get_init_path(self):
    return ''

  ###############################################################################
  def __print_files_directories_recursive(files, directories):
    print('Files----')
    for f in files:
      print(f)
    for d, (fi, dir) in directories.items():
      print(f'Directory ---- {d}----')
      StorageBase.__print_files_directories_recursive(fi, dir)

  ###############################################################################
  def get_filenames_and_directories_and_cache(self, root: str):

    head = root
    root_folders = []
    while head:
      head, tail = os.path.split(head)
      root_folders = [tail] + root_folders

    folderid = 0
    path_so_far = self.get_init_path()
    print('root_folders', root_folders)
    for rf in root_folders:
      _, directories_ = self._get_filenames_and_directories(folderid=folderid, recursive=False, path_so_far=path_so_far)
      path_so_far = os.path.join(path_so_far, rf)
      print("JUST path_so_far", path_so_far)
      if path_so_far not in directories_:
        if self.inexistent_directories_are_empty():
          self.cached_filenames, self.cached_directories = {}, {}
          return self.cached_filenames, self.cached_directories
        self.create_directory(dirname=path_so_far)
        print("CREATED", path_so_far)
        _, directories_ = self._get_filenames_and_directories(folderid=folderid, recursive=False, path_so_far=os.path.dirname(path_so_far))
      folderid = directories_[path_so_far]
    
    self.cached_filenames, self.cached_directories = self._get_filenames_and_directories(folderid=folderid, recursive=True, path_so_far=root)
    StorageBase.__print_files_directories_recursive(files=self.cached_filenames, directories=self.cached_directories)
    return self.cached_filenames, self.cached_directories

  ###############################################################################
  def clean_cache(self):
    self.cached_filenames_and_directories = None

  ###############################################################################
  def _file_stats_are_comparable_and_same(self, my_filename, another_source, another_source_filename):
    compare_stats = another_source.compare_stats_not_content() and self.compare_stats_not_content()
    comp_result = compare_stats and (self.get_stats(my_filename) == another_source.get_stats(another_source_filename))
    return compare_stats, comp_result

  ###############################################################################
  def _compare_and_update_a_file_in_another_source(self, my_filename, another_source, another_source_filename):
    compare_stats, comp_result = self._file_stats_are_comparable_and_same(my_filename=my_filename, 
                                                                          another_source=another_source, 
                                                                          another_source_filename=another_source_filename)
    if not comp_result:
      my_contents = self.get_contents(my_filename) 
      if compare_stats or (another_source.get_contents(another_source_filename) != my_contents):
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
    print('removed file ' + filename)
    
  ###############################################################################
  def delete_directory(self, dirname):
    self._delete_directory(dirname)
    print('removed directory ' + dirname)

  ###############################################################################
  def create_file_given_content(self, filename, content):
    self._create_file_given_content(filename=filename, content=content)
    print('created file ' + filename)

  ###############################################################################
  def update_file_given_content(self, filename, content):
    self._update_file_given_content(filename=filename, content=content)
    print('updated file ' + filename)
  
  ###############################################################################
  def create_directory(self, dirname):
    self._create_directory(dirname)
    print('created directory ' + dirname)
    
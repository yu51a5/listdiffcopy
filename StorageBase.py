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
  def _get_filenames_and_directories(self, root: str):
    raise Exception("needs to be overriden")

  ###############################################################################
  def _delete_file(self, filename):
    raise Exception("needs to be overriden")
    
  ###############################################################################
  def _delete_directory(self, dirname):
    raise Exception("needs to be overriden")

  ###############################################################################
  def _create_directory(self, dirname):
    raise Exception("needs to be overriden")
  
  ###############################################################################
  def compare_stats_not_content(self):
    return True

  ###############################################################################
  def inexistent_directories_are_empty(self):
    return False
  
  ###############################################################################
  def delete_file(self, filename):
    self._delete_file(filename)
    print('removed file ' + filename)
    
  ###############################################################################
  def delete_directory(self, dirname):
    self._delete_directory(dirname)
    print('removed directory ' + dirname)

  ###############################################################################
  def create_directory(self, dirname):
    self._create_directory(dirname)
    print('created directory ' + dirname)
    
  ###############################################################################
  def get_init_path(self):
    return ''

  ###############################################################################
  def get_filenames_and_directories_and_cache(self, root: str):

    head = root
    root_folders = []
    while head:
      head, tail = os.path.split(head)
      root_folders = [tail] + root_folders

    folderid = 0
    path_so_far = self.get_init_path()
    for rf in root_folders:
      _, directories_ = self._get_filenames_and_directories(folderid=folderid, recursive=False, path_so_far=path_so_far)
      path_so_far = os.path.join(path_so_far, rf)
      if path_so_far not in directories_:
        if self.inexistent_directories_are_empty():
          self.cached_filenames, self.cached_directories = {}, {}
          return self.cached_filenames, self.cached_directories
        self.create_directory(dirname=path_so_far)
        _, directories_ = self._get_filenames_and_directories(folderid=folderid, recursive=False, path_so_far=os.path.dirname(path_so_far))
      folderid = directories_[path_so_far]
      
    
    self.cached_filenames, self.cached_directories = self._get_filenames_and_directories(folderid=folderid, recursive=True, path_so_far=root)
    return self.cached_filenames, self.cached_directories

  ###############################################################################
  def clean_cache(self):
    self.cached_filenames_and_directories = None

  ###############################################################################
  def compare_and_update_a_file(self, another_source, another_source_filename, my_filename):
    another_source._compare_and_update_a_file_in_another_source(my_filename=another_source_filename, 
                                                                another_source=self, 
                                                                another_source_filename=my_filename)

  ###############################################################################
  def _compare_and_update_a_file_in_another_source(self, my_filename, another_source, another_source_filename):
    compare_stats = another_source.compare_stats_not_content() and self.compare_stats_not_content()
    if compare_stats and (self.get_stats(my_filename) == another_source.stats(another_source_filename)):
      return
    my_contents = self.read(my_filename) 
    if compare_stats or (another_source.read(another_source_filename) != my_contents):
      another_source.update_file(another_source_filename, content=my_contents)
      print('updated ' + another_source_filename)

    
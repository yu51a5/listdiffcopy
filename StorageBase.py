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
  def compare_stats_not_content(self):
    return True
  
  ###############################################################################
  def delete_file(self, filename):
    self._delete_file(filename)
    print('removed file ' + filename)
    
  ###############################################################################
  def delete_directory(self, dirname):
    self._delete_directory(dirname)
    print('removed directory ' + dirname)
  
  ###############################################################################
  def get_folder_pairs(self):
    sftp_storage_folders_tuples = os.environ[f'sftp_{self.name}_folders'].split(';')
    sftp_storage_folders_pairs = [gsp.split(',') for gsp in sftp_storage_folders_tuples]
    return sftp_storage_folders_pairs

  ###############################################################################
  def get_filenames_and_directories_and_cache(self, root: str):
    self.cached_filenames_and_directories = self._get_filenames_and_directories(root=root)
    return self.cached_filenames_and_directories

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
      
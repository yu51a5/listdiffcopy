import os
import shutil
from StorageBase import StorageBase

#################################################################################
class StorageLocal(StorageBase):

  ###############################################################################
  # Use eapi if the server is in Europe
  # For Pcloud token, see
  def __init__(self):
    super().__init__()

  ###############################################################################
  def get_init_path(self):
    return '.'
    
  ###############################################################################
  def _get_filenames_and_directories(self, path_so_far : str):
    files_, directories_ = [], []
    for basename_ in os.listdir(path_so_far):
      full_name = os.path.join(path_so_far, basename_)
      
      (files_ if os.path.isfile(full_name) else directories_).append(full_name)

    return files_, directories_

###############################################################################
  def get_contents(self, filename, length=None):
    f = open(filename, "r")
    return f.read()

  ###############################################################################
  def _delete_file(self, filename):
    os.remove(filename)

  ###############################################################################
  def _delete_directory(self, dirname):
    shutil.rmtree(dirname=dirname)

  ###############################################################################
  def _create_directory(self, dirname):
    os.mkdir(dirname)

  ###############################################################################
  def _create_file_given_content(self, filename, content):
    mode = "w" if isinstance(content, str) else "wb"
    with open(filename, mode) as file_object:
      file_object.write(content)

  ###############################################################################
  def _update_file_given_content(self, filename, content):
    self._create_file_given_content(filename=filename, content=content)

  ###############################################################################
  def _fetch_file_size(self, filename):
    return os.path.getsize(filename)

  ###############################################################################
  def _rename_file(self, path_to_existing_file, path_to_new_file):
    os.rename(path_to_existing_file, path_to_new_file)

  ###############################################################################
  def _rename_directory(self, path_to_existing_dir, path_to_new_dir):
    # https://stackoverflow.com/questions/8735312/how-to-change-folder-names-in-python
    shutil.move(path_to_existing_dir, path_to_new_dir)

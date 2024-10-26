import os
import shutil
from listdiffcopy.StorageBase import StorageBase

#################################################################################
class StorageLocal(StorageBase):

  _init_path = '.'

  ###############################################################################
  def __init__(self, logger_name=None, objects_to_sync_logger_with=[]):
    super().__init__(constructor_kwargs={}, logger_name=logger_name, objects_to_sync_logger_with=objects_to_sync_logger_with)
    
  ###############################################################################
  def _get_filenames_and_directories(self, path : str):
    files_, directories_ = [], []
    for basename_ in os.listdir(path):
      full_name = os.path.join(path, basename_)      
      (files_ if os.path.isfile(full_name) else directories_).append(full_name)

    return files_, directories_

###############################################################################
  def _read_file(self, path, binary=True, length=None):
    with open(path, "rb" if binary else "r") as fi:
      result = fi.read()
      return result
  
  ###############################################################################
  def _delete_file(self, filename):
    os.remove(filename)

  ###############################################################################
  def _delete_directory(self, path):
    shutil.rmtree(path=path)

  ###############################################################################
  def _create_directory_only(self, path):
    os.mkdir(path)

  ###############################################################################
  def _create_file_given_content(self, path, content):
    mode = "w" if isinstance(content, str) else "wb"
    with open(path, mode) as file_object:
      file_object.write(content)

  ###############################################################################
  def _fetch_file_size_efficiently(self, path):
    return os.path.getsize(path)

  ###############################################################################
  def _rename_file(self, path_to_existing_file, path_to_new_file):
    os.rename(path_to_existing_file, path_to_new_file)

  ###############################################################################
  def _rename_directory(self, path_to_existing_dir, path_to_new_dir):
    # https://stackoverflow.com/questions/8735312/how-to-change-folder-names-in-python
    shutil.move(path_to_existing_dir, path_to_new_dir)

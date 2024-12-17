import mysql.connector

from .StorageBase import StorageBase

#################################################################################
class StorageMySQL(StorageBase):

  _init_path = '.'

  def __init__(self, secret_name=None, logger_name=None, objects_to_sync_logger_with=[]):
    super().__init__(constructor_kwargs=dict(secret_name=secret_name), 
                     logger_name=logger_name, 
                     objects_to_sync_logger_with=objects_to_sync_logger_with, 
                     connection_var_name=['_cnx', '_cursor'])

    secret_components = self._find_secret_components(4, secret_name=secret_name)
    
    self._connection_params = {what : secret_components[i] for i, what 
                              in enumerate(('host', 'database', 'user', 'password'))}


  ###############################################################################
  def _open(self):
    self._cnx = mysql.connector.connect(user='scott', database='employees')
    self._cursor = self._cnx.cursor()
    return self

  ###############################################################################
  def _get_filenames_and_directories(self, path: str):

    return all_files, all_directories

  ###############################################################################
  def _delete_file(self, filename):
    pass

  ###############################################################################
  def _delete_directory(self, path):
    pass

  ###############################################################################
  def _read_file(self, path, length=None):
    pass

  ###############################################################################
  def _create_file_given_content(self, path, content):
    pass

  ###############################################################################
  def _create_directory_only(self, path):
    pass

  ###############################################################################
  def _rename_file(self, path_to_existing_file, path_to_new_file):
    pass

  ###############################################################################
  def _rename_directory(self, path_to_existing_dir, path_to_new_dir):
    pass

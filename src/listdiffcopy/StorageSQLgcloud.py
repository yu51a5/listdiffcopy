import os
import pandas
import pandas_gbq
from google.cloud import bigquery
from google.oauth2 import service_account

from .StorageBase import StorageBase

#################################################################################
class StorageMySQL(StorageBase):

  _init_path = '.'

  def __init__(self, secret_name=None, logger_name=None, objects_to_sync_logger_with=[]):
    super().__init__(constructor_kwargs=dict(secret_name=secret_name), 
                     logger_name=logger_name, 
                     objects_to_sync_logger_with=objects_to_sync_logger_with, 
                     connection_var_name=['_client'])

    secret_components = self._find_secret_components(1, secret_name=secret_name)
    credentials_dict = eval("{" + secret_components[0] +"}")

    self._credentials = service_account.Credentials.from_service_account_info(credentials_dict)

  ###############################################################################
  def _open(self):
    self._client = bigquery.Client(credentials=self._credentials, 
                                   project=self._credentials.project_id)
    return self

  ###############################################################################
  def _get_filenames_and_directories(self, path: str):

    pass

  ###############################################################################
  def _delete_file(self, filename):
    pass

  ###############################################################################
  def _delete_directory(self, path):
    pass

  ###############################################################################
  def _read_file(self, path):
    query_job = self._get_connection_var().query("SELECT " + path)
    df = query_job.to_dataframe()
    return df

  ###############################################################################
  def _create_file_given_content(self, path, content, if_exists='replace'):
    pandas_gbq.to_gbq(content, path, 
                      self.credentials.project_id, 
                      credentials=self.credentials, if_exists=if_exists)

  ###############################################################################
  def _create_directory_only(self, path):
    pass

  ###############################################################################
  def _rename_file(self, path_to_existing_file, path_to_new_file):
    pass

  ###############################################################################
  def _rename_directory(self, path_to_existing_dir, path_to_new_dir):
    pass

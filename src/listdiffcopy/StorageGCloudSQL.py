import os
import pandas
import pandas_gbq
from google.cloud import bigquery
from google.oauth2 import service_account

from .LoggerObj import FDStatus
from .StorageBase import StorageBase

#################################################################################
class StorageGCloudSQL(StorageBase):

  _init_path = '.'

  def __init__(self, secret_name=None, logger_name=None, objects_to_sync_logger_with=[]):
    super().__init__(constructor_kwargs=dict(secret_name=secret_name), 
                     logger_name=logger_name, 
                     objects_to_sync_logger_with=objects_to_sync_logger_with
                     #, connection_var_name=['_client']
                    )

    secret_components = self._find_secret_components(1, secret_name=secret_name)
    credentials_dict = eval("{" + secret_components[0] +"}")

    self._credentials = service_account.Credentials.from_service_account_info(credentials_dict)
    pandas_gbq.context.credentials = self._credentials
    pandas_gbq.context.project = self._credentials.project_id

  ###############################################################################
  #def _open(self):
    #self._client = bigquery.Client(credentials=self._credentials, 
    #                               project=self._credentials.project_id)
    # return self
  ###############################################################################
  def _read_file(self, path):
    df = pandas_gbq.read_gbq("SELECT " + path, 
                             project_id=self._credentials.project_id, 
                             progress_bar_type=None)
    return df

  ###############################################################################
  def _create_file_given_content(self, path, content, if_exists='append'):
    # python-bigquery-pandas/pandas_gbq/gbq.py
    if if_exists not in ('fail', 'replace', 'append'):
      self.log_error(f"if_exists must be one of ('fail', 'replace', 'append'), not {if_exists}")
      return FDStatus.Error
    pandas_gbq.to_gbq(content, path, 
                      self._credentials.project_id, 
                      credentials=self._credentials, if_exists=if_exists)

  ###############################################################################
  def _get_filenames_and_directories(self, path: str):
    return [], []
    
  #def _delete_file(self, filename)
  #def _delete_directory(self, path)
  #def _read_file(self, path, length=None)
  #def _create_file_given_content(self, path, content):
  #def _create_directory_only(self, path)
  #def _rename_file(self, path_to_existing_file, path_to_new_file)
  #def _rename_directory(self, path_to_existing_dir, path_to_new_dir)

import mysql.connector

from listdiffcopy.StorageBase import StorageBase

#################################################################################
class StorageMySQL(StorageBase):

  _init_path = '.'

  def __init__(self, secret_name=None, logger_name=None, objects_to_sync_logger_with=[]):
    super().__init__(constructor_kwargs=dict(secret_name=secret_name), logger_name=logger_name, objects_to_sync_logger_with=objects_to_sync_logger_with, connection_var_name=['_mydb_connect'])

    secret_components = self._find_secret_components((3, 4), secret_name=secret_name)

    mydb = mysql.connector.connect(
      host="localhost",
      user="yourusername",
      password="yourpassword",
      database="mydatabase"
    )
    
    self.ssh_client_params = {what : secret_components[i] for i, what in enumerate(('hostname', 'port', 'username', 'password'))}

    if len(secret_components) == 5:
      # https://stackoverflow.com/questions/9963391/how-do-use-paramiko-rsakey-from-private-key
      # needed to ensure that `\n`s are in the right place
      private_key__ = io.StringIO()
      private_key__.write(f"""-----BEGIN OPENSSH PRIVATE KEY-----
                         {secret_components[-1]}==
                         -----END OPENSSH PRIVATE KEY-----""")
      private_key__.seek(0)
      self.ssh_client_params['pkey'] = paramiko.RSAKey.from_private_key(
        private_key__, self.ssh_client_params['password'])
      del self.ssh_client_params['password']

  ###############################################################################
  def _open(self):
    self._ssh_client = paramiko.SSHClient()
    # AutoAddPolicy explained in --> https://www.linode.com/docs/guides/use-paramiko-python-to-ssh-into-a-server/
    self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self._ssh_client.connect(**self.ssh_client_params)
    self._sftp_client = self._ssh_client.open_sftp()
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

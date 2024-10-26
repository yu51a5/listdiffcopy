import io
import os
import paramiko
from stat import S_ISDIR, S_ISREG

from listdiffcopy.StorageBase import StorageBase

#################################################################################
class StorageSFTP(StorageBase):

  _init_path = '.'

  def __init__(self, secret_name=None, logger_name=None, objects_to_sync_logger_with=[]):
    super().__init__(constructor_kwargs=dict(secret_name=secret_name), logger_name=logger_name, objects_to_sync_logger_with=objects_to_sync_logger_with, connection_var_name=['_ssh_client', '_sftp_client'])
    
    secret_components = self._find_secret_components((4, 5), secret_name=secret_name)
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
    
    contents = self._get_connection_var().listdir_attr(path)

    all_files, all_directories = [], []
    for entry in contents:
      path_ = os.path.join(path, entry.filename)
      mode = entry.st_mode
      if S_ISDIR(mode):
        all_directories.append(path_)
      if S_ISREG(mode):
        all_files.append(path_)
    return all_files, all_directories
    
  ###############################################################################
  def _delete_file(self, filename):
    self._get_connection_var().remove(filename)

  ###############################################################################
  def _delete_directory(self, path):
    self._delete_directory_contents(path=path)
    self._get_connection_var().rmdir(path)

  ###############################################################################
  def _fetch_file_size_efficiently(self, path):
    result_raw = self._get_connection_var().stat(path)
    result = result_raw.st_size #, 'modified' : result_raw.st_mtime
    return result

  ###############################################################################
  def _read_file(self, path, length=None):
    with self._get_connection_var().open(path) as sftp_file:
      sftp_contents = sftp_file.read(size=length)
    return sftp_contents

  ###############################################################################
  def file_contents_is_text(self, path):
    with self._get_connection_var().open(path) as sftp_file:
      sftp_contents = sftp_file.read(size=2048)
      result = StorageBase._file_contents_is_text(file_beginning=sftp_contents)
      return result
    
  ###############################################################################
  def _create_file_given_content(self, path, content):
    _content = io.BytesIO(content) if isinstance(content, bytes) else io.BytesIO(content.encode())
    self._get_connection_var().putfo(_content, path)

  ###############################################################################
  def _create_directory_only(self, path):
    self._get_connection_var().mkdir(path)

  ###############################################################################
  def _rename_file(self, path_to_existing_file, path_to_new_file):
    self._get_connection_var().rename(path_to_existing_file, path_to_new_file)
    
  ###############################################################################
  def _rename_directory(self, path_to_existing_dir, path_to_new_dir):
    self._get_connection_var().rename(path_to_existing_dir, path_to_new_dir)
      
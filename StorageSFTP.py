import io
import os
import paramiko
from stat import S_ISDIR, S_ISREG
from StorageBase import StorageBase


#################################################################################
class StorageSFTP(StorageBase):

  def __init__(self,
               hostname=None,
               port=None,
               username=None,
               password=None,
               private_key=None):
    super().__init__(name='SFTP')
    self.ssh_client_params = dict(hostname=hostname,
                                  port=port,
                                  username=username,
                                  password=password)
    for what in ('hostname', 'port', 'username', 'password'):
      if not self.ssh_client_params[what]:
        self.ssh_client_params[what] = os.getenv(f'sftp_{what}')

    not_defined_errors = [
      what for what in ('hostname', 'port', 'username', 'password')
      if not self.ssh_client_params[what]
    ]
    if not_defined_errors:
      raise Exception(", ".join(not_defined_errors) + " are not defined")

    if not private_key:
      private_key = os.getenv("sftp_private_key")
    if private_key:
      # https://stackoverflow.com/questions/9963391/how-do-use-paramiko-rsakey-from-private-key
      # needed to ensure that `\n`s are in the right place
      private_key__ = io.StringIO()
      private_key__.write(f"""-----BEGIN OPENSSH PRIVATE KEY-----
                         {private_key}==
                         -----END OPENSSH PRIVATE KEY-----""")
      private_key__.seek(0)
      self.ssh_client_params['pkey'] = paramiko.RSAKey.from_private_key(
        private_key__, self.ssh_client_params['password'])
      del self.ssh_client_params['password']

  ###############################################################################
  def __enter__(self):
    self.ssh_client = paramiko.SSHClient()
    # AutoAddPolicy explained in --> https://www.linode.com/docs/guides/use-paramiko-python-to-ssh-into-a-server/
    self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.ssh_client.connect(**self.ssh_client_params)
    self.sftp_client = self.ssh_client.open_sftp()
    return self

  ###############################################################################
  def __exit__(self, type, value, traceback):
    self.sftp_client.close()
    self.ssh_client.close()

  ###############################################################################
  def _get_filenames_and_directories(self, folderid: int, recursive: bool,
                                                 path_so_far: str):
    contents = self.sftp_client.listdir_attr(path_so_far)

    all_files, all_directories = [], {}
    for entry in contents:
      path = os.path.join(path_so_far, entry.filename)
      mode = entry.st_mode
      if S_ISDIR(mode):
        all_directories[path] = self._get_filenames_and_directories(
          None, True, path) if recursive else None
      if S_ISREG(mode):
        all_files.append(path)

    return all_files, all_directories

  ###############################################################################
  def _delete_file(self, filename):
    self.sftp_client.remove(filename)

  ###############################################################################
  def _delete_directory(self, dirname):
    self.sftp_client.rmdir(dirname)

  ###############################################################################
  def get_stats(self, filename):
    result = self.sftp_client.stat(filename)
    return result

  ###############################################################################
  def get_init_path(self):
    return '.'

  ###############################################################################
  def get_contents(self, filename):
    with self.sftp_client.open(filename) as sftp_file:
      sftp_contents = sftp_file.read()
    return sftp_contents

  ###############################################################################
  def _create_file_given_content(self, filename, content):
    self._update_file_given_content(filename=filename, content=content)

  ###############################################################################
  def _update_file_given_content(self, filename, content):
    self.sftp_client.putfo(io.BytesIO(content.encode()), filename)
  
  ###############################################################################
  def compare_and_update_a_file(self, my_filename, another_source, another_source_filename):

    compare_stats, comp_result = self._file_stats_are_comparable_and_same(
          my_filename=my_filename, another_source=another_source, another_source_filename=another_source_filename)
    if comp_result:
        return
      
    another_contents = another_source.get_contents(another_source_filename)
                                  
    if not compare_stats:
      with self.sftp_client.open(my_filename) as sftp_file:
        sftp_contents = sftp_file.read()
        if another_contents != sftp_contents:
          return

    self.update_file_given_content(filename=my_filename, content=another_contents)


  ###############################################################################
  def _update_file_in_another_source(self, my_filename, another_source,
                                     another_source_filename):
    compare_stats, comp_result = self._file_stats_are_comparable_and_same(
          my_filename=my_filename, another_source=another_source, another_source_filename=another_source_filename)
    if comp_result:
        return
    with self.sftp_client.open(my_filename) as sftp_file:
      sftp_contents = sftp_file.read()
      if compare_stats or (another_source.get_contents(another_source_filename) != sftp_contents):
        another_source.update_file_given_content(filename=another_source_filename, content=sftp_contents)

  ###############################################################################
  def _create_directory(self, dirname):
    self.sftp_client.mkdir(dirname)

  ###############################################################################
  def _create_a_file_in_another_source(self, my_filename, another_source, another_source_filename):
    with self.sftp_client.open(my_filename) as sftp_file:
      sftp_contents = sftp_file.read()
      another_source.create_file_given_content(filename=another_source_filename, content=sftp_contents)
      
import io 
import os 
import paramiko
from stat import S_ISDIR, S_ISREG
from StorageBase import StorageBase

#################################################################################
class StorageSFTP(StorageBase):
  def __init__(self, hostname=None, port=None, username=None, password=None, private_key=None):
    super().__init__(name='SFTP')
    self.ssh_client_params = dict(hostname=hostname, port=port, username=username, password=password)
    for what in ('hostname', 'port', 'username', 'password'):
      if not self.ssh_client_params[what]:
        self.ssh_client_params[what] = os.getenv(f'sftp_{what}')
  
    not_defined_errors = [what for what in ('hostname', 'port', 'username', 'password') if not self.ssh_client_params[what]]
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
      self.ssh_client_params['pkey'] = paramiko.RSAKey.from_private_key(private_key__, ssh_client_params['password'])
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
  def _get_filenames_and_directories(self, root: str):  
    files, directories = [], {}
    for entry in self.sftp_client.listdir_attr(self):
      path = os.path.join(self, entry.filename)
      mode = entry.st_mode
      if S_ISDIR(mode):
        directories[path] = self.get_contents_of_an_sftp_directory(root=path)
      if S_ISREG(mode):
        files.append(path)
    return files, directories

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
  def compare_and_update_a_file(self, another_source, another_source_filename, my_filename):
    if another_source.compare_stats_not_content():
      if self.get_stats(full_path_1) == another_source.stats(another_source_filename):
        return
        
    another_contents = another_source.get_contents(another_source_filename)
    
    if not another_source.compare_stats_not_content():
      with self.sftp_client.open(my_filename) as sftp_file:
        sftp_contents = sftp_file.read() 
        if another_contents != sftp_contents:
          return
          
    self.sftp_client.putfo(BytesIO(another_contents.encode()), my_filename)

  ###############################################################################
  def _compare_and_update_a_file_in_another_source(self, my_filename, another_source, another_source_filename):
    if another_source.compare_stats_not_content():
      if self.get_stats(my_filename) == another_source.stats(another_source_filename):
        return
    with self.sftp_client.open(my_filename) as sftp_file:
      sftp_contents = sftp_file.read() 
      if another_source.compare_stats_not_content() 
           or (another_source.get_contents(another_source_filename) != sftp_contents):
        another_source.update_file(another_source_filename, content=sftp_contents)
        print('updated ' + another_source_filename)
          
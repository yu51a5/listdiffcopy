import io
import os
import paramiko
from stat import S_ISDIR, S_ISREG

from StorageBase import StorageBase
from settings import wp_images_extensions, default_ignore_wp_scaled_images

#################################################################################
class StorageSFTP(StorageBase):

  def __init__(self, secret_name=None, ignore_wp_scaled_images=default_ignore_wp_scaled_images):
    super().__init__()
    self.ignore_wp_scaled_images = ignore_wp_scaled_images

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
    self.ssh_client = paramiko.SSHClient()
    # AutoAddPolicy explained in --> https://www.linode.com/docs/guides/use-paramiko-python-to-ssh-into-a-server/
    self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.ssh_client.connect(**self.ssh_client_params)
    self.sftp_client = self.ssh_client.open_sftp()
    return self

  ###############################################################################
  def _close(self):
    self.sftp_client.close()
    self.ssh_client.close()

  ###############################################################################
  def _get_filenames_and_directories(self, path_so_far: str):
    
    contents = self.sftp_client.listdir_attr(path_so_far)

    all_files, all_directories = [], []
    for entry in contents:
      path = os.path.join(path_so_far, entry.filename)
      mode = entry.st_mode
      if S_ISDIR(mode):
        all_directories.append(path)
      if S_ISREG(mode):
        all_files.append(path)

    return all_files, all_directories

  ###############################################################################
  def _filter_out_files(self, files_):
    
    if not self.ignore_wp_scaled_images:
      return files_
      
    qty_files = len(files_)
    i = 0
    while i < qty_files:
      this_file_name = files_[i]
      i += 1 # as if it's already the next iteration
      pos = {c : this_file_name.rfind(c) for c in ('.', 'x', '-')}
      if min(pos.values()) < 0:
        continue
      if not ((pos['-'] + 4) <= (pos['x'] + 2) <= pos['.']):
        continue
      maybe_numbers = this_file_name[pos['-'] + 1:pos['x']] + this_file_name[pos['x'] + 1:pos['.']]
      not_numbers = [c for c in maybe_numbers if not ('0' <= c <= '9')]
      if not_numbers:
        continue
      extension = (this_file_name[pos['.']+1:]).lower() 
      if extension not in wp_images_extensions:
        continue
      presumed_original = this_file_name[:pos['-']] + this_file_name[pos['.']:]
      for j in range(i, qty_files):
        if files_[j] == presumed_original:
          qty_files -= 1
          i -= 1 #rolling back
          files_.pop(i)
          break
        if files_[j] > presumed_original:
          break

    return files_
    
  ###############################################################################
  def _delete_file(self, filename):
    self.sftp_client.remove(filename)

  ###############################################################################
  def _delete_directory(self, dirname):
    self.sftp_client.rmdir(dirname)

  ###############################################################################
  def _fetch_file_size(self, filename):
    result_raw = self.sftp_client.stat(filename)
    result = result_raw.st_size #, 'modified' : result_raw.st_mtime
    return result

  ###############################################################################
  def get_init_path(self):
    return '.'

  ###############################################################################
  def get_contents(self, filename, length=None):
    with self.sftp_client.open(filename) as sftp_file:
      sftp_contents = sftp_file.read(size=length)
    return sftp_contents

  ###############################################################################
  def file_contents_is_text(self, filename):
    with self.sftp_client.open(filename) as sftp_file:
      sftp_contents = sftp_file.read(size=2048)
      result = StorageBase._file_contents_is_text(file_beginning=sftp_contents)
      return result
    
  ###############################################################################
  def _create_file_given_content(self, filename, content):
    self._update_file_given_content(filename=filename, content=content)

  ###############################################################################
  def _update_file_given_content(self, filename, content):
    self.sftp_client.putfo(io.BytesIO(content.encode()), filename)

  ###############################################################################
  def _create_directory(self, dirname):
    self.sftp_client.mkdir(dirname)

  ###############################################################################
  def _create_file_in_another_source(self, my_filename, source, source_filename):
    with self.sftp_client.open(my_filename) as sftp_file:
      sftp_contents = sftp_file.read()
      source._create_file_given_content(filename=source_filename, content=sftp_contents)
      return len(sftp_contents)

  ###############################################################################
  def _rename_file(self, path_to_existing_file, path_to_new_file):
    self.sftp_client.rename(path_to_existing_file, path_to_new_file)
    
  ###############################################################################
  def _rename_directory(self, path_to_existing_dir, path_to_new_dir):
    self.sftp_client.rename(path_to_existing_dir, path_to_new_dir)
      
import os
import requests
import requests.packages.urllib3.contrib
# installed using pip install urllib3==1.26.15 requests-toolbelt==0.10.1
# https://stackoverflow.com/questions/76175487
from requests_toolbelt.multipart.encoder import MultipartEncoder

from StorageBase import StorageBase

#################################################################################
# pCloud
#################################################################################
class StoragePCloud(StorageBase):

  ###############################################################################
  # Use eapi if the server is in Europe
  # For Pcloud token, see
  def __init__(self):
    super().__init__()

  ###############################################################################
  def __enter__(self):
    return self

  ###############################################################################
  def __exit__(self, type, value, traceback):
    pass

  ###############################################################################
  def _get_filenames_and_directories(self, path_so_far : str):
    contents_ = self.__post_folderid(url_addon='listfolder', dirname=path_so_far)['metadata']['contents']
    files_, directories_ = [], []
    for c in contents_:
      full_name = os.path.join(path_so_far, c['name'])
      if c['isfolder']:
        self.set_dir_info(full_name, {'id' : c['folderid']})
        directories_.append(full_name)
      else:
        files_.append(full_name)
        self.set_file_info(full_name, {'id' : c['fileid']})

    return files_, directories_

###############################################################################
  def get_contents(self, filename, length=None):
    contents_ = self.wrapper_with_id(filename=filename, func=self.__get_contents_inner, length=length)
    return contents_

  ###############################################################################
  def _delete_file(self, filename):
    self.__post_fileid(url_addon='deletefile', filename=filename)

  ###############################################################################
  def _delete_directory(self, dirname):
    self.__post_folderid(url_addon='deletefolderrecursive', dirname=dirname)

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
    response = self.__post_fileid(url_addon='stat', filename=filename)
    metadata = response['metadata']
    result = metadata['size']
    # 'modified' : datetime.strptime(metadata['modified'], '%a, %d %b %Y %H:%M:%S +0000')
    return  result

  ###############################################################################
  # using https://docs.pcloud.com/methods/file/renamefile.html
  def _rename_file(self, path_to_existing_file, path_to_new_file):
    param_dict = {'tofolderid' : self.get_dir_info(os.path.dirname(path_to_new_file), 'id'),
                  'toname' : os.path.basename(path_to_new_file)}
    result = self.__post_fileid(url_addon='renamefile', 
                                filename=path_to_existing_file, 
                                param_dict=param_dict)
    return result['metadata']

  ###############################################################################
  def _rename_directory(self, path_to_existing_dir, path_to_new_dir):
    param_dict = {'tofolderid' : self.get_dir_info(os.path.dirname(path_to_new_file), 'id'),
                  'toname' : os.path.basename(path_to_new_dir)}
    result = self.__post_folderid(url_addon='renamefolder', 
                                  dirname=path_to_existing_dir,
                                  param_dict=param_dict)
    return result['metadata']

import os
import requests
from StorageBase import StorageBase

#################################################################################
# pCloud
#################################################################################
class StoragePCloud(StorageBase):

  base_url = ['https://api.pcloud.com/', 'https://eapi.pcloud.com/']

  ###############################################################################
  # Use eapi if the server is in Europe
  # For Pcloud token, see
  def __init__(self, is_eapi, token=None):
    super().__init__(name='pCloud')
    self.token = os.environ['pcloud_token'] if token is None else token
    self.url = StoragePCloud.base_url[is_eapi]

  ###############################################################################
  def __enter__(self):
    self.requests_session = requests.Session()
    return self

  ###############################################################################
  def __exit__(self, type, value, traceback):
    self.requests_session.close()

  ###############################################################################
  def __post(self, url_addon, param_dict={}):
    url = f'{self.url}{url_addon}?access_token={self.token}&' + '&'.join(f'{key}={str(value).replace(" ", "%20")}' for key, value in param_dict.items())
    response = self.requests_session.post(url)
    content_type = response.headers["content-type"].strip()

    if 'application/json' in content_type:
      result = response.json()
    elif 'application/octet-stream' in content_type:
      result = response.content
    else:
      raise Exception(f'Cannot process response which type is {content_type}')
      
    return result
    
  ###############################################################################
  # filenames and their sha's are needed to be able to update existing files, see
  # https://stackoverflow.com/questions/63435987/python-pygithub-if-file-exists-then-update-else-create
  ###############################################################################
  def _get_filenames_and_directories(self, folderid : int, recursive : bool, path_so_far : str):
    contents_ = self.__post(url_addon='listfolder', param_dict=dict(folderid=folderid))['metadata']['contents']
    files_, directories_ = {}, {}
    for c in contents_:
      full_name = os.path.join(path_so_far, c['name'])
      if not c['isfolder']:
        files_[full_name] = c['fileid'] 
      else:
        directories_[full_name] = c['folderid'] if not recursive \
                      else self._get_filenames_and_directories(folderid=c['folderid'], recursive=True, path_so_far=full_name)
        
    return files_, directories_
  
###############################################################################
  def get_contents(self, filename):
    print('started')
    c = self.__post(url_addon='file_open', param_dict=dict(path='/'+filename, flags=64))#['metadata']['contents']
    size_ = self.__post(url_addon='file_size', param_dict=dict(fd=c['fd']))['size']
    contents_ = self.__post(url_addon='file_read', param_dict=dict(fd=c['fd'], count=size_))
    self.__post(url_addon='file_close', param_dict=dict(fd=c['fd']))
    print('get_contents')
    return contents_

###############################################################################

###############################################################################

    
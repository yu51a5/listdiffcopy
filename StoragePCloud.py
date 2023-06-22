import io
import os
import requests
from StorageBase import StorageBase

requests_session = requests.Session()

#################################################################################
# pCloud. Use eapi if the server is in Europe
###############################################################################
class StoragePCloud(StorageBase):

  base_url = ['https://api.pcloud.com/', 'https://eapi.pcloud.com/']

  def _post(self, url_addon, param_dict={}):
    url = f'{self.url}{url_addon}?access_token={self.token}&' + '&'.join(f'{key}={value}' for key, value in param_dict.items())
    result = requests_session.post(url).json()
    return result

  ###############################################################################
  # For Github token, see
  # https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
  def __init__(self, is_eapi, token=None):
    super().__init__(name='pCloud')
    self.token = os.environ['pcloud_token'] if token is None else token
    self.url = StoragePCloud.base_url[is_eapi]

  ###############################################################################
  # filenames and their sha's are needed to be able to update existing files, see
  # https://stackoverflow.com/questions/63435987/python-pygithub-if-file-exists-then-update-else-create
  ###############################################################################
  def __get_filenames_and_directories(self, folderid : int, recursive : bool, path_so_far : str):
    contents_ = self._post(url_addon='listfolder', param_dict=dict(folderid=folderid))['metadata']['contents']
    files_, directories_ = {}, {}
    for c in contents_:
      full_name = os.path.join(path_so_far, c['name'])
      if not c['isfolder']:
        files_[full_name] = c['fileid'] 
      else:
        directories_[full_name] = c['folderid'] if not recursive \
                      else self.__get_filenames_and_directories(folderid=c['folderid'], recursive=True, path_so_far=full_name)
        
    return files_, directories_
    
  def _get_filenames_and_directories(self, directory: str):
    
    head = directory
    root_folders = []
    while head:
      head, tail = os.path.split(head)
      root_folders = [tail] + root_folders

    folderid = 0
    path_so_far = ''
    for rf in root_folders:
      _, directories_ = self.__get_filenames_and_directories(folderid=folderid, recursive=False, path_so_far=path_so_far)
      if rf not in directories_:
        return [], []
      folderid = directories_[rf]
      path_so_far = os.path.join(path_so_far, rf)
        
    files_, directories_ = self.__get_filenames_and_directories(folderid=folderid, recursive=True, path_so_far=directory)

    return files_, directories_ 
    

  
###############################################################################
  def get_stats(self, filename):
    files = {'01 - Border Reiver.mp3': open('d:\MUSIC\Get Lucky\01 - Border Reiver.mp3', 'rb')}
    result = self._post(url_add_on='listfolder', param_dict={'folderid'})
    return result


###############################################################################
  def upload_to_pCloud(self, full_filename):
    files = {'01 - Border Reiver.mp3': open('d:\MUSIC\Get Lucky\01 - Border Reiver.mp3', 'rb')}
    post = requests_session.post('https://eapi.pcloud.com/uploadfile', files=files, data=self.auth)
    return post.json()
    
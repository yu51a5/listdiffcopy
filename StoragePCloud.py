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
    print((result['metadata']))
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
  def _get_filenames_and_directories(self, directory: str):
    
    head = directory
    root_folders = []
    while head:
      head, tail = os.path.split(head)
      root_folders = [tail] + root_folders

    folderid = 0

    path_so_far = ''
    for rf in root_folders:
      contents_ = self._post(url_addon='listfolder', param_dict=dict(folderid=folderid))['metadata']['contents']
      paths_next_level = {c['name'] : c['folderid'] for c in contents_ if c['isfolder']}
      print( paths_next_level )
      if rf not in paths_next_level:
        return [], []
      path_so_far = os.path.join(path_so_far, rf)
        
    contents = self.repo.get_contents(directory)
    all_files, all_directories = {}, {}
    while contents:
      content_item = contents.pop(0)
      if content_item.type == "dir":
        all_directories[content_item.name] = _self._get_filenames_and_directories(directory=content_item.path)
      else:
        all_files[content_item.name] = content_item.sha

    return all_files, all_directories 
    

  
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
    
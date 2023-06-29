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
  def _get_filenames_and_directories(self, recursive : bool, path_so_far : str):
    contents_ = self.__post(url_addon='listfolder', param_dict=dict(folderid=self.cached_directories_flat[path_so_far]))['metadata']['contents']
    files_, directories_ = [], {}
    for c in contents_:
      full_name = os.path.join(path_so_far, c['name'])
      if c['isfolder']:
        self.cached_directories_flat[full_name] = c['folderid']
        directories_[full_name] = None if not recursive \
                      else self._get_filenames_and_directories(recursive=True, path_so_far=full_name)
      else:
        files_.append(full_name)
        self.cached_filenames_flat[full_name] = c['fileid'] 
        
    return files_, directories_

###############################################################################
  def wrapper_with_id(self, filename, func, **kwargs):
    print('started')
    c = self.__post(url_addon='file_open', param_dict=dict(path='/'+filename, flags=64))#['metadata']['contents']
    result = func(id=c['fd'], **kwargs)
    self.__post(url_addon='file_close', param_dict=dict(fd=c['fd']))
    print('completed wrapper_with_id')
    return result
    
###############################################################################
  def __get_contents_inner(self, id, length=None):
    size_ = self.__post(url_addon='file_size', param_dict=dict(fd=id))['size']
    if length and size_ > length:
       size_ = length
    contents_ = self.__post(url_addon='file_read', param_dict=dict(fd=id, count=size_))
    return contents_
    
  def get_contents(self, filename, length=None):
    contents_ = self.wrapper_with_id(filename=filename, func=self.__get_contents_inner, length=length)
    return contents_

  ###############################################################################
  def _delete_file(self, filename):
    self.__post(url_addon='deletefile', param_dict=dict(fileid=self.cached_filenames_flat[filename]))
    
  ###############################################################################
  def _delete_directory(self, dirname):
    self.__post(url_addon='deletefolder', param_dict=dict(folderid=self.cached_directories_flat[dirname]))

  ###############################################################################
  def _create_directory(self, dirname):
    self.__post(url_addon='createfolder', param_dict=dict(folderid=self.cached_directories_flat[os.path.dirname(dirname)],  
                                                          name=os.path.basename(dirname)))

  ###############################################################################
  def _create_file_given_content(self, filename, content):
    self.__post(url_addon='file_write', param_dict=dict(fileid=self.cached_filenames_flat[filename]))
    
  ###############################################################################
  def _update_file_given_content(self, filename, content):
    self.__post(url_addon='file_write', param_dict=dict(fileid=self.cached_filenames_flat[filename]))

  ###############################################################################
  def get_stats(self, filename):
    result = self.__post(url_addon='stat', param_dict=dict(fileid=self.cached_filenames_flat[filename]))
    return result

###############################################################################

    
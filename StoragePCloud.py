import os
import requests
import requests.packages.urllib3.contrib
# installed using pip install urllib3==1.26.15 requests-toolbelt==0.10.1
# https://stackoverflow.com/questions/76175487
from requests_toolbelt.multipart.encoder import MultipartEncoder

from StorageBase import StorageBase
from settings import pcloud_urls_are_eapi

#################################################################################
# pCloud
#################################################################################
class StoragePCloud(StorageBase):

  base_url = ['https://api.pcloud.com/', 'https://eapi.pcloud.com/']

  ###############################################################################
  # Use eapi if the server is in Europe
  # For Pcloud token, see
  def __init__(self, is_eapi=pcloud_urls_are_eapi, secret_name=None):
    super().__init__()
    self.token = self._find_secret_components(1, secret_name=secret_name)[0]
    self.url = StoragePCloud.base_url[is_eapi]

  ###############################################################################
  def _open(self):
    self.requests_session = requests.Session()

  ###############################################################################
  def _close(self):
    self.requests_session.close()

  ###############################################################################
  def __post(self, url_addon, param_dict={}, files=None):

    if files:
      fields = [(str(k), str(v)) for k, v in param_dict.items()] + files
      m = MultipartEncoder(fields=fields)
      request_dict = dict(data=m, headers={"Content-Type": m.content_type, "Authorization" : f"Bearer {self.token}"})
    else:
      all_params = {'access_token' : self.token}
      all_params.update(param_dict)
      request_dict = dict(data=all_params)
      
    response = self.requests_session.post(self.url + url_addon, **request_dict)
    content_type = response.headers["content-type"].strip()

    if 'application/json' in content_type:
      result = response.json()
    elif 'application/octet-stream' in content_type:
      result = response.content
    else:
      raise Exception(f'Cannot process response which type is {content_type}')

    if isinstance(result, dict) and 'error' in result:
      raise Exception(f'{result["error"]} with {url_addon} and {param_dict}')
      
    return result

  #############################################################
  def __post_fileid(self, url_addon, filename, param_dict={}, files=None):
    param_dict['fileid'] = self.get_file_info(filename, 'id')
    return self.__post(url_addon=url_addon, param_dict=param_dict, files=files)

  def __post_folderid(self, url_addon, dirname, param_dict={}, files=None):
    param_dict['folderid'] = self.get_dir_info(dirname, 'id')
    return self.__post(url_addon=url_addon, param_dict=param_dict, files=files)
    
  ###############################################################################
  # filenames and their sha's are needed to be able to update existing files, see
  # https://stackoverflow.com/questions/63435987/python-pygithub-if-file-exists-then-update-else-create
  ###############################################################################  
  def _get_default_root_dir_info(self):
    return {'' : {'id' : 0}}
    
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
  def _wrapper_with_id(self, filename, func, **kwargs):
    c = self.__post(url_addon='file_open', param_dict=dict(path='/'+filename, flags=64))#['metadata']['contents']
    result = func(id=c['fd'], **kwargs)
    self.__post(url_addon='file_close', param_dict=dict(fd=c['fd']))
    return result
    
###############################################################################
  def __get_contents_inner(self, id, length=None):
    size_ = self.__post(url_addon='file_size', param_dict=dict(fd=id))['size']
    if length and size_ > length:
       size_ = length
    contents_ = self.__post(url_addon='file_read', param_dict=dict(fd=id, count=size_))
    return contents_
    
  def get_contents(self, filename, length=None):
    contents_ = self._wrapper_with_id(filename=filename, func=self.__get_contents_inner, length=length)
    return contents_

  ###############################################################################
  def _delete_file(self, filename):
    self.__post_fileid(url_addon='deletefile', filename=filename)
    
  ###############################################################################
  def _delete_directory(self, dirname):
    self.__post_folderid(url_addon='deletefolderrecursive', dirname=dirname)

  ###############################################################################
  def _create_directory(self, dirname):
    result = self.__post_folderid(url_addon='createfolder', 
                                  dirname=os.path.dirname(dirname),
                                  param_dict={'name' : os.path.basename(dirname)})
    return {'id' : result["metadata"]["folderid"]}

  ###############################################################################
  def _create_file_given_content(self, filename, content):

    files = [("file", (os.path.basename(filename), content), )] 
    
    result = self.__post_folderid(url_addon='uploadfile', 
                                   dirname=os.path.dirname(filename), 
                                   param_dict={'filename' : os.path.basename(filename)}, 
                                   files=files)
    self.set_file_info(filename, {'id' : result["fileids"][0]})
    
  ###############################################################################
  def _update_file_given_content(self, filename, content):
    self.__post_fileid(url_addon='file_write', filename=filename)

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

import os
import requests
import requests.packages.urllib3.contrib
# installed using pip install urllib3==1.26.15 requests-toolbelt==0.10.1
# https://stackoverflow.com/questions/76175487
from requests_toolbelt.multipart.encoder import MultipartEncoder

from listdiffcopy.StorageBase import StorageBase
from listdiffcopy.settings import pcloud_urls_are_eapi

#################################################################################
# pCloud
#################################################################################
class StoragePCloud(StorageBase):

  base_url = ['https://api.pcloud.com/', 'https://eapi.pcloud.com/']

  ###############################################################################
  # Use eapi if the server is in Europe
  # For Pcloud token, see
  def __init__(self, is_eapi=pcloud_urls_are_eapi, secret_name=None, logger_name=None, objects_to_sync_logger_with=[]):
    super().__init__(constructor_kwargs=dict(is_eapi=is_eapi, secret_name=secret_name), logger_name=logger_name, objects_to_sync_logger_with=objects_to_sync_logger_with, connection_var_name='_requests_session')
    self.token = self._find_secret_components(1, secret_name=secret_name)[0]
    self.url = StoragePCloud.base_url[is_eapi]

  ###############################################################################
  def _open(self):
    self._requests_session = requests.Session()

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
      
    response = self._get_connection_var().post(self.url + url_addon, **request_dict)
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
    param_dict['fileid'] = self._get_file_id(filename)
    if param_dict['fileid'] is None:
      return
    return self.__post(url_addon=url_addon, param_dict=param_dict, files=files)

  def __post_folderid(self, url_addon, dirname, param_dict={}, files=None):
    param_dict['folderid'] = self._get_dir_id(dirname)
    if param_dict['folderid'] is None:
      return
    return self.__post(url_addon=url_addon, param_dict=param_dict, files=files)
    
  ###############################################################################
  # filenames and their id's are needed to be able to update existing files, see
  ###############################################################################
  def __get_id(self, name, isfolder, id_name):
    if not name:
      return 0, None
    basename = os.path.basename(name)
    parent_dirname = os.path.dirname(name)
      
    contents_ = self.__post_folderid(url_addon='listfolder', dirname=parent_dirname)['metadata']['contents']
    for c in contents_:
      if (c['isfolder'] == isfolder) and c['name'] == basename:
        return c[id_name], None
    return None, name

  def _get_dir_id(self, name):
    result, whats_broken = self.__get_id(name=name, isfolder=True, id_name='folderid')
    if result is None:
      raise Exception(f'Directory {whats_broken} is not found')
    return result

  def _get_file_id(self, name):
    result, whats_broken = self.__get_id(name=name, isfolder=False, id_name='fileid')
    if result is None:
      raise Exception (f'File {whats_broken} is not found')
    return result
  
  ###############################################################################
  def _get_filenames_and_directories(self, path : str):
    contents_ = self.__post_folderid(url_addon='listfolder', dirname=path)['metadata']['contents']
    files_, directories_ = [], []
    for c in contents_:
      full_name = os.path.join(path, c['name'])
      if c['isfolder']:
        #self.set_dir_info(full_name, {'id' : c['folderid']})
        directories_.append(full_name)
      else:
        files_.append(full_name)
        #self.set_file_info(full_name, {'id' : c['fileid']})
        
    return files_, directories_

###############################################################################
  def _wrapper_with_id(self, filename, func, **kwargs):
    c = self.__post(url_addon='file_open', param_dict=dict(path='/'+filename, flags=64))#['metadata']['contents']
    result = func(id=c['fd'], **kwargs)
    self.__post(url_addon='file_close', param_dict=dict(fd=c['fd']))
    return result
    
###############################################################################
  def __get_content_inner(self, id, length=None):
    size_ = self.__post(url_addon='file_size', param_dict=dict(fd=id))['size']
    if length and size_ > length:
       size_ = length
    contents_ = self.__post(url_addon='file_read', param_dict=dict(fd=id, count=size_))
    return contents_
    
  def _read_file(self, path, length=None):
    contents_ = self._wrapper_with_id(filename=path, func=self.__get_content_inner, length=length)
    return contents_

  ###############################################################################
  def _delete_file(self, filename):
    self.__post_fileid(url_addon='deletefile', filename=filename)
    
  ###############################################################################
  def _delete_directory(self, path):
    self.__post_folderid(url_addon='deletefolderrecursive', dirname=path)

  ###############################################################################
  def _create_directory_only(self, path):
    result = self.__post_folderid(url_addon='createfolder', 
                                  dirname=os.path.dirname(path),
                                  param_dict={'name' : os.path.basename(path)})
    return {'id' : result["metadata"]["folderid"]}

  ###############################################################################
  def _create_file_given_content(self, path, content):

    files = [("file", (os.path.basename(path), content), )] 
    
    result = self.__post_folderid(url_addon='uploadfile', 
                                   dirname=os.path.dirname(path), 
                                   param_dict={'filename' : os.path.basename(path)}, 
                                   files=files)
    # self.set_file_info(filename, {'id' : result["fileids"][0]})
    #self.__post_fileid(url_addon='file_write', filename=filename)

  ###############################################################################
  def _fetch_file_size_efficiently(self, path):
    response = self.__post_fileid(url_addon='stat', filename=path)
    metadata = response['metadata']
    result = metadata['size']
    # 'modified' : datetime.strptime(metadata['modified'], '%a, %d %b %Y %H:%M:%S +0000')
    return  result

  ###############################################################################
  # using https://docs.pcloud.com/methods/file/renamefile.html
  def _rename_file(self, path_to_existing_file, path_to_new_file):
    param_dict = {'tofolderid' : self._get_dir_id(os.path.dirname(path_to_new_file)),
                  'toname' : os.path.basename(path_to_new_file)}
    result = self.__post_fileid(url_addon='renamefile', 
                                filename=path_to_existing_file, 
                                param_dict=param_dict)
    return result['metadata']
    
  ###############################################################################
  def _rename_directory(self, path_to_existing_dir, path_to_new_dir):
    param_dict = {'tofolderid' : self._get_dir_id(os.path.dirname(path_to_new_dir)),
                  'toname' : os.path.basename(path_to_new_dir)}
    result = self.__post_folderid(url_addon='renamefolder', 
                                  dirname=path_to_existing_dir,
                                  param_dict=param_dict)
    return result['metadata']

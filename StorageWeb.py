import os
import requests

from utils import remove_duplicates
from StorageBase import StorageBase

#################################################################################
class StorageWeb(StorageBase):

  __fake_directories = [{}, [], []]
  __fake_files = {}
  __name_content_type_is_content = {}
    
  ###############################################################################
  def __init__(self, logger_name=None, objects_to_sync_logger_with=[]):
    super().__init__(constructor_kwargs={}, logger_name=logger_name, objects_to_sync_logger_with=objects_to_sync_logger_with)

  ###############################################################################
  def get_response_code(url):
    with requests.get(url) as response:
      return response.status_code

  ###############################################################################
  def check_urls(self, urls, print_ok=False):
    by_resp_code = {}
    for url, pages_where_referenced in urls.items():
      try:
        response_code = StorageWeb.get_response_code(url)
      except:
        response_code = 418
      if response_code in by_resp_code:
        by_resp_code[response_code].append([url, pages_where_referenced])
      else:
        by_resp_code[response_code] = [[url, pages_where_referenced]]

    for code, urls_pages in by_resp_code.items():
      if code == 200:
        if print_ok:
          self.log_info("OK URL:\n" + "\n".join([u for u, p in urls_pages]))
      elif code == 403:
        self.log_warning("URL that cannot be automatically checked (code 403):\n" + "\n".join([("\n" + u + ": this URL is referenced in:\n" + "\n".join(p)) for u, p in urls_pages]))
      else:
        self.log_error(f"URL check failed (code {code}):\n" + "\n".join([("\n" + u + ": this URL is referenced in:\n" + "\n".join(p)) for u, p in urls_pages]))
    
  ###############################################################################
  def get_contents(self, filename, length=None, use_content_not_text=None): # filename is url
    if filename in StorageWeb.__fake_files:
      return StorageWeb.__fake_files[filename]
    with requests.get(filename) as response:
      if response.status_code == 200:
        use_content = use_content_not_text if use_content_not_text is not None else StorageWeb.__name_content_type_is_content[filename]
        return response.content if use_content else (response.text[:length] if length else response.text)
      else:
        self.log_error(f'Downloading of {filename} failed, code {response.status_code}') 

  ###############################################################################
  def _get_filenames_and_directories(self, dir_name : str):
    files_, directories_ = [], []
    if not dir_name:
      directories_, urls, fake_filename_contents = self.__fake_directories
    else:
      root_folders = StorageBase.split_path_into_dirs_filename(path=dir_name)
      what = self.__fake_directories
      for rf in root_folders:
        if rf not in what[0]:
          return [], []
        what = what[0][rf]
      directories_, urls, fake_filename_contents = what
      
    directories_ = [os.path.join(dir_name, k) for k in directories_.keys()]
    files_ = urls + [os.path.join(dir_name, k) for k in fake_filename_contents]
    return files_, directories_
    
  ###############################################################################
  def url_or_urls_to_fake_directory(self, url_or_urls, path, do_same_root_urls=True, check_other_urls=True):
    urls = [url_or_urls] if isinstance(url_or_urls, str) else [s for s in url_or_urls]
    # removing duplicates
    urls = remove_duplicates(urls)
    # making sure the root is the same
    root_url = os.path.dirname(urls[0])
    faulty_urls = [u for u in urls if not u.startswith(os.path.dirname(urls[0]))]
    urls = [u for u in urls if u not in faulty_urls]
    completed_urls = []
    external_urls = {}
    while urls:
      url = urls.pop(0)
      back_up_content, assets_urls, urls_to_add, backup_name = self.url_to_backup_content_hrefs(url)
      self.log_info(f'Analysing "{url}".\nResults saved as directory "{backup_name}"\n')
      if do_same_root_urls:
        completed_urls.append(url)
        urls += [u for u in urls_to_add if u not in completed_urls and u.startswith(root_url)]
        urls = remove_duplicates(urls)    
      if check_other_urls:
        for u in urls_to_add:
          if not u.startswith(root_url):
            if u in external_urls:
              external_urls[u].append(url)
            else:
              external_urls[u] = [url]

      assets_urls = remove_duplicates(assets_urls)
      fake_filename_contents_text = {'source_'+backup_name+'.txt' : back_up_content}

      StorageWeb.__fake_files.update({os.path.join(path, backup_name, k) : v for k, v in fake_filename_contents_text.items()})

      root_folders = StorageBase.split_path_into_dirs_filename(path=os.path.join(path, backup_name))
      dict_to_use = StorageWeb.__fake_directories
      for rf in root_folders:
        if rf not in dict_to_use[0]:
          dict_to_use[0][rf] = [{}, [], []]
        dict_to_use = dict_to_use[0][rf]

      dict_to_use[1] = assets_urls
      dict_to_use[2] = fake_filename_contents_text.keys()      

      StorageWeb.__name_content_type_is_content.update({k: True for k in assets_urls})
      StorageWeb.__name_content_type_is_content.update({k: False for k in fake_filename_contents_text})
      
    return external_urls

  ###############################################################################
  def url_to_backup_content_hrefs(self, url):
    self.__please_override()
    
import os
import requests

from StorageBase import StorageBase

#################################################################################
class StorageWeb(StorageBase):

  __fake_directories = [{}, [], []]
  __fake_files = {}
  __name_content_type_is_content = {}

  ###############################################################################
  def __init__(self):
    super().__init__(constructor_kwargs={})

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
  def create_fake_directory(dir_name, urls_content, fake_filename_contents_text):
    would_be_filenames = [os.path.basename(u) for u in urls_content] + [k for k in fake_filename_contents_text.keys()]
    dupes = [x for n, x in enumerate(would_be_filenames) if would_be_filenames.index(x) < n]
    assert not dupes, f'Duplicate filenames: {dupes}'

    StorageWeb.__fake_files.update({os.path.join(dir_name, k) : v for k, v in fake_filename_contents_text.items()})

    root_folders = StorageBase.split_path_into_dirs_filename(path=dir_name)
    dict_to_use = StorageWeb.__fake_directories
    for rf in root_folders:
      if rf not in dict_to_use:
        dict_to_use[0][rf] = [{}, [], []]
      dict_to_use = dict_to_use[0][rf]
    dict_to_use[1] = urls_content
    dict_to_use[2] = fake_filename_contents_text.keys()

    StorageWeb.__name_content_type_is_content.update({k: True for k in urls_content})
    StorageWeb.__name_content_type_is_content.update({k: False for k in fake_filename_contents_text})

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

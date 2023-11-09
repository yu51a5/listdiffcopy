import os
import requests

from StorageBase import StorageBase

#################################################################################
class StorageWeb(StorageBase):

  __fake_directories = [{}, [], []]
  __fake_files = {}

  ###############################################################################
  def __init__(self):
    super().__init__(constructor_kwargs={})

  ###############################################################################
  def get_contents(self, filename, length=None, func=None): # filename is url
    if filename in StorageWeb.__fake_files:
      return StorageWeb.__fake_files[filename]
    with requests.get(filename) as response:
      if response.status_code == 200:
        assert (length is None) != (func is None), f'Only one of {length}, {func} should be None'
        return func(response) if func else response.text[:length]
      else:
        self.log_error(f'Downloading of {filename} failed, code {response.status_code}') 

  ###############################################################################
  def create_fake_directory(dir_name, urls, fake_filename_contents):
    print('create_fake_directory', dir_name, urls, fake_filename_contents)
    would_be_filenames = [os.path.basename(u) for u in urls] + [k for k in fake_filename_contents.keys()]
    dupes = [x for n, x in enumerate(would_be_filenames) if would_be_filenames.index(x) < n]
    assert not dupes, f'Duplicate filenames: {dupes}'

    StorageWeb.__fake_files.update({os.path.join(dir_name, k) : v for k, v in fake_filename_contents.items()})

    root_folders = StorageBase.split_path_into_dirs_filename(path=dir_name)
    dict_to_use = StorageWeb.__fake_directories
    for rf in root_folders:
      if rf not in dict_to_use:
        dict_to_use[0][rf] = [{}, [], []]
      dict_to_use = dict_to_use[0][rf]
    dict_to_use[1] = urls
    dict_to_use[2] = fake_filename_contents.keys()

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
        print('what', rf, what)
      directories_, urls, fake_filename_contents = what
      
      
    directories_ = [os.path.join(dir_name, k) for k in directories_.keys()]
    files_ = urls + [os.path.join(dir_name, k) for k in fake_filename_contents]
    print('result', dir_name, directories_, files_)
    return files_, directories_

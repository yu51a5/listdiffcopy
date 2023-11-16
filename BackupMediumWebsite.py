import os

from Action2CompareCopyMove import synchronize, compare
from StorageWebMedium import StorageWebMedium
from StorageGitHub import StorageGitHub
from Logger import Logger
from Action1 import list

# inspirations: https://gist.github.com/bgoonz/217ba804d2b3aabe8415c9c99d8f9224
# and           https://github.com/gunar/medium-parser/blob/master/src/processElement.js

#################################################################################
class BackupMediumWebsite:
  
  def __init__(self, url_or_urls, path, storage=None, StorageType=None, kwargs_storage={}, do_same_root_urls=True, check_other_urls=True):

    logger = Logger()
    #assert False, isinstance(logger, Logger)
    swm = StorageWebMedium(logger=logger)

    external_urls_only = swm.url_or_urls_to_fake_directory(url_or_urls=url_or_urls, path=path, do_same_root_urls=True, check_other_urls=True)

    list(path=path, storage=swm, enforce_size_fetching=False)
    synchronize(path_from=path, path_to=path, storage_from=swm, StorageToType=StorageType, kwargs_to=kwargs_storage)

    
    #sa = SomeAction1(title=f'Scrapping {"/n".join(urls)} -> ',  StorageType=StorageType, path=path, kwargs_storage=kwargs_storage, storage=None, )

    def func(external_urls):

      
      # synchronize(storage_from=self.instanceStorageWeb, storage_to=self.storage, path_from=path, path_to=path)

      if external_urls:
        problem_eus = {}
        for eu, pages_where in external_urls.items():
          response_code = StorageWeb.get_response_code(eu)
          if response_code != 200:
            problem_eus[eu] = response_code
        if problem_eus:
          print('problem_eus', problem_eus)
  
      #self.storage.create_directory(path=assets_dir)
      #for url_pic in all_pic_urls:
        #target_path = os.path.join(assets_dir, os.path.basename(url_pic))
        #self.log_print_basic(f'Downloading {url_pic} -> {target_path}')
        #func_pic = lambda response: self.storage.create_file_given_content(filename=target_path, content=response.content)
        #instanceStorageWeb.get_contents(filename=url_pic, func=func_pic)
  
      #assert assets_dir is not None
      #self.storage.create_file_given_content(filename=assets_dir+'.txt', content=back_up_content)
    

  
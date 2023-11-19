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

    swm = StorageWebMedium(logger=logger)

    external_urls = swm.url_or_urls_to_fake_directory(url_or_urls=url_or_urls, path=path, do_same_root_urls=do_same_root_urls, check_other_urls=check_other_urls)

    if check_other_urls:
      swm.check_urls(external_urls, print_ok=True)
      
    synchronize(path_from=path, path_to=path, storage_from=swm, StorageToType=StorageType, kwargs_to=kwargs_storage)
    

  
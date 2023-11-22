from storage_actions import backup_a_Medium_website, delete
from StorageLocal import StorageLocal
from StoragePCloud import StoragePCloud
from StorageGitHub import StorageGitHub
from StorageBase import StorageBase

kwargs = dict(url_or_urls='https://medium.com/@real.zyxxy/about', 
             StorageType=StorageLocal, 
             path='medium' 
             #, kwargs_storage={'secret_name': "default_pcloud_secret"}
             ) #  medium_github_secret

delete('medium', StorageType=StorageLocal)

for _ in range(3):
  backup_a_Medium_website(**kwargs, do_same_root_urls=False, check_other_urls=False)

if False:
  backup_a_Medium_website(**kwargs, check_other_urls=False)
  backup_a_Medium_website(**kwargs, do_same_root_urls=False)
  backup_a_Medium_website(**kwargs)
  
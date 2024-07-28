import os 

from StorageSFTP import StorageSFTP
from StorageGitHub import StorageGitHub
from StoragePCloud import StoragePCloud

from storage_actions import copy_into

for sf in [ 'www/yu51a5.org/public_html/wp-content/themes/pinboard-child',
            'www/yu51a5.org/backup',
            'www/yu51a5.org/public_html/wp-content/uploads' ]:
  copy_into(StorageSFTP, sf, StoragePCloud, 'website')

# with cProfile.Profile() as pr:
#with create_logging_object() as ll:
  #folders_sftp_github = [['www/yu51a5.org/public_html/wp-content/themes/pinboard-child', 'pinboard-child'], ['www/yu51a5.org/backup', 'posts'], ['www/yu51a5.org/public_html/wp-content/themes', 'themes']]
  #folders_pcloud_github = [['music/nein', 'b']]

  #sync_contents(folders_sftp_github, StorageSFTP, StorageGitHub) #, StoragePCloud,)
  #sync_contents([['music/warum', 'a']], StorageGitHub, StorageGitHub) 
  # sync_contents([['tiny', 'e']], StorageGitHub, StoragePCloud) 
  #sync_contents([['music/warum', 'e']], StorageGitHub, StoragePCloud)
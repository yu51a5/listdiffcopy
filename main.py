#import os 
import cProfile
import pstats
from StorageSFTP import StorageSFTP
from StorageGitHub import StorageGitHub
from StoragePCloud import StoragePCloud
from sync_contents import sync_contents

with cProfile.Profile() as pr:
  #folders_sftp_github = [['www/yu51a5.org/public_html/wp-content/themes/pinboard-child', 'pinboard-child'], ['www/yu51a5.org/backup', 'posts'], ['www/yu51a5.org/public_html/wp-content/themes', 'themes']]
  #folders_pcloud_github = [['music/nein', 'b']]

  #sync_contents(folders_sftp_github, StorageSFTP, StorageGitHub) #, StoragePCloud,)
  sync_contents([['music/warum', 'a']], StorageGitHub, StorageGitHub) 
  # sync_contents([['tiny', 'e']], StorageGitHub, StoragePCloud) 
  #sync_contents([['', 'music/warum']], StoragePCloud, StorageGitHub) 

  print("all done!")
  
  #stats = pstats.Stats(pr).sort_stats('tottime')
  # stats.print_stats()
  #stats.dump_stats('pstats.csv')
  
  # pr.print_stats()

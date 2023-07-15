#import os 
import cProfile
import pstats
from StorageSFTP import StorageSFTP
from StorageGitHub import StorageGitHub
from StoragePCloud import StoragePCloud
from sync_contents import sync_contents, list_contents
from StorageBase import do_dry_run

with cProfile.Profile() as pr:
  #folders_sftp_github = [['www/yu51a5.org/public_html/wp-content/themes/pinboard-child', 'pinboard-child'], ['www/yu51a5.org/backup', 'posts'], ['www/yu51a5.org/public_html/wp-content/themes', 'themes']]
  #folders_pcloud_github = [['music/nein', 'b']]

  #sync_contents(folders_sftp_github, StorageSFTP, StorageGitHub) #, StoragePCloud,)
  #sync_contents([['music/warum', 'a']], StorageGitHub, StorageGitHub) 
  # sync_contents([['tiny', 'e']], StorageGitHub, StoragePCloud) 
  #do_dry_run()
  #sync_contents([['music/warum', 'e']], StorageGitHub, StoragePCloud) 
  #sync_contents([['', 'music/warum']], StoragePCloud, StorageGitHub) 
  #

  #list_contents(StorageSFTP, 'www/yu51a5.org/backup')
  list_contents(StorageSFTP, 'www/yu51a5.org/public_html/wp-content/uploads/')
  #list_contents(StoragePCloud, 'sf')
  #sync_contents(StorageSFTP, 'www/yu51a5.org/backup', StoragePCloud, 'sf') 
  #sync_contents(StorageSFTP, 'www/yu51a5.org/backup', StorageGitHub, 'w1/w3')  
  #sync_contents(StorageSFTP, 'www/yu51a5.org/public_html/wp-content/themes/pinboard-child', StorageGitHub, 'pinboard-child')  
  #sync_contents(StorageSFTP, 'www/yu51a5.org/public_html/wp-content/uploads/persia_greece', StoragePCloud, 'persia_greece')  
  #list_contents(StorageGitHub, 'w1')
  print("all done!")
  
  #stats = pstats.Stats(pr).sort_stats('tottime')
  # stats.print_stats()
  #stats.dump_stats('pstats.csv')
  
  # pr.print_stats()

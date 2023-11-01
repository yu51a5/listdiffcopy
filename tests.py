import os 
import cProfile
import pstats
from StorageSFTP import StorageSFTP
from StorageGitHub import StorageGitHub
from StoragePCloud import StoragePCloud

from SomeAction import list_directory, rename_file, delete_directory, rename_directory, delete_file
from SomeAction2 import compare, synchronize, copy

# with cProfile.Profile() as pr:
#with create_logging_object() as ll:
  #folders_sftp_github = [['www/yu51a5.org/public_html/wp-content/themes/pinboard-child', 'pinboard-child'], ['www/yu51a5.org/backup', 'posts'], ['www/yu51a5.org/public_html/wp-content/themes', 'themes']]
  #folders_pcloud_github = [['music/nein', 'b']]

  #sync_contents(folders_sftp_github, StorageSFTP, StorageGitHub) #, StoragePCloud,)
  #sync_contents([['music/warum', 'a']], StorageGitHub, StorageGitHub) 
  # sync_contents([['tiny', 'e']], StorageGitHub, StoragePCloud) 
  #sync_contents([['music/warum', 'e']], StorageGitHub, StoragePCloud) 
  #sync_contents([['', 'music/warum']], StoragePCloud, StorageGitHub) 
  #

# list_contents(StorageSFTP, 'www/yu51a5.org/backup')
# list_contents(StorageSFTP, 'www/yu51a5.org/public_html/wp-content/uploads/')

#list_contents(StoragePCloud, '')
#list_contents(StorageSFTP, 'www/yu51a5.org/public_html/wp-content/themes/')
#list_contents(StorageGitHub, 'w1')

copy(StoragePCloud, 'My Music/GotJoy.mp3', StoragePCloud, 'aa/My_Music/GotJoy.mp3')
assert 6 > 7

copy(StoragePCloud, 'My Pictures', StoragePCloud, 'aa/My_Pictures')

compare(StoragePCloud, 'My Pictures', StoragePCloud, 'aa/My_Pictures')
compare(StoragePCloud, 'My Music', StoragePCloud, 'aa/My_Music')
copy(StoragePCloud, 'My Music', StoragePCloud, 'aa/My_Music')

list_directory(StorageSFTP, 'www/yu51a5.org/public_html/wp-content/themes/')


synchronize(StoragePCloud, 'aa', StorageGitHub, 'a')
_, files, dirs = list_directory(StoragePCloud, 'aa')
dirs_with_files = [d for d in dirs if len(dirs[d][0]) >= 1]

assert len(dirs_with_files) >= 3
assert len(dirs[dirs_with_files[0]][0]) >=2

delete_file(StoragePCloud, dirs[dirs_with_files[0]][0][1])
delete_directory(StoragePCloud, dirs_with_files[2])

synchronize(StorageGitHub, 'a', StoragePCloud, 'aa')
compare(StorageGitHub, 'a', StoragePCloud, 'aa')

rename_file(StoragePCloud, dirs[dirs_with_files[0]][0][0], dirs[dirs_with_files[0]][0][1])
rename_directory(StoragePCloud, dirs_with_files[1], dirs_with_files[2])

synchronize(StorageGitHub, 'a', StoragePCloud, 'aa')
compare(StorageGitHub, 'a', StoragePCloud, 'aa')

  #sync_contents(StorageSFTP, 'www/yu51a5.org/public_html/wp-content/uploads', StoragePCloud, 'wp_uploads')
  #sync_contents(StorageSFTP, 'www/yu51a5.org/public_html/wp-content/uploads', StorageGitHub, 'dont')
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

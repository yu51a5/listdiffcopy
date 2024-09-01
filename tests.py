import os 
import cProfile
import pstats
from StorageSFTP import StorageSFTP
#from StorageGitHub import StorageGitHub
from StoragePCloud import StoragePCloud

from storage_actions import list, rename, delete, compare, synchronize, copy, get_filenames_and_dirnames, get_filenames_and_dirnames_


from utils import convert_image, get_file_extention, is_an_image, resize_image, idem, convert_image_to_AVIF_if_another_format_image, batch_resize_images

from StorageSFTP import StorageSFTP
from StorageLocal import StorageLocal
from StorageAction2 import Transform
from StorageWeb import StorageWeb

delete( StorageSFTP, "www/yu51a5.xyz/public_html/wp-content/uploads/hamlet/test8/dogs")

copy(StorageLocal, "dogs", StorageSFTP, "www/yu51a5.xyz/public_html/wp-content/uploads/hamlet/test8/dogs")

Transform(StorageLocal, "dogs", 
          StorageSFTP, "www/yu51a5.xyz/public_html/wp-content/uploads/hamlet/test8",
          filename_contents_transform=convert_image_to_AVIF_if_another_format_image)

list(StorageSFTP, "www/yu51a5.xyz/public_html/wp-content/uploads//hamlet/test8")

quit()

Transform( StorageSFTP, "www/yu51a5.xyz/public_html/wp-content/uploads/hamlet/test8", 
  StorageSFTP, "www/yu51a5.xyz/public_html/wp-content/uploads/hamlet/test8resized",
  filename_contents_transform=batch_resize_images)

assert 0

with StorageWeb() as sw:
  img_content = sw.read_file("https://www.nationalgallery.org.uk/media/35259/n-0035-00-000177-hd.jpg", use_content_not_text=True)

init_filename = "Titian_Bacchus_and_Ariadne.jpg"


with StorageSFTP() as s:
  for fn, content in [[init_filename, img_content]]:
    s.write_file(f"www/yu51a5.xyz/public_html/wp-content/uploads/hamlet/test9/{fn}", content)

list(StorageSFTP, "www/yu51a5.xyz/public_html/wp-content/uploads/")




with StorageLocal() as sl:
  original_img_content = sl.read_file("dogs/l.jpg")
  result = convert_image_to_AVIF(original_img_content)
  with StorageSFTP() as s:
    s.write_file("www/yu51a5.xyz/public_html/wp-content/uploads/hamlet/test9/puppy39.avif", result)


list(StoragePCloud, 'My Music')
list(StorageSFTP, 'www/yu51a5.xyz/public_html/wp-content/themes/')

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

copy(StoragePCloud, 'My Pictures', StoragePCloud, 'aa/My_Pictures')

compare(StoragePCloud, 'My Pictures', StoragePCloud, 'aa/My_Pictures')
compare(StoragePCloud, 'My Music', StoragePCloud, 'aa/My_Music')
copy(StoragePCloud, 'My Music', StoragePCloud, 'aa/My_Music')
copy(StoragePCloud, 'My Music', StoragePCloud, 'aa/My_Music2')


if False:
  synchronize(StoragePCloud, 'aa', StorageGitHub, 'a')
  
files, dirs = get_filenames_and_dirnames_(StoragePCloud, 'aa')
dirs_with_files = [d for d in dirs if get_filenames_and_dirnames_(StoragePCloud, d)[0]]

print(dirs_with_files)
print(dirs)
assert len(dirs_with_files) >= 3
assert len(get_filenames_and_dirnames_(StoragePCloud, dirs_with_files[0])[0]) >=2

delete(StoragePCloud, dirs[dirs_with_files[0]][0][1])
delete(StoragePCloud, dirs_with_files[2])

if False:
  synchronize(StorageGitHub, 'a', StoragePCloud, 'aa')
  compare(StorageGitHub, 'a', StoragePCloud, 'aa')

rename(StoragePCloud, dirs[dirs_with_files[0]][0][0], dirs[dirs_with_files[0]][0][1])
rename(StoragePCloud, dirs_with_files[1], dirs_with_files[2])

if False:
  synchronize(StorageGitHub, 'a', StoragePCloud, 'aa')
  compare(StorageGitHub, 'a', StoragePCloud, 'aa')

synchronize(StorageSFTP, 'www/yu51a5.xyz/public_html/wp-content/uploads/hamlet', StoragePCloud, 'wp_uploads/hamlet')
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

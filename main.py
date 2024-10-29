import paramiko
import pandas
import sys
import os
sys.path.append('src')
#import listdiffcopy
# https://docs.pytest.org/en/stable/explanation/goodpractices.html#choosing-an-import-mode
from listdiffcopy import StorageBase, StorageSFTP, StorageLocal
from listdiffcopy.StorageAction2 import CopyAndTransform
from listdiffcopy.storage_actions import list, copy_into, create_directory
from listdiffcopy.utils import batch_resize_images

def files_lower_case(files):
  with StorageLocal.StorageLocal() as sl:
    start_filename = sl.read_file_(path="filename_started.txt", binary=False)
  return [f for f in files if os.path.basename(f) < start_filename]

def batch_resize_images_plus(path, *args, **kwargs):
  with StorageLocal.StorageLocal() as sl:
    pass # sl.write_file_(path="filename_started.txt", content=path)
  result = batch_resize_images(path=path, *args, **kwargs)
  return result

list(StorageLocal.StorageLocal, "dogs/", filenames_filter=[files_lower_case])
CopyAndTransform(StorageLocal.StorageLocal, "dogs/",
                   StorageSFTP.StorageSFTP, "domains/yu51a.org/public_html/wp-content/uploads/hamlet/test8/dogs2", 
                   sert_key=lambda x:x, sort_reverse=True,
                   filename_contents_transform=batch_resize_images_plus, 
                   filenames_filter=[files_lower_case],
                   change_if_both_exist='pass')

quit()

print(dir(StorageSFTP))
list(StorageLocal.StorageLocal, path='logs', sort_reverse=True)
create_directory(StorageSFTP.StorageSFTP, "www/yu51a5.xyz/public_html/wp-content/uploads/hamlet/test8/dogs")
copy_into(StorageLocal.StorageLocal, "dogs", StorageSFTP.StorageSFTP, "www/yu51a5.xyz/public_html/wp-content/uploads/hamlet/test8/dogs2", sort_reverse=True)
list(StorageSFTP.StorageSFTP, "www/yu51a5.xyz/public_html/wp-content/uploads/hamlet")

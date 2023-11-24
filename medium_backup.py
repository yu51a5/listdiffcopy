import os
from storage_actions import backup_a_Medium_website, delete, get_size, get_content, synchronize, create_directory,\
                            list, check_path_exist_is_dir_not_file, create_file_given_content
from StorageLocal import StorageLocal
from StoragePCloud import StoragePCloud
from StorageGitHub import StorageGitHub
from StorageWebMedium import StorageWebMedium
from LoggerObj import LoggerObj

if False:
  logger = LoggerObj("another")
  
  content = "Test line"
  
  d = 'test_test_test2'
  t, di = StoragePCloud, {'secret_name': "default_pcloud_secret"}
  #delete(d*2, StorageType=t, kwargs_storage=di)
  #create_directory(d*2, StorageType=t, kwargs_storage=di)
  synchronize(path_from=d, path_to=d*2, StorageFromType=StorageLocal, StorageToType=t, kwargs_to=di)
  synchronize(path_from=d, path_to=d, StorageFromType=StorageLocal, StorageToType=t, kwargs_to=di)
  
  assert 0.00
  
  for t, di in ((StorageLocal, {}), 
                (StoragePCloud, {'secret_name': "default_pcloud_secret"}), 
                (StorageGitHub, {'secret_name': "medium_github_secret"})):
    for d in ["test_test_test", "test_test_test2"]:
      create_directory(d, logger=logger, StorageType=t, kwargs_storage=di)
      check_path_exist_is_dir_not_file(d, StorageType=t, kwargs_storage=di)
      list(d, StorageType=t, kwargs_storage=di, enforce_size_fetching=True)
      filename = os.path.join(d, "testfile.txt")
      create_file_given_content(filename, content=content, StorageType=t, kwargs_storage=di)
      list(d, StorageType=t, kwargs_storage=di, enforce_size_fetching=True)
      assert len(content) == get_size(filename, StorageType=t, kwargs_storage=di)
      if t != StorageLocal:
        synchronize(path_from=d, path_to=d, StorageFromType=StorageLocal, StorageToType=t, kwargs_to=di)
        list(d, StorageType=t, kwargs_storage=di, enforce_size_fetching=True)
        assert len(content) == (get_size(filename, StorageType=t, kwargs_storage=di))
  
  assert 0

med_url_1 = 'https://medium.com/@yu51a5/123-1332f629e146?source=friends_link&sk=6a7033b41578929ffc6569bbb25283f9'
med_url_2 = 'https://medium.com/@real.zyxxy/about'
d2 = 'medium2'
d2_to =  'medium2'

swm = StorageWebMedium()
swm.url_or_urls_to_fake_directory(url_or_urls=med_url_1, path='medium2')
swm.list(d2, enforce_size_fetching=False)
cont = {}
#cont = {str(StorageWebMedium) : swm.get_content(s)}
for t, di in ((StorageLocal, {}), 
              (StorageGitHub, {'secret_name': "medium_github_secret"}), 
              (StoragePCloud, {'secret_name': "default_pcloud_secret"})):
  synchronize(path_from=d2, path_to=d2_to, storage_from=swm, StorageToType=t, kwargs_to=di)
  cont[str(t)] = get_size(d2_to, StorageType=t, kwargs_storage=di)

print(cont)
assert 0.00000

kwargs = dict(url_or_urls=med_url_1, 
             StorageType=StorageLocal, 
             path='medium' 
             #, kwargs_storage={'secret_name': "default_pcloud_secret"}
             ) #  medium_github_secret



#delete('medium', StorageType=StorageLocal)
for d in ('medium/about', 'medium/about/source_about.txt'):
  print(d, swm.get_size(d))
  for t, di in ((StorageLocal, {}), 
                (StoragePCloud, {'secret_name': "default_pcloud_secret"}), 
                (StorageGitHub, {'secret_name': "medium_github_secret"}), ):
    print(str(t), (d, t, di))
    print(str(t), get_size(d, StorageType=t, kwargs_storage=di))

s = 'test_files'
cont = {}
#cont = {str(StorageWebMedium) : swm.get_content(s)}
for t, di in ((StorageLocal, {}), 
              (StoragePCloud, {'secret_name': "default_pcloud_secret"}), 
              (StorageGitHub, {'secret_name': "medium_github_secret"})):
  if t != StorageLocal:
    delete('test_files', StorageType=t, kwargs_storage=di)
    synchronize(path_from=s, path_to='test_files', StorageFromType=StorageLocal, StorageToType=t, kwargs_to=di)
  cont[str(t)] = get_content(s, StorageType=t, kwargs_storage=di)

print(cont)


for _ in range(0):
  backup_a_Medium_website(**kwargs, do_same_root_urls=False, check_other_urls=False)

if False:
  backup_a_Medium_website(**kwargs, check_other_urls=False)
  backup_a_Medium_website(**kwargs, do_same_root_urls=False)
  backup_a_Medium_website(**kwargs)
  
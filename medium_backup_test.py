import os
from settings import log_dirname
from storage_actions import backup_a_Medium_website, delete, get_size, read_file, synchronize, create_directory,\
                            list, check_path_exist_is_dir_not_file, write_file, get_filenames_and_directories
from StorageLocal import StorageLocal
from StoragePCloud import StoragePCloud
from StorageGitHub import StorageGitHub
from StorageWebMedium import StorageWebMedium
from LoggerObj import LoggerObj

github_secret_name = "medium_github_2" #  medium_github_secret

mb_kwargs = dict(url_or_urls='https://medium.com/@real.zyxxy/about', path="medium55", do_same_root_urls=True)
backup_a_Medium_website(**mb_kwargs, StorageType=StorageGitHub, kwargs_storage={'secret_name': github_secret_name}, check_other_urls=True, save_texts=True, save_assets=False)
backup_a_Medium_website(**mb_kwargs, StorageType=StoragePCloud, kwargs_storage={'secret_name': "default_pcloud_secret"}, check_other_urls=False, save_texts=False, save_assets=True)

if 1:
  t, di = (StoragePCloud, {'secret_name': "default_pcloud_secret"})
  filename = os.path.join('test', "testfile.txt")
  content = "Test line 22"
  write_file(filename, content=content, StorageType=t, kwargs_storage=di)
  write_file(filename, content=content + "ho ho", StorageType=t, kwargs_storage=di)
  
  logger = LoggerObj("another")
  content = "Test line"
  
  for t, di in ((StorageLocal, {}), 
                (StoragePCloud, {'secret_name': "default_pcloud_secret"}), 
                (StorageGitHub, {'secret_name': github_secret_name})):
    with t(**di, logger=logger) as storage:
      for d in ["test_test_test", "test_test_test2"]:
        storage.create_directory(d)
        storage.check_path_exist_is_dir_not_file(d)
        storage.list(d, enforce_size_fetching=True)
        filename = os.path.join(d, "testfile.txt")
        storage.write_file(filename, content=content) 
        storage.list(d, enforce_size_fetching=True)
        assert len(content) == storage.get_size(filename)
        if t != StorageLocal:
          synchronize(path_from=d, path_to=d, StorageFromType=StorageLocal, StorageToType=t, kwargs_to=di)
          with StorageLocal() as sl:
            sl.list(d, enforce_size_fetching=True)
            assert len(content) == (sl.get_size(filename))
    
  
  med_url_1 = 'https://medium.com/@yu51a5/123-1332f629e146?source=friends_link&sk=6a7033b41578929ffc6569bbb25283f9'
  d1 = 'medium1'
  
  swm = StorageWebMedium()
  swm.url_or_urls_to_fake_directory(url_or_urls=med_url_1, path=d1)
  swm.list(d1, enforce_size_fetching=False)
  cont = {}
  for t, di in ((StorageLocal, {}), 
                (StorageGitHub, {'secret_name': github_secret_name}), 
                (StoragePCloud, {'secret_name': "default_pcloud_secret"})):
    synchronize(path_from=d1, path_to=d1, storage_from=swm, StorageToType=t, kwargs_to=di)
    cont[str(t)] = get_size(d1, StorageType=t, kwargs_storage=di)

med_url_2 = 'https://medium.com/@real.zyxxy/about'
d2 = 'medium2'
swm.url_or_urls_to_fake_directory(url_or_urls=med_url_2, path=d2)
swm.list(d2, enforce_size_fetching=False)

kwargs = dict(url_or_urls=med_url_2, path=d2)

for t, di in ((StoragePCloud, {'secret_name': "default_pcloud_secret"}), 
              (StorageGitHub, {'secret_name': github_secret_name}), 
              (StorageLocal, {}), ):
  kwargs['StorageType'] = t
  backup_a_Medium_website(**kwargs)

for _ in range(3):
  backup_a_Medium_website(**kwargs, do_same_root_urls=False, check_other_urls=False)

if True:
  backup_a_Medium_website(**kwargs, check_other_urls=False)
  backup_a_Medium_website(**kwargs, do_same_root_urls=False)
  backup_a_Medium_website(**kwargs)

# cleanup
_, dirs = get_filenames_and_directories("", StorageType=StorageLocal)
for d in dirs:
  if (os.path.basename(d) not in [log_dirname, 'venv']) and ("a" <= os.path.basename(d)[0] <= 'z'):
    delete(d, StorageType=StorageLocal)
  
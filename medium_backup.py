from storage_actions import backup_a_Medium_website, delete, get_size, get_content, synchronize
from StorageLocal import StorageLocal
from StoragePCloud import StoragePCloud
from StorageGitHub import StorageGitHub
from StorageWebMedium import StorageWebMedium

kwargs = dict(url_or_urls='https://medium.com/@real.zyxxy/about', 
             StorageType=StorageLocal, 
             path='medium' 
             #, kwargs_storage={'secret_name': "default_pcloud_secret"}
             ) #  medium_github_secret

swm = StorageWebMedium()
swm.url_or_urls_to_fake_directory(url_or_urls='https://medium.com/@real.zyxxy/about', path='medium', do_same_root_urls=False, check_other_urls=False)

#delete('medium', StorageType=StorageLocal)
for d in ('medium/about', 'medium/about/source_about.txt'):
  #print(d, swm.get_size(d))
  for t, di in (#(StorageLocal, {}), 
                #(StoragePCloud, {'secret_name': "default_pcloud_secret"}), 
                (StorageGitHub, {'secret_name': "medium_github_secret"}), ):
    print(str(t), (d, t, di))
    print(str(t), get_size(d, StorageType=t, kwargs_storage=di))

s = 'test_files/t.log'
cont = {}
#cont = {str(StorageWebMedium) : swm.get_content(s)}
for t, di in ((StorageLocal, {}), 
              (StoragePCloud, {'secret_name': "default_pcloud_secret"}), 
              (StorageGitHub, {'secret_name': "medium_github_secret"})):
  if t != StorageLocal:
    synchronize(path_from=s, path_to='test_files', StorageFromType=StorageLocal, StorageToType=t, kwargs_to=di)
  cont[str(t)] = get_content(s, StorageType=t, kwargs_storage=di)

print(cont)


for _ in range(0):
  backup_a_Medium_website(**kwargs, do_same_root_urls=False, check_other_urls=False)

if False:
  backup_a_Medium_website(**kwargs, check_other_urls=False)
  backup_a_Medium_website(**kwargs, do_same_root_urls=False)
  backup_a_Medium_website(**kwargs)
  
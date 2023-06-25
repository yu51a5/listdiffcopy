import os 
from StorageSFTP import StorageSFTP
from StorageGitHub import StorageGitHub
from StoragePCloud import StoragePCloud
from sync_contents import sync_contents

#pcloud = StoragePCloud(is_eapi=True)
#pcloud._get_filenames_and_directories('')

#storage = StorageGitHub()
folders_pairs = [gsp.split(',') for gsp in os.environ['sftp_github_folders'].split(';')]
print(folders_pairs)

sync_contents(folders_pairs, StorageSFTP, StorageGitHub, kwargs_to={"repo_name":"wordpress"}) #, StoragePCloud, kwargs_to={'is_eapi' : True} ,)
sync_contents([['My Music', 'music']], StoragePCloud, StorageGitHub, kwargs_from={'is_eapi' : True}, kwargs_to={"repo_name":"wordpress"}) 

print("all done!")

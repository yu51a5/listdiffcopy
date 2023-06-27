import os 
from StorageSFTP import StorageSFTP
from StorageGitHub import StorageGitHub
from StoragePCloud import StoragePCloud
from sync_contents import sync_contents

folders_sftp_github = [gsp.split(',') for gsp in os.environ['sftp_github_folders'].split(';')]
print(folders_sftp_github)

folders_pcloud_github = [['', 'music']]

sync_contents(folders_sftp_github, StorageSFTP, StorageGitHub, kwargs_to={"repo_name":"wordpress"}) #, StoragePCloud, kwargs_to={'is_eapi' : True} ,)
sync_contents(folders_pcloud_github, StoragePCloud, StorageGitHub, kwargs_from={'is_eapi' : True}, kwargs_to={"repo_name":"wordpress"}) 

print("all done!")

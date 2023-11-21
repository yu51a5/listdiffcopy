from BackupMediumWebsite import BackupMediumWebsite
from StorageLocal import StorageLocal
from StoragePCloud import StoragePCloud
from StorageGitHub import StorageGitHub

BackupMediumWebsite(url_or_urls='https://medium.com/@real.zyxxy/about', 
                    StorageType=StorageGitHub, 
                    path='medium', 
                    kwargs_storage={'secret_name':"medium_github_secret"}
                    #, do_same_root_urls=False
                    , check_other_urls=False
                   )


#print(', \n'.join(["'https://medium.com/" + u + "'" for u in urls if not u.startswith('https://')]))

urls = ['https://medium.com//@real.zyxxy/python-for-busy-people-part-0-why-python-is-the-swiss-knife-of-programming-7abb4a19d1de?source=about_page-------------------------------------&sk=eed9ccf298eaf5475bc36d61561bec3a', 
       'https://medium.com//@real.zyxxy/python-learning-for-busy-people-1-3-resources-a81cd604cd99?source=about_page-------------------------------------&sk=d642604346531c1fedf6a3b28fa7eb52', 
       'https://medium.com//@real.zyxxy/python-learning-for-busy-people-2-3-code-blocks-ed743f28be63?source=about_page-------------------------------------', 
       'https://medium.com//@real.zyxxy/python-for-busy-people-3-1-3-atomic-types-73f97c36f8d6?source=about_page-------------------------------------&sk=803e16dfb164aa35fa3f70c59f262ed0', 
       'https://medium.com//@real.zyxxy/python-pieces-for-busy-people-4-5-composite-types-in-python-2e67bb217945?source=about_page-------------------------------------&sk=5ee725548a109f3ab19dc5afe57aef30', 
       'https://medium.com//@real.zyxxy/what-does-good-python-code-mean-ddc48360aad4?source=about_page-------------------------------------&sk=26a0fa98dad75c2e98f00d85f5622afb', 
       'https://medium.com//@real.zyxxy/having-your-code-reviewed-f37a7f48175c?source=about_page-------------------------------------&sk=c146446e8261c1acdac3b0c3bb06ad9c', 
       'https://medium.com//@real.zyxxy/get-a-web-based-pro-grade-python-environment-in-5-minutes-at-0-cost-8843f5a07f88?source=about_page-------------------------------------&sk=78358fc8867308d0effe835e63409413', 
       'https://medium.com//@real.zyxxy/hello-chatgpt-world-run-chatgpt-inside-a-python-script-in-5-minutes-4c9f4bdb6e28?source=about_page-------------------------------------&sk=453993a0cb6a50d4e5f3bcf1a1f9800a', 
       'https://medium.com//@real.zyxxy/hello-chatgpt-world-run-chatgpt-inside-a-python-script-in-5-minutes-4c9f4bdb6e28?source=about_page-------------------------------------&sk=453993a0cb6a50d4e5f3bcf1a1f9800a']
#url = 'https://medium.com/@real.zyxxy/about'

from BackupMediumWebsite import BackupMediumWebsite
from StorageLocal import StorageLocal
from StoragePCloud import StoragePCloud
from StorageGitHub import StorageGitHub

BackupMediumWebsite(url_or_urls='https://medium.com/@real.zyxxy/about', 
                    StorageType=StorageGitHub, 
                    path='medium', 
                    kwargs_storage={'secret_name':"medium_github_secret"})


#print(', \n'.join(["'https://medium.com/" + u + "'" for u in urls if not u.startswith('https://')]))

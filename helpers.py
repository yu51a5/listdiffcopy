#import os
from github import Github
import paramiko
import io

def get_ssh_client(hostname: str, port: str, username: str, password: str, private_key: str):
  
  # establish connection with targeted server
  ssh_client = paramiko.SSHClient()

  # needed to ensure that `\n`s are in the right place
  ssh_private_key = f"""-----BEGIN OPENSSH PRIVATE KEY-----
  {private_key}==
  -----END OPENSSH PRIVATE KEY-----"""

  # https://stackoverflow.com/questions/9963391/how-do-use-paramiko-rsakey-from-private-key
  private_key = io.StringIO()
  private_key.write(ssh_private_key)
  private_key.seek(0)
  key = paramiko.RSAKey.from_private_key(private_key, password)

  
  ssh_client = paramiko.SSHClient()
  # AutoAddPolicy explained in --> https://www.linode.com/docs/guides/use-paramiko-python-to-ssh-into-a-server/
  ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
  ssh_client.connect(hostname, port, username, pkey=key)

  return ssh_client


# filenames and their sha's are needed to be able to update existing files
# https://stackoverflow.com/questions/63435987/python-pygithub-if-file-exists-then-update-else-create
def get_repo_and_its_filenames_sha(token : str, repo_name : str):

  # Github token
  # https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
  github_object = Github(token)
  github_user = github_object.get_user()
  repo = github_user.get_repo(repo_name)
    
  all_files = {}

  contents = repo.get_contents('.')
  while contents:
    content_item = contents.pop(0)
    if content_item.type == "dir":
      pass # contents.extend(repo.get_contents(content_item.path))
    else:
      filename = str(content_item).replace('ContentFile(path="','').replace('")','')
      contents_file = repo.get_contents(filename)
      all_files[filename] = contents_file.sha
      
  return repo, all_files

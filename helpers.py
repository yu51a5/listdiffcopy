from github import Github, Repository
import paramiko
import io
import json
import os
import requests

###############################################################################
# get pCloud service
###############################################################################
GOOGLE_DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def get_google_drive_service():
  service_account_info = json.loads(os.getenv('GDRIVE_AUTH'))
  creds = service_account.Credentials.from_service_account_info(
                             service_account_info, scopes=GOOGLE_DRIVE_SCOPES)
  service = build('drive', 'v3', credentials=creds)
  return service

###############################################################################
# get SSHClient client
# this connection works for siteground.com servers
###############################################################################
def get_siteground_ssh_client(hostname: str, port: str, username: str, password: str,
                   private_key: str):

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
  ssh_client.connect(hostname=hostname, port=port, username=username, pkey=key)

  return ssh_client

###############################################################################
def get_another_ssh_client(hostname: str, port: str, username: str, password: str):
  ssh_client = paramiko.SSHClient()
  ssh_client.connect(hostname=hostname, port=port, username=username, password=password)
  return ssh_client
  
###############################################################################
# filenames and their sha's are needed to be able to update existing files, see
# https://stackoverflow.com/questions/63435987/python-pygithub-if-file-exists-then-update-else-create
###############################################################################
def get_github_repo(token: str, repo_name: str):

  # Github token, see
  # https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
  github_object = Github(token)
  github_user = github_object.get_user()
  repo = github_user.get_repo(repo_name)
  return repo


def get_github_repo_filenames_sha(repo: Repository, dir: str):
  all_files = {}
  contents = repo.get_contents(dir)
  while contents:
    content_item = contents.pop(0)
    if content_item.type == "dir":
      print(content_item.name)
      all_files[content_item.name] = get_github_repo_filenames_sha(repo=repo, dir=content_item.path)
    else:
      filename = str(content_item).replace('ContentFile(path="', '').replace('")', '')
      contents_file = repo.get_contents(filename)
      all_files[filename[len(dir)+1:]] = contents_file.sha

  return all_files

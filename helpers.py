from github import Github, Repository
import paramiko
import io
import os
import requests

requests_session = requests.Session()
#pcloud_auth = {what : os.environ[f'pcloud_{what}'] for what in ['username', 'password']}

###############################################################################
# pCloud. Use eapi if the server is in Europe
###############################################################################
def get_pCloud_file_stats(full_filename):
  files = {'01 - Border Reiver.mp3': open('d:\MUSIC\Get Lucky\01 - Border Reiver.mp3', 'rb')}
  post = requests_session.post('https://eapi.pcloud.com/uploadfile', files=files, data=pcloud_auth)
  return post.json()
  
def upload_to_pCloud(full_filename):
  files = {'01 - Border Reiver.mp3': open('d:\MUSIC\Get Lucky\01 - Border Reiver.mp3', 'rb')}
  post = requests_session.post('https://eapi.pcloud.com/uploadfile', files=files, data=pcloud_auth)
  return post.json()

###############################################################################
# get SSHClient client
###############################################################################
def get_ssh_client(hostname=None, port=None, username=None, password=None, private_key=None):

  ssh_client = paramiko.SSHClient()
  # AutoAddPolicy explained in --> https://www.linode.com/docs/guides/use-paramiko-python-to-ssh-into-a-server/
  ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

  ssh_client_params = dict(hostname=hostname, port=port, username=username, password=password)
  for what in ('hostname', 'port', 'username', 'password'):
    if not ssh_client_params[what]:
      ssh_client_params[what] = os.getenv(f'sftp_{what}')

  not_defined_errors = [what for what in ('hostname', 'port', 'username', 'password') if not ssh_client_params[what]]
  if not_defined_errors:
    raise Exception(", ".join(not_defined_errors) + " are not defined")

  if not private_key:
    private_key = os.getenv("sftp_private_key")
  if private_key:
    # https://stackoverflow.com/questions/9963391/how-do-use-paramiko-rsakey-from-private-key
    # needed to ensure that `\n`s are in the right place
    private_key__ = io.StringIO()
    private_key__.write(f"""-----BEGIN OPENSSH PRIVATE KEY-----
                       {private_key}==
                       -----END OPENSSH PRIVATE KEY-----""")
    private_key__.seek(0)
    ssh_client_params['pkey'] = paramiko.RSAKey.from_private_key(private_key__, ssh_client_params['password'])
    del ssh_client_params['password']

  ssh_client.connect(**ssh_client_params)
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

###############################################################################
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

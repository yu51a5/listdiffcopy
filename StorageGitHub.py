import os
from github import Github, ContentFile
import requests
from requests.structures import CaseInsensitiveDict

from StorageBase import StorageBase
from settings import fetch_github_modif_timestamps

#################################################################################
class StorageGitHub(StorageBase):
  file_size_limit = 100 << 20
  
  # github_token secret structure: OWNER|REPO|TOKEN . For Github token, see
  # https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
  def __init__(self, owner=None, repo_name=None, token=None):
    super().__init__()
    
    secret = os.getenv('github_owner_repo_token')
    secret_components = secret.split('|') if secret else []
    
    self.token = secret_components.pop(-1) if secret_components and (not token) else token
    self.repo_name = secret_components.pop(-1) if secret_components and (not repo_name) else repo_name
    self.owner = secret_components.pop(-1) if secret_components and (not owner) else owner
        
    github_object = Github(self.token)
    github_user = github_object.get_user()
    self.repo = github_user.get_repo(self.repo_name)

  ###############################################################################
  def inexistent_directories_are_empty(self):
    return True

  ###############################################################################
  # filenames and their sha's are needed to be able to update existing files, see
  # https://stackoverflow.com/questions/63435987/python-pygithub-if-file-exists-then-update-else-create
  ###############################################################################
  def _get_filenames_and_directories(self, path_so_far: str):
    
    all_files, all_directories = [], []
    
    exists = self.check_directory_exists(path=path_so_far, create_if_doesnt_exist=False)

    if exists:
    
      contents = self.repo.get_contents(path_so_far)
      if isinstance(contents, ContentFile.ContentFile):
        contents = [contents]
  
      for content_item in contents:
        if content_item.type == "dir":
          all_directories.append(content_item.path)
        else:
          all_files.append(content_item.path)
          self.set_file_info(content_item.path, {'sha' : content_item.sha})

    return all_files, all_directories

  ###############################################################################
  def get_contents(self, filename, length=None):

    if length:
      return bytes(b'')

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/vnd.github.v3.raw"
    headers["Authorization"] = f"Bearer {self.token}"
    headers["X-GitHub-Api-Version"] = "2022-11-28"

    url = f"https://api.github.com/repos/{self.owner}/{self.repo_name}/contents/{filename}"
    #url2 = f'https://raw.githubusercontent.com/{self.owner}/{self.repo_name}/main/{filename}'
    response = requests.get(url, headers=headers)
    content = response.content
    self.set_file_info(filename, {'size' : len(content)})
    #content_2 = requests.get(url2, headers=headers).content
    #contents = [content, content_2]
    #print("checking contents", contents[0] == contents[1], filename)
    
    #cont_raw = self.repo.get_contents(filename)
    #if not cont_raw.content:
    #  return cont_raw.content
    #content_ref = cont_raw.decoded_content # bytes
  
    return content
  ###############################################################################
  def _delete_file(self, filename):
    self.repo.delete_file(filename,
                          "removing " + filename,
                          sha=self.get_file_info(filename, 'sha'))

  def _create_file_given_content(self, filename, content):
    self.repo.create_file(filename,
                          message="creating " + filename,
                          content=content)

  def _update_file_given_content(self, filename, content):
    self.repo.update_file(filename,
                          message="updating " + filename,
                          content=content,
                          sha=self.get_file_info(filename, 'sha'))

  def _create_directory(self, dirname):
    pass
    
  def _delete_directory(self, dirname):
    pass
    
  ###############################################################################
  def file_contents_is_text(self, filename):
    return None
  
  ###############################################################################
  def _fetch_stats_one_file(self, filename):
    last_modif_date = None
    if False: #fetch_github_modif_timestamps:
      # https://stackoverflow.com/questions/50194241/get-when-the-file-was-last-updated-from-a-github-repository
      #sha=self.get_file_info(filename, 'sha')
      commits = self.repo.get_commits(path=filename) # sha=sha)
      if commits.totalCount:
        last_modif_date = commits[0].commit.committer.date
      else:
        pass
        #print(f"total count is 0, filename is {filename}, sha is {sha}")
        #commits2 = self.repo.get_commits(path=filename)
        #contents = self.repo.get_contents(filename)
        #print(f"total count 2 is {commits2.totalCount}, filename is {filename}, sha is {sha}, {sha==contents.sha}")
    dict_ = {#'modified' : last_modif_date, 
             'size' : None}
    return dict_
    

  ###############################################################################

import os
from github import Github
from StorageBase import StorageBase

#################################################################################
class StorageGitHub(StorageBase):
  # For Github token, see
  # https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
  def __init__(self, token=os.environ['github_token'], repo_name="wordpress"):
    super().__init__(name='github')
    github_object = Github(token)
    github_user = github_object.get_user()
    self.repo = github_user.get_repo(repo_name)

    
  ###############################################################################
  def compare_stats_not_content(self):
    return False
  
  ###############################################################################
  # filenames and their sha's are needed to be able to update existing files, see
  # https://stackoverflow.com/questions/63435987/python-pygithub-if-file-exists-then-update-else-create
  ###############################################################################
  def _get_filenames_and_directories(self, directory: str):
    
    head = directory
    root_folders = []
    while head:
      head, tail = os.path.split(head)
      root_folders = [tail] + root_folders

    path_so_far = ''
    for rf in root_folders:
      contents_ = self.repo.get_contents(path_so_far if path_so_far else '.')
      paths_next_level = [item.path for item in contents_]
      if rf not in paths_next_level:
        return [], []
      path_so_far = os.path.join(path_so_far, rf)
        
    contents = self.repo.get_contents(directory)
    all_files, all_directories = {}, {}
    while contents:
      content_item = contents.pop(0)
      if content_item.type == "dir":
        all_directories[content_item.name] = _self._get_filenames_and_directories(directory=content_item.path)
      else:
        all_files[content_item.name] = content_item.sha

    return all_files, all_directories 
    
  ###############################################################################
  def read(self, storage_filename):
    content = self.repo.get_contents(storage_filename).decoded_content
    return content

  def _delete_file(self, storage_filename):
    self.repo.delete_file(storage_filename, "removing "+storage_filename, sha=self.cached_filenames[storage_filename])

  def create_file(self, storage_filename, content):
    self.repo.create_file(storage_filename, message="creating "+storage_filename, content=content)

  def update_file(self, storage_filename, content):
    self.repo.update_file(storage_filename, message="updating "+storage_filename, content=content, sha=self.cached_filenames[storage_filename])

  ###############################################################################
  
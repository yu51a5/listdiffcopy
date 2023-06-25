import os
from github import Github, ContentFile
from StorageBase import StorageBase

#################################################################################
class StorageGitHub(StorageBase):
  # For Github token, see
  # https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
  def __init__(self, repo_name, token=os.environ['github_token'], ):
    super().__init__(name='github')
    github_object = Github(token)
    github_user = github_object.get_user()
    self.repo = github_user.get_repo(repo_name)

    
  ###############################################################################
  def compare_stats_not_content(self):
    return False

  ###############################################################################
  def inexistent_directories_are_empty(self):
    return True
    
  ###############################################################################
  # filenames and their sha's are needed to be able to update existing files, see
  # https://stackoverflow.com/questions/63435987/python-pygithub-if-file-exists-then-update-else-create
  ###############################################################################
  def _get_filenames_and_directories(self, folderid: int, recursive : bool, path_so_far : str):
    contents = self.repo.get_contents(path_so_far)
    if isinstance(contents, ContentFile.ContentFile):
      contents = [contents]

    all_files, all_directories = {}, {}
    for content_item in contents:
      if content_item.type == "dir":
        all_directories[content_item.path] = self._get_filenames_and_directories(None, True, path_so_far=content_item.path) if recursive else None
      else:
        all_files[content_item.path] = content_item.sha
      
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


  def _create_directory(self, dirname):
    pass
  ###############################################################################
  
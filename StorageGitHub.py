import os
from datetime import datetime
from github import Github, ContentFile
from StorageBase import StorageBase

#################################################################################
class StorageGitHub(StorageBase):
  # For Github token, see
  # https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
  def __init__(self, repo_name, token=os.environ['github_token']):
    super().__init__(name='github')
    github_object = Github(token)
    github_user = github_object.get_user()
    self.repo = github_user.get_repo(repo_name)

  ###############################################################################
  def inexistent_directories_are_empty(self):
    return True

  ###############################################################################
  # filenames and their sha's are needed to be able to update existing files, see
  # https://stackoverflow.com/questions/63435987/python-pygithub-if-file-exists-then-update-else-create
  ###############################################################################
  def _get_filenames_and_directories(self, recursive: bool, path_so_far: str):
    contents = self.repo.get_contents(path_so_far)
    if isinstance(contents, ContentFile.ContentFile):
      contents = [contents]

    all_files, all_directories = [], {}
    for content_item in contents:
      if content_item.type == "dir":
        all_directories[
          content_item.path] = self._get_filenames_and_directories(
            True, path_so_far=content_item.path) if recursive else None
      else:
        all_files.append(content_item.path)
        self.cached_filenames_flat[content_item.path] = content_item.sha

    return all_files, all_directories

  ###############################################################################
  def get_contents(self, filename, length=None):
    
    cont_raw = self.repo.get_contents(filename)
    if not cont_raw.content:
      return cont_raw.content
    content = self.repo.get_contents(filename).decoded_content # bytes
    if length:
      return content[:length]
    return content

  def _delete_file(self, filename):
    self.repo.delete_file(filename,
                          "removing " + filename,
                          sha=self.cached_filenames_flat[filename])

  def _create_file_given_content(self, filename, content):
    self.repo.create_file(filename,
                          message="creating " + filename,
                          content=content)

  def _update_file_given_content(self, filename, content):
    self.repo.update_file(filename,
                          message="updating " + filename,
                          content=content,
                          sha=self.cached_filenames_flat[filename])

  def _create_directory(self, dirname):
    pass
  ###############################################################################
  def get_stats(self, filename):
    contents = self.repo.get_contents(filename)
    commits = self.repo.get_commits()
    for c in commits:
      for f in c.files:
        if f.filename == filename:
          result = {'modified' : c.last_modified, 'size' : contents.size}
          result['modified'] = datetime.strptime(result['modified'], '%a, %d %b %Y %H:%M:%S GMT')
          return result

  ###############################################################################

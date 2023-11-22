from github import Github, ContentFile, GithubException
import requests
from requests.structures import CaseInsensitiveDict

from StorageBase import StorageBase

#################################################################################
class StorageGitHub(StorageBase):
  file_size_limit = 100 << 20
  
  # github_token secret structure: OWNER|REPO|TOKEN . For Github token, see
  # https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
  def __init__(self, secret_name=None, logger_name=None, objects_to_sync_logger_with=[]):
    super().__init__(constructor_kwargs=dict(secret_name=secret_name), logger_name=logger_name, objects_to_sync_logger_with=objects_to_sync_logger_with)

    self.repo_name, self.token = self._find_secret_components(2, secret_name=secret_name)

    try:
      github_object = Github(self.token)
    except Exception as e:
      raise Exception(f"Secret {secret_name} contains invalid GitHub token, {e}")
    github_user = github_object.get_user()
    self.owner = github_user.login
    try:
      self.repo = github_user.get_repo(self.repo_name)
    except GithubException as e:
      raise Exception(f'ERROR! Repository {self.owner}/{self.repo_name} does not exist, {e}')

    self.headers = CaseInsensitiveDict()
    self.headers["Accept"] = "application/vnd.github.v3.raw"
    self.headers["Authorization"] = f"Bearer {self.token}"
    self.headers["X-GitHub-Api-Version"] = "2022-11-28"

  ###############################################################################
  def inexistent_directories_are_empty(self):
    return True

  ###############################################################################
  # filenames and their sha's are needed to be able to update existing files, see
  # https://stackoverflow.com/questions/63435987/python-pygithub-if-file-exists-then-update-else-create
  ###############################################################################
  def _get_filenames_and_directories(self, dir_name: str):
    
    all_files, all_directories = [], []
    
    exists = self.check_directory_exists(path=dir_name)

    if exists:
    
      contents = self.repo.get_contents(dir_name)
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
  def _get_contents(self, filename, length=None):

    if length:
      return bytes(b'')

    url = f"https://api.github.com/repos/{self.owner}/{self.repo_name}/contents/{filename}"
    #url2 = f'https://raw.githubusercontent.com/{self.owner}/{self.repo_name}/main/{filename}'
    response = requests.get(url, headers=self.headers)
    content = response.content

    #self.set_file_info(filename, {'size' : len(content)})
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
    assert isinstance(content, (str, bytes)), f'Type of contents is {type(content)}'
    self.repo.create_file(filename,
                          message="creating " + filename,
                          content=content)

  def _update_file_given_content(self, filename, content):
    self.repo.update_file(filename,
                          message="updating " + filename,
                          content=content,
                          sha=self.get_file_info(filename, 'sha'))

  ###############################################################################
  def _create_directory(self, dirname):
    pass

  ###############################################################################
  def _delete_directory(self, dirname):
    all_files, all_directories = self.get_filenames_and_directories(dir_name=dirname)
    for f in all_files:
      self._delete_file(filename=f)
    for d in all_directories:
      self._delete_directory(dirname=d)
    
  ###############################################################################
  def file_contents_is_text(self, filename):
    return None
  
  ###############################################################################
  #def _fetch_file_size(self, filename):
    #last_modif_date = None
    #if False: #fetch_github_modif_timestamps:
      # https://stackoverflow.com/questions/50194241/get-when-the-file-was-last-updated-from-a-github-repository
      #sha=self.get_file_info(filename, 'sha')
      #commits = self.repo.get_commits(path=filename) # sha=sha)
      #if commits.totalCount:
      #  pass # last_modif_date = commits[0].commit.committer.date
      #else:
        #print(f"total count is 0, filename is {filename}, sha is {sha}")
        #commits2 = self.repo.get_commits(path=filename)
        #contents = self.repo.get_contents(filename)
        #print(f"total count 2 is {commits2.totalCount}, filename is {filename}, sha is {sha}, {sha==contents.sha}")
    #self.get_contents(filename=filename)
    #result = self.get_file_info(filename, 'size')
    #return result

  
  ###############################################################################
  # using https://medium.com/@obodley/renaming-a-file-using-the-git-api-fed1e6f04188
  def _rename_file(self, path_to_existing_file, path_to_new_file):
    self.__please_override()
    
  ###############################################################################
  def _rename_directory(self, path_to_existing_dir, path_to_new_dir):
    self.__please_override()
    
  ###############################################################################

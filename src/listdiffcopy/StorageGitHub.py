import requests
import os
from requests.structures import CaseInsensitiveDict

from listdiffcopy.StorageBase import StorageBase

#################################################################################
class StorageGitHub(StorageBase):
  file_size_limit = 100 << 20
  inexistent_directories_are_empty = True
  
  # github_token secret structure: REPO_NAME|TOKEN . For Github token, see
  # https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
  # shortcut: https://github.com/settings/tokens?type=beta
  # expiration: 1 year
  # repositories - select one where the contents will be stored
  # repo permissions: read metadata (default); read and write contents
  # "API rate limit exceeded for user ID 123456789. 
  # If you reach out to GitHub Support for help, please include the request ID 123:123:123:123:123.
  # documentation_url": "https://docs.github.com/rest/overview/rate-limits-for-the-rest-api"
  def __init__(self, secret_name=None, logger_name=None, objects_to_sync_logger_with=[]):
    super().__init__(constructor_kwargs=dict(secret_name=secret_name), logger_name=logger_name, objects_to_sync_logger_with=objects_to_sync_logger_with)

    repo_name, self.token = self._find_secret_components(2, secret_name=secret_name)

    try:
      github_object = Github(self.token)
    except Exception as e:
      raise Exception(f"Secret {secret_name} contains invalid GitHub token, {e}")
    github_user = github_object.get_user()
    owner = github_user.login
    try:
      self.repo = github_user.get_repo(repo_name)
    except Exception as e:
      raise Exception(f'ERROR! Repository {owner}/{repo_name} does not exist, {e}')

    self.url_head =  f"https://api.github.com/repos/{owner}/{repo_name}"
    self.branch_name = "MASTER"

    self.headers = CaseInsensitiveDict()
    self.headers["Accept"] = "application/vnd.github.v3.raw"
    self.headers["Authorization"] = f"Bearer {self.token}"
    self.headers["X-GitHub-Api-Version"] = "2022-11-28"

  ###############################################################################
  # filenames and their sha's are needed to be able to update existing files, see
  # https://stackoverflow.com/questions/63435987/python-pygithub-if-file-exists-then-update-else-create
  ###############################################################################
  def _get_filenames_and_directories(self, path: str):
    
    all_files, all_directories = [], []
    
    exists = self.check_directory_exists(path=path)

    if exists:

      url = f"{self.url_head}/git/trees/({self.branch_name}):({path})"
      
      contents = self.repo.get_contents(path)
      if isinstance(contents, ContentFile.ContentFile):
        contents = [contents]
  
      for content_item in contents:
        if content_item.type == "dir":
          all_directories.append(content_item.path)
        else:
          all_files.append(content_item.path)
          #self.set_file_info(content_item.path, {'sha' : content_item.sha})

    return all_files, all_directories

  ###############################################################################
  def get_file_id(self, path):
    dir_name = os.path.dirname(path)
    exists = self.check_directory_exists(path=dir_name)
    if exists:
      contents = self.repo.get_contents(dir_name)
      for content_item in contents:
        if path == content_item.path:
          return content_item.sha if content_item.type != "dir" else None
    return None

  ###############################################################################
  def _read_file(self, path, length=None):

    if length:
      return bytes(b'')

    url = f"{self.url_head}/contents/{path}"
    #url2 = f'https://raw.githubusercontent.com/{self.owner}/{self.repo_name}/main/{filename}'
    response = requests.get(url, headers=self.headers)
    content = response.content

    #self.set_file_info(filename, {'size' : len(content)})
    #content_2 = requests.get(url2, headers=headers).content
    #contents = [content, content_2]
    #print("checking contents", contents[0] == contents[1], filename)
    
    #cont_raw = self.repo.get_content(filename)
    #if not cont_raw.content:
    #  return cont_raw.content
    #content_ref = cont_raw.decoded_content # bytes
  
    return content
  ###############################################################################
  def _delete_file(self, filename):
    self.repo.delete_file(filename,
                          "removing " + filename,
                          sha=self.get_file_id(filename))

  def _create_file_given_content(self, path, content):
    self.repo.create_file(path,
                          message="creating " + path,
                          content=content)

  def _update_file_given_content(self, path, content):
    self.repo.update_file(path,
                          message="updating " + path,
                          content=content,
                          sha=self.get_file_id(path))

  ###############################################################################
  def _create_directory_only(self, path):
    pass

  ###############################################################################
  def _delete_directory(self, path):
    self._delete_directory_contents(path=path)
    
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
        #contents = self.repo.get_content(filename)
        #print(f"total count 2 is {commits2.totalCount}, filename is {filename}, sha is {sha}, {sha==contents.sha}")
    #self.read_file(filename=filename)
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

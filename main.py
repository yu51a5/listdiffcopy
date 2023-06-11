import os
from helpers import get_ssh_client, get_github_repo, get_github_repo_filenames_sha

repo = get_github_repo(token=os.environ['github_token'], repo_name="wordpress")

# creating a folder using pygithub - see https://stackoverflow.com/questions/60815076/how-to-create-a-new-directory-in-a-repo-using-pygithub
with get_ssh_client(**{what: os.environ[f'sftp_{what}'] for what in ('hostname', 'port', 'username', 'password', 'private_key')}) as ssh_client:
  with ssh_client.open_sftp() as sftp_client:
    for sftp_dir, github_dir in (('www/yu51a5.org/public_html/wp-content/themes/pinboard-child', 'pinboard-child'), ):
      all_existing_files = get_github_repo_filenames_sha(repo=repo, dir=github_dir)
      for filename in sftp_client.listdir(sftp_dir):
        with sftp_client.open(sftp_dir+"/"+filename) as remote_file:
          contents = remote_file.read()
          github_filename = github_dir+'/'+filename
          if filename not in all_existing_files:
            repo.create_file(github_filename, message="creating "+filename, content=contents)
          else:
            current_content = repo.get_contents(github_filename)
            if current_content.decoded_content != contents: # only update in the new file is diffenent
              repo.update_file(github_filename, message="updating "+filename, content=contents, sha=all_existing_files[filename])
      
print("all done!")

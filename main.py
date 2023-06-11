import os
from helpers import get_ssh_client, get_repo_and_its_filenames_sha


ssh_client = get_ssh_client(**{what: os.environ[f'sftp_{what}'] for what in ('hostname', 'port', 'username', 'password', 'private_key')})

sftp = ssh_client.open_sftp()
for filename in sftp.listdir('www/yu51a5.org/public_html/wp-content/themes/pinboard-child'):
    print(filename)
  
ssh_client.close()

repo, all_existing_files = get_repo_and_its_filenames_sha(token=os.environ['github_token'], repo_name="wordpress")

for filename, contents in [["hw.txt", "Hello, world!!!!!!!!"], ["a.txt", "a, a!!!"]]:
  if filename not in all_existing_files:
    repo.create_file(filename, message="Test", content=contents)
  else:
    repo.update_file(filename, message="Test", content=contents, sha=all_existing_files[filename])

print(all_existing_files)
print("hi yu")
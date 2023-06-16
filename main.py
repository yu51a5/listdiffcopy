import os
from helpers import get_ssh_client, get_github_repo, get_github_repo_filenames_sha

repo = get_github_repo(token=os.environ['github_token'], repo_name="wordpress")

sftp_github_folders_pairs = os.environ['sftp_github_folders'].split(';')
sftp_github_folders = [gsp.split(',') for gsp in sftp_github_folders_pairs]

# creating a folder using pygithub - see https://stackoverflow.com/questions/60815076/how-to-create-a-new-directory-in-a-repo-using-pygithub
with get_ssh_client() as ssh_client:
  with ssh_client.open_sftp() as sftp_client:
    # backing up to GitHub
    for sftp_dir, github_dir in sftp_github_folders:
      all_github_files = get_github_repo_filenames_sha(repo=repo, dir=github_dir)
      all_sftp_files = sorted(sftp_client.listdir(sftp_dir))
      # removing the files in github repo that are no longer on SFTP server
      for filename in all_github_files:
        if filename not in all_sftp_files:
          github_filename = github_dir+'/'+filename
          repo.delete_file(github_filename, "removing "+filename, sha=all_github_files[filename])
          print('removed '+ github_filename)
      # for all files on SFTP server ...
      for filename in all_sftp_files:
        with sftp_client.open(sftp_dir+"/"+filename) as sftp_file:
          sftp_contents = sftp_file.read()
          github_filename = github_dir+'/'+filename
          # ... either create a new, if it's not on github ...
          if filename not in all_github_files:
            print('created '+ github_filename)
            repo.create_file(github_filename, message="creating "+filename, content=sftp_contents)
          # ... or update an existing file ...
          else:
            current_github_content = repo.get_contents(github_filename).decoded_content
            if current_github_content != sftp_contents: # ... but only if the new file is diffenent
              print('updated '+ github_filename)
              repo.update_file(github_filename, message="updating "+filename, content=sftp_contents, sha=all_github_files[filename])
    # backing up to a file
    for sftp_dir, file_repo_dir in (('www/yu51a5.org/public_html/wp-content/themes/pinboard-child', 'pinboard-child'), ('www/yu51a5.org/backup', 'posts')):
      pass

      
print("all done!")

import os 
import requests
from StorageGitHub import StorageGitHub
from StoragePCloud import StoragePCloud

pcloud = StoragePCloud(is_eapi=True)
pcloud._get_filenames_and_directories('a')

storage = StorageGitHub()
#backup(storage)
      
print("all done!")

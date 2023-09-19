import os
import math
import pandas as pd
import numpy as np

from SomeAction import SomeAction, creates_multi_index

#################################################################################
class SomeAction2(SomeAction):

  create_if_left_only = None
  delete_if_right_only = None
  change_if_both = None

  enter_123 = [None, None, None]
  
  #################################################################################
  def __init__(self, StorageFromType, dir_from, StorageToType, dir_to, require_dir_to=True, kwargs_from={}, kwargs_to={}, **kwargs):
    self.root_dir_from = dir_from
    self.root_dir_to = dir_to

    self.index_comp_df = pd.MultiIndex.from_tuples(creates_multi_index(self.index_listing_df, self.status_names))

    with StorageFromType(**kwargs_from) as self.storage_from:
      if (StorageFromType == StorageToType) and (kwargs_from == kwargs_to):
        self.storage_to = self.storage_from 
        self.__common_part_of_constructor(dir_from=dir_from, dir_to=dir_to, require_dir_to=require_dir_to)
      else:
        with StorageToType(**kwargs_to) as self.storage_to: 
          self.__common_part_of_constructor(dir_from=dir_from, dir_to=dir_to, require_dir_to=require_dir_to)

  ###############################################################################
  def __common_part_of_constructor(self, dir_from, dir_to, require_dir_to):
    if require_dir_to:
      storages_dirs_that_must_exist = ((self.storage_from, dir_from), (self.storage_to, dir_to))
    else:
      storages_dirs_that_must_exist = ((self.storage_from, dir_from), )
      self.storage_to.create_directory(dir_to)
      
    super().__init__(title=f'{self.enter_123[0]} {self.storage_from.str(dir_from)} {self.enter_123[2]} {self.storage_to.str(dir_to)}',
                     storages_dirs_that_must_exist=storages_dirs_that_must_exist)
    if self.dir_exists():
      self._action_files_directories_recursive(common_dir_appendix='')

  ###############################################################################
  def _action_files_directories_recursive(self, common_dir_appendix):
  
    self.log_enter_level(common_dir_appendix, self.enter_123[0])

    _dir_from = os.path.join(self.root_dir_from, common_dir_appendix) if common_dir_appendix else self.root_dir_from
    files_from, dirs_from, _ = self.storage_from.get_filenames_and_directories(_dir_from, enforce_size_fetching=True)
    _dir_to = os.path.join(self.root_dir_to, common_dir_appendix) if common_dir_appendix else self.root_dir_to
    files_to  , dirs_to  , _ = self.storage_to.get_filenames_and_directories(_dir_to, enforce_size_fetching=True)
  
    dir_info_first_level = np.zeros((4, 3), float)
    dir_info_total = np.zeros((4, 3), float)
    # dir_info_first_level[3][0] = math.nan # no information about deleted files' size 
    
    if_from = -len(files_from)
    if_to = -len(files_to)
    files_data = []
    
    while (if_from < 0) or (if_to < 0):
      if if_from < 0:
        file_from = files_from[if_from]
        basename_from = os.path.basename(file_from)
      if if_to < 0:
        file_to   = files_to[  if_to]
        basename_to   = os.path.basename(file_to)
        
      filename, status, file_size = None, None, math.nan
      if (if_to == 0) or ((if_from != 0) and (basename_from < basename_to)):
        status, filename = 0, basename_from
        if self.create_if_left_only:
          file_size = self.storage_to.create_file(my_filename=os.path.join(_dir_to, basename_from), 
                                             source=self.storage_from, 
                                             source_filename=file_from)
          
        if_from += 1
      elif (if_from == 0) or (basename_to < basename_from):
        if self.delete_if_right_only:
          self.storage_to._delete_file(file_to)
        status, filename = 1, basename_to
        if_to += 1  
      elif (basename_from == basename_to):
        if_from += 1
        if_to += 1
        files_are_identical, from_contents = self.storage_from.check_if_files_are_identical(my_filename=file_from, 
                                                                             source=self.storage_to, 
                                                                             source_filename=file_to)
        if (not files_are_identical) and self.change_if_both:
          if from_contents is None:
            from_contents = self.storage_from.get_contents(file_from) 
          self.storage_to._update_file_given_content(filename=file_to, content=from_contents)
        file_size = len(from_contents) 
        status, filename = 3 if files_are_identical else 2, basename_to
        
      dir_info_first_level[status][1] += 1
      dir_info_first_level[status][0] += file_size
      files_data.append([filename, file_size, status])
  
    self.print_files_df(data=files_data)
  
    id_from = -len(dirs_from)
    id_to = -len(dirs_to)
  
    while ((id_from < 0) or (id_to < 0)):
      if id_from < 0:
        dir_from = dirs_from[id_from]
        basename_from = os.path.basename(dir_from)
      if id_to < 0:
        dir_to   = dirs_to[  id_to]
        basename_to   = os.path.basename(dir_to)
      if (id_to == 0) or (basename_from < basename_to):
        dir_info_first_level[0][2] += 1
        if self.create_if_left_only:
          self.storage_to.create_directory_in_existing_folder(path=os.path.join(_dir_to, basename_from))
          subdir_info_total = self._action_files_directories_recursive(common_dir_appendix=os.path.join(common_dir_appendix, basename_from))
          dir_info_total += subdir_info_total
        else:
          subdir_list_total, _, _ = self._list_files_directories_recursive(storage=self.storage_from, dir_to_list=dir_from, message2=f"Exists in {_dir_from} but not in {_dir_to}", enforce_size_fetching=False) 
          dir_info_total[0] += subdir_list_total
        id_from += 1
      elif (id_from == 0) or (basename_to < basename_from):
        dir_info_first_level[1][2] += 1
        if self.delete_if_right_only:
          self.log_mention_directory(dirname=dir_to, message_to_print="Deleting", message2=f"in {self.storage_to.str(_dir_to)}")
          self.storage_to._delete_directory(dir_to)
          dir_info_first_level[1] += np.array([math.nan] * 3)
        else:
          subdir_list_total, _, _ = self._list_files_directories_recursive(storage=self.storage_to, dir_to_list=dir_to, message2=f"Exists in {_dir_to} but not in {_dir_from}", enforce_size_fetching=False)
          dir_info_total[1] += subdir_list_total
        id_to += 1  
      elif (basename_from == basename_to):
        id_from += 1
        id_to += 1
        
        subdir_info_total = self._action_files_directories_recursive(common_dir_appendix=os.path.join(common_dir_appendix, basename_from))
        dir_info_total += subdir_info_total
        is_identical = not any([any([c for c in s if c and c != math.nan]) for s in subdir_info_total[:-1]])
        dir_info_first_level[3 if is_identical else 2][2] += 1

    dir_info_total += dir_info_first_level
  
    self.log_exit_level(dir_details_df=pd.DataFrame(np.vstack((dir_info_first_level, dir_info_total)), index=self.index_comp_df, columns=self.columns_df))
    return dir_info_total


#################################################################################
class Compare(SomeAction2):

  create_if_left_only = False
  delete_if_right_only = False
  change_if_both = False
  
  status_names = ["Left Only", "Right Only", "Different", "Identical"]

  enter_123 = ['Comparing', 'in', 'against']
  
  #################################################################################
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

#################################################################################
def compare(*args, **kwargs):
  Compare(*args, **kwargs)

#################################################################################
class Copy(SomeAction2):

  create_if_left_only = True
  delete_if_right_only = False
  change_if_both = True

  enter_123 = ['Copying', 'from', 'to']

  status_names = ["New", "Pre-existing", "Updated", "Identical"]
  
  #################################################################################
  def __init__(self, *args, **kwargs):
    super().__init__(*args, require_dir_to=False, **kwargs)
    
#################################################################################
def copy(*args, **kwargs):
  with Copy(*args, **kwargs) as _:
    pass

#################################################################################
class Synchronize(SomeAction2):

  create_if_left_only = True
  delete_if_right_only = True
  change_if_both = True

  enter_123 = ['Synchronizing', 'in', 'with']

  status_names = ["New", "Deleted", "Updated", "Identical"]
  
  #################################################################################
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

#################################################################################
def synchronize(*args, **kwargs):
  with Synchronize(*args, **kwargs) as _:
    pass
  
import os
import math
import pandas as pd
import numpy as np

from SomeAction import SomeAction, creates_multi_index

#################################################################################
class SomeAction2(SomeAction):

  create_if_left_only = None
  delete_if_right_only = None
  change_if_both_exist = None

  is_renaming = None
  is_move_not_copy = None
  is_file_not_dir = None
  require_path_to = None

  enter_123 = [None, None, None]
  
  #################################################################################
  def __init__(self, path_from, path_to, storage_from=None, storage_to=None, StorageFromType=None, StorageToType=None, kwargs_from={}, kwargs_to={}):
    self.root_path_from = path_from
    self.root_path_to = path_to

    self.index_comp_df = pd.MultiIndex.from_tuples(creates_multi_index(self.index_listing_df, self.status_names))

    errors = []
    if (storage_from is None) == (StorageFromType is None):
      errors.append(f"storage_from {storage_from} and StorageFromType {StorageFromType} mustn't be both None or both not None")
    if (StorageFromType is None) and kwargs_from:
      errors.append(f"StorageFromType is not provided, but arguments {kwargs_from} are")
    if (storage_to is None) == (StorageToType is None):
      errors.append(f"storage_from {storage_to} and StorageToType {StorageToType} mustn't be both None or both not None")
    if (StorageToType is None) and kwargs_to:
      errors.append(f"StorageToType is not provided, but arguments {kwargs_to} are")

    assert not errors, '.\n'.join(['ERRORS:'] + errors)

    self.storage_from = storage_from if storage_from else None
    self.storage_to   = storage_to   if storage_to   else None

    if self.storage_from and not self.storage_to and StorageToType == type(self.storage_from) and kwargs_to == self.storage_from.get_constructor_kwargs():
      self.storage_to = self.storage_from
    if self.storage_to and not self.storage_from and StorageFromType == type(self.storage_to) and kwargs_from == self.storage_to.get_constructor_kwargs():
      self.storage_from = self.storage_to

    if self.storage_to and self.storage_from:
      self.__common_part_of_constructor()
    elif self.storage_to and (not self.storage_from):
      with StorageFromType(**kwargs_from) as self.storage_from:
        self.__common_part_of_constructor()
    elif self.storage_from and (not self.storage_to):
      with StorageToType(**kwargs_to) as self.storage_to:
        self.__common_part_of_constructor()
    else:
      with StorageFromType(**kwargs_from) as self.storage_from:
        with StorageToType(**kwargs_to) as self.storage_to: 
          self.__common_part_of_constructor()

  ###############################################################################
  def __common_part_of_constructor(self):

    self.storage_from._logger = self
    self.storage_to._logger = self

    str_from = self.storage_from.str(self.root_path_from)
    str_to = self.storage_to.str(self.root_path_to)

    super().__init__(title=f'{self.enter_123[0]} {str_from} {self.enter_123[2]} {str_to}')
    
    path_exist_is_dir_not_file_from = self.storage_from.check_path_exist_is_dir_not_file(self.root_path_from)
    path_exist_is_dir_not_file_to = self.storage_to.check_path_exist_is_dir_not_file(self.root_path_to)
    
    if path_exist_is_dir_not_file_from is None:
      self.log_error(f"{str_from} does not exist")
    elif (path_exist_is_dir_not_file_from == 'both'):
      if path_exist_is_dir_not_file_to == 'both':
        self.log_error(f"Both {str_from} and {str_to} are both a directory and a file")
      elif path_exist_is_dir_not_file_to is None:
        self.log_error(f"{str_from} is both a directory and a file, and {str_to} does not exist")
        return
      else:
        # make path_exist_is_dir_not_file_from either True or False
        path_exist_is_dir_not_file_from = path_exist_is_dir_not_file_to
    elif path_exist_is_dir_not_file_to == 'both':
      path_exist_is_dir_not_file_to = path_exist_is_dir_not_file_to

    # now path_exist_is_dir_not_file_from is either True or False
    # now path_exist_is_dir_not_file_to is either True or False or None

    if path_exist_is_dir_not_file_to is None:
      if self.require_path_to:
        self.log_error(f"{str_to} does not exist")
      elif path_exist_is_dir_not_file_from is True:
        self.storage_to.create_directory(self.root_path_to)
        path_exist_is_dir_not_file_to = True
        
    if (path_exist_is_dir_not_file_from in [True, False]) and (path_exist_is_dir_not_file_to in [True, False]) and (path_exist_is_dir_not_file_from is not path_exist_is_dir_not_file_to):
      self.log_error(f"{str_from} is a {'directory' if path_exist_is_dir_not_file_from else 'file'} whereas {str_to} is a {'directory' if path_exist_is_dir_not_file_to else 'file'} ")

    if self.get_errors_count():
      return
    
    if path_exist_is_dir_not_file_from:
      self._action_files_directories_recursive(common_dir_appendix='')
    else:
      self._action_files(file_from=self.root_path_from, file_to=self.root_path_to, file_to_doesnt_exist=(path_exist_is_dir_not_file_to is None), add_basename=False)

  ###############################################################################
  def _action_files(self, file_from, file_to, file_to_doesnt_exist, add_basename, enforce_size_fetching):

    basename = os.path.basename(file_from if file_from is not None else file_to)
    if add_basename:
      assert file_from is not None
    file_to_2 = file_to if not add_basename else os.path.join(file_to, basename)

    file_size = math.nan
    if file_to_doesnt_exist:
      status = 0
      if self.create_if_left_only:
        file_size = self.storage_to.create_file(my_filename=file_to_2,
                                                 source=self.storage_from, 
                                                 source_filename=file_from)
    elif file_from is None:
      if self.delete_if_right_only:
        self.storage_to._delete_file(file_to)
      status = 1 
    else:
      files_are_identical, from_contents = self.storage_from.check_if_files_are_identical(my_filename=file_from, 
                                                                               source=self.storage_to, 
                                                                               source_filename=file_to_2)
        
      if (not files_are_identical) and self.change_if_both_exist:   
        from_contents = self.storage_from.get_contents(file_from) 
        self.storage_to._update_file_given_content(filename=file_to_2, content=from_contents)
      elif enforce_size_fetching:
        from_contents = self.storage_from.get_contents(file_from) 
      else:
        from_contents = None
        
      file_size = len(from_contents) if from_contents is not None else math.nan
      status = 3 if files_are_identical else 2
      
    return basename, file_size, status
    
  ###############################################################################
  def _action_files_directories_recursive(self, common_dir_appendix):
  
    self.log_enter_level(common_dir_appendix, self.enter_123[0])

    _dir_from = os.path.join(self.root_path_from, common_dir_appendix) if common_dir_appendix else self.root_path_from
    files_from, dirs_from, _ = self.storage_from.get_filenames_and_directories(_dir_from, enforce_size_fetching=True)
    _dir_to = os.path.join(self.root_path_to, common_dir_appendix) if common_dir_appendix else self.root_path_to
    files_to  , dirs_to  , _ = self.storage_to.get_filenames_and_directories(_dir_to, enforce_size_fetching=True)

    print('_dir_from', _dir_from, type(self.storage_from))
    print('files_from', files_from)
    print('files_to', files_to)
    print('_dir_to', _dir_to)
  
    dir_info_first_level = np.zeros((4, 3), float)
    dir_info_total = np.zeros((4, 3), float)
    # dir_info_first_level[3][0] = math.nan # no information about deleted files' size 
    
    if_from = -len(files_from)
    if_to = -len(files_to)
    files_data = []
    
    while (if_from < 0) or (if_to < 0):
      
      file_from = files_from[if_from] if if_from < 0 else None
      file_to   = files_to[  if_to]   if if_to < 0   else None

      if (file_from is not None) and (file_to is not None):
        basename_from = os.path.basename(file_from)
        basename_to   = os.path.basename(file_to)
        if basename_from < basename_to:
          file_to = None
        if basename_to < basename_from:
          file_from = None

      if (file_from is not None):
        if_from += 1      
      if (file_to is not None):
        if_to   += 1   
        
      filename = os.path.basename(file_from if file_from is not None else file_to)
      file_size = math.nan
      if file_to is None:
        status = 0
        if self.create_if_left_only:
          file_size = self.storage_to.create_file(my_filename=os.path.join(_dir_to, basename_from), 
                                                   source=self.storage_from, 
                                                   source_filename=file_from)
      elif file_from is None:
        if self.delete_if_right_only:
          self.storage_to._delete_file(file_to)
        status = 1 
      else:
        files_are_identical, file_size = self._compare_or_copy_files(file_from=file_from, file_to=file_to)
        status = 3 if files_are_identical else 2
        
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
          self.storage_to.create_directory_in_existing_directory(path=os.path.join(_dir_to, basename_from))
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
  change_if_both_exist = False
  require_path_to = True
  
  status_names = ["Left Only", "Right Only", "Different", "Identical"]

  enter_123 = ['Comparing', '', 'against']
  
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
  change_if_both_exist = True
  require_path_to = False

  enter_123 = ['Copying', 'from', 'to']

  status_names = ["New", "Pre-existing", "Updated", "Identical"]
  
  #################################################################################
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
#################################################################################
def copy(*args, **kwargs):
  with Copy(*args, **kwargs) as _:
    pass

def copy_and_rename(*args, **kwargs):
  with Copy(*args, **kwargs) as _:
    pass

def move(*args, **kwargs):
  with Copy(*args, **kwargs) as _:
    pass

def move_and_rename(*args, **kwargs):
  with Copy(*args, **kwargs) as _:
    pass
    
#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.

def copy_file(*args, **kwargs):
  with Copy(*args, **kwargs) as _:
    pass

def copy_file_and_rename(*args, **kwargs):
  with Copy(*args, **kwargs) as _:
    pass

def move_file(*args, **kwargs):
  with Copy(*args, **kwargs) as _:
    pass

def move_file_and_rename(*args, **kwargs):
  with Copy(*args, **kwargs) as _:
    pass

#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.

def copy_directory(*args, **kwargs):
  with Copy(*args, **kwargs) as _:
    pass

def copy_directory_and_rename(*args, **kwargs):
  with Copy(*args, **kwargs) as _:
    pass

def move_directory(*args, **kwargs):
  with Copy(*args, **kwargs) as _:
    pass

def move_directory_and_rename(*args, **kwargs):
  with Copy(*args, **kwargs) as _:
    pass

#################################################################################
class Synchronize(SomeAction2):

  create_if_left_only = True
  delete_if_right_only = True
  change_if_both_exist = True
  require_path_to = False

  enter_123 = ['Synchronizing', '', 'with']

  status_names = ["New", "Deleted", "Updated", "Identical"]
  
  #################################################################################
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

#################################################################################
def synchronize(*args, **kwargs):
  with Synchronize(*args, **kwargs) as _:
    pass
  
import os
import math
import pandas as pd
import numpy as np

from utils import creates_multi_index
from ObjectWithLogger import FDStatus, ObjectWithLogger
from StorageBase import StorageBase

#################################################################################
class Action2(ObjectWithLogger):

  create_if_left_only = None
  delete_if_right_only = None
  change_if_both_exist = None

  is_renaming = None
  is_move_not_copy = None
  is_file_not_dir = None
  require_path_to = None

  enter_123 = [None, None, None]

  #################################################################################
  def __init__(self, path_from, path_to, storage_from=None, storage_to=None, StorageFromType=None, StorageToType=None, kwargs_from={}, kwargs_to={}, **kwargs):
    self.root_path_from = path_from
    self.root_path_to = path_to

    self.index_comp_df = pd.MultiIndex.from_tuples(creates_multi_index(self.index_listing_df, self.status_names))

    errors = StorageBase._check_storage_or_type(storage=storage_from, StorageType=StorageFromType, kwargs=kwargs_from) \
           + StorageBase._check_storage_or_type(storage=storage_to  , StorageType=StorageToType  , kwargs=kwargs_to)

    if errors:
      self.log_critical(errors)

    self.storage_from = storage_from if storage_from else None
    self.storage_to   = storage_to   if storage_to   else None

    if self.storage_from and not self.storage_to and StorageToType == type(self.storage_from) and self.storage_from.check_if_constructor_kwargs_are_the_same(kwargs_to):
      self.storage_to = self.storage_from
    if self.storage_to and not self.storage_from and StorageFromType == type(self.storage_to) and self.storage_to.check_if_constructor_kwargs_are_the_same(kwargs_from):
      self.storage_from = self.storage_to

    if self.storage_to and self.storage_from:
      self.__common_part_of_constructor(**kwargs)
    elif self.storage_to and (not self.storage_from):
      with StorageFromType(**kwargs_from, objects_to_sync_logger_with=[self.storage_to]) as self.storage_from:
        self.__common_part_of_constructor(**kwargs)
    elif self.storage_from and (not self.storage_to):
      with StorageToType(**kwargs_to, objects_to_sync_logger_with=[self.storage_from]) as self.storage_to:
        self.__common_part_of_constructor(**kwargs)
    else:
      with StorageFromType(**kwargs_from) as self.storage_from:
        if StorageFromType == StorageToType and kwargs_from == kwargs_to:
          self.storage_to = self.storage_from
          self.__common_part_of_constructor(**kwargs)
        else:
          with StorageToType(**kwargs_to, objects_to_sync_logger_with=[self.storage_from]) as self.storage_to: 
            self.__common_part_of_constructor(**kwargs)

  #################################################################################
  def _put_title_together(self):
    title = f'{self.enter_123[0]} {self.storage_from.str(self.root_path_from)} {self.enter_123[2]} {self.storage_to.str(self.root_path_to)}'
    return title

  ###############################################################################
  def __common_part_of_constructor(self):

    super().__init__(title = self._put_title_together(), objects_to_sync_logger_with=[self.storage_from, self.storage_to])

    str_from = self.storage_from.str(self.root_path_from)
    str_to = self.storage_to.str(self.root_path_to)
    
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
        self.storage_to._create_directory(self.root_path_to)
        path_exist_is_dir_not_file_to = True
        
    if (path_exist_is_dir_not_file_from in [True, False]) and (path_exist_is_dir_not_file_to in [True, False]) and (path_exist_is_dir_not_file_from is not path_exist_is_dir_not_file_to):
      self.log_error(f"{str_from} is a {'directory' if path_exist_is_dir_not_file_from else 'file'} whereas {str_to} is a {'directory' if path_exist_is_dir_not_file_to else 'file'} ")

    if self.get_errors_count():
      return
    
    if path_exist_is_dir_not_file_from:
      self._action_files_directories_recursive(common_dir_appendix='')
    else:
      self._action_files(file_from=self.root_path_from, file_to=self.root_path_to, 
                         file_from_doesnt_exist=(path_exist_is_dir_not_file_from is None), 
                         file_to_doesnt_exist  =(path_exist_is_dir_not_file_to   is None), add_basename=False)

  ###############################################################################
  def _action_files(self, file_from, file_to, file_from_doesnt_exist, file_to_doesnt_exist, add_basename):
    basename = os.path.basename(file_from if file_from is not None else file_to)
    size_from, size_to, status = math.nan, math.nan, FDStatus.Error
    try:
      assert (file_from is not None) or (not add_basename)
      file_to_2 = file_to if (not add_basename) or not(basename) else os.path.join(file_to, basename)

      if not file_from_doesnt_exist:
        assert file_from

      if not file_to_doesnt_exist:
        assert file_to
        assert file_to_2, file_to
  
      if file_to_doesnt_exist:
        status = FDStatus.LeftOnly_or_New
        if self.create_if_left_only:
          from_contents = self.storage_from.get_contents(file_from) 
          self.storage_to.create_file_given_content(filename=file_to_2, content=from_contents) 
          size_from = len(from_contents)
          size_to = size_from
        else:
          size_from, _ = self.storage_from.get_file_size_or_contents(filename=file_from)
          size_to   = 0
      elif file_from_doesnt_exist:
        status = FDStatus.RightOnly_or_Deleted
        if self.delete_if_right_only:
          self.storage_to._delete_file(file_to_2)
          size_from, size_to = 0, 0
        else:
          size_from = 0
          size_to, _ = self.storage_to.get_file_size_or_contents(filename=file_to_2)
      else:
        if self.change_if_both_exist:
          from_contents = self.storage_from.get_contents(file_from) 
          assert file_to_2 is not None
          status = self.storage_to.create_file_given_content(filename=file_to_2, content=from_contents) 
          size_from = len(from_contents)
          size_to = size_from
        else:
          size_from, cont_from = self.storage_from.get_file_size_or_contents(filename=file_from)
          size_to, cont_to = self.storage_to.get_file_size_or_contents(filename=file_to_2)
          if size_from != size_to:
            status = FDStatus.Different_or_Updated
          else:
            if cont_from is None:
              cont_from = self.storage_from.get_contents(file_from) 
            if cont_to is None:
              cont_to = self.storage_to.get_contents(file_to_2) 
            status = FDStatus.Different_or_Updated if cont_from != cont_to else FDStatus.Identical
    except:
      self.log_error(f'{self.enter_123[0]} {self.enter_123[1]} {self.storage_from.str(file_from)} {self.storage_to.str(file_to)} {self.enter_123[1]} failed')
    
    return [basename, size_from, size_to, status]
    
  ###############################################################################
  def _action_files_directories_recursive(self, common_dir_appendix):
  
    self.log_enter_level(common_dir_appendix, self.enter_123[0])

    _dir_from = os.path.join(self.root_path_from, common_dir_appendix) if common_dir_appendix else self.root_path_from
    files_from, dirs_from = self.storage_from.get_filenames_and_directories(_dir_from)
    _dir_to = os.path.join(self.root_path_to, common_dir_appendix) if common_dir_appendix else self.root_path_to
    files_to  , dirs_to   = self.storage_to.get_filenames_and_directories(_dir_to)
  
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
        basename = min(os.path.basename(file_from), os.path.basename(file_to))
        if os.path.basename(file_to) > basename:
          file_to = None
        if os.path.basename(file_from) > basename:
          file_from = None
      elif (file_from is not None) and (file_to is None):
        basename = os.path.basename(file_from)
      elif (file_from is None) and (file_to is not None):
        basename = os.path.basename(file_to)
      else:
        basename = None

      if (file_from is not None):
        if_from += 1      
      if (file_to is not None):
        if_to   += 1  
      else:
        file_to = os.path.join(_dir_from, basename)

      this_file_result = self._action_files(file_from=file_from, 
                                            file_to=file_to, 
                                            file_from_doesnt_exist=(file_from is None), 
                                            file_to_doesnt_exist=(file_to is None), 
                                            add_basename=False)

      status = this_file_result[-1].value
      dir_info_first_level[status][1] += 1
      dir_info_first_level[status][0] += this_file_result[1]
      files_data.append(this_file_result)
  
    self.print_files_df(data=files_data)
  
    id_from = -len(dirs_from)
    id_to = -len(dirs_to)
  
    while ((id_from < 0) or (id_to < 0)):
      if id_from < 0:
        dir_from = dirs_from[id_from]
        basename_from = os.path.basename(dir_from)
      else:
        basename_from = None
      if id_to < 0:
        dir_to   = dirs_to[  id_to]
        basename_to   = os.path.basename(dir_to)
      else:
        basename_to = None
      if (id_to == 0) or ((basename_from is not None) and (basename_to is not None) and (basename_from < basename_to)):
        dir_info_first_level[0][2] += 1
        if self.create_if_left_only:
          self.storage_to.create_directory_in_existing_directory(path=os.path.join(_dir_to, basename_from))
          subdir_info_total = self._action_files_directories_recursive(common_dir_appendix=os.path.join(common_dir_appendix, basename_from))
          dir_info_total += subdir_info_total
        else:
          subdir_list_total, _, _ = self.storage_from._list_files_directories_recursive(dir_to_list=dir_from, message2=f"Exists in {_dir_from} but not in {_dir_to}", enforce_size_fetching=False) 
          dir_info_total[0] += subdir_list_total
        id_from += 1
      elif (id_from == 0) or ((basename_from is not None) and (basename_to is not None) and (basename_to < basename_from)):
        dir_info_first_level[1][2] += 1
        if self.delete_if_right_only:
          self.log_mention_directory(dirname=dir_to, message_to_print="Deleting", message2=f"in {self.storage_to.str(_dir_to)}")
          self.storage_to._delete_directory(dir_to)
          dir_info_first_level[1] += np.array([math.nan] * 3)
        else:
          subdir_list_total, _, _ = self.storage_to._list_files_directories_recursive(dir_to_list=dir_to, message2=f"Exists in {_dir_to} but not in {_dir_from}", enforce_size_fetching=False)
          dir_info_total[1] += subdir_list_total
        id_to += 1  
      elif ((basename_from is not None) and (basename_to is not None) and (basename_from == basename_to)):
        id_from += 1
        id_to += 1
        
        subdir_info_total = self._action_files_directories_recursive(common_dir_appendix=os.path.join(common_dir_appendix, basename_from))
        dir_info_total += subdir_info_total
        is_identical = not any([any([c for c in s if c and c != math.nan]) for s in subdir_info_total[:-1]])
        dir_info_first_level[3 if is_identical else 2][2] += 1
      else:
        self.log_critical("Algo bug")

    dir_info_total += dir_info_first_level
  
    self.log_exit_level(dir_details_df=pd.DataFrame(np.vstack((dir_info_first_level, dir_info_total)), index=self.index_comp_df, columns=self.columns_df))
    return dir_info_total


#################################################################################
class Compare(Action2):

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
class Copy(Action2):

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
  Copy(*args, **kwargs)

def copy_and_rename(*args, **kwargs):
  Copy(*args, **kwargs)

def move(*args, **kwargs):
  Copy(*args, **kwargs)

def move_and_rename(*args, **kwargs):
  Copy(*args, **kwargs)
    
#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.

def copy_file(*args, **kwargs):
  Copy(*args, **kwargs)

def copy_file_and_rename(*args, **kwargs):
  Copy(*args, **kwargs)

def move_file(*args, **kwargs):
  Copy(*args, **kwargs)

def move_file_and_rename(*args, **kwargs):
  Copy(*args, **kwargs)

#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.

def copy_directory(*args, **kwargs):
  with Copy(*args, **kwargs) as _:
    pass

def copy_directory_and_rename(*args, **kwargs):
  Copy(*args, **kwargs)

def move_directory(*args, **kwargs):
  Copy(*args, **kwargs)

def move_directory_and_rename(*args, **kwargs):
  Copy(*args, **kwargs)

#################################################################################
class Synchronize(Action2):

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
  Synchronize(*args, **kwargs)
  
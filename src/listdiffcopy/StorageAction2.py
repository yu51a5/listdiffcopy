import os
import math
import pandas as pd
import numpy as np
from functools import partial

from listdiffcopy.settings import ENFORCE_SIZE_FETCHING_WHEN_COMPARING, DEFAULT_SORT_KEY
from listdiffcopy.utils import creates_multi_index, idem
from listdiffcopy.LoggerObj import FDStatus, LoggerObj
from listdiffcopy.StorageBase import StorageBase

def filename_contents_transform_default(path, content, *args, **kwargs):
  return [path, content]
  
#################################################################################
class StorageAction2(LoggerObj):

  create_if_left_only = None
  delete_if_right_only = None
  change_if_both_exist = None
  delete_left_afterwards = False

  require_path_to = False
  add_basename_to_to = False

  enter_123 = [None, None, None]

  #################################################################################
  def __init__(self, *args, **kwargs):

    for fn_name, default_fn in [['filename_contents_transform', filename_contents_transform_default], 
                                ['sort_key', DEFAULT_SORT_KEY], 
                                ['sort_reverse', False],    
                                ['sort_resume', False],
                                ['filenames_filter', []],
                                ['change_if_both_exist', None]]:
      setattr(self, fn_name, kwargs[fn_name] if (fn_name in kwargs) else default_fn)
      kwargs.pop(fn_name, None)
      
    super().__init__()
    self.clear_errors_count()
    
    constr_args = {}

    args_inputs = ((str, 'path'),
       (StorageBase, 'storage'),
       (None, ('StorageFromType', 'StorageToType')),
       (dict, 'kwargs'))

    for type_, arg_name in args_inputs:
      arg_names = arg_name if type_ is None else [f'{arg_name}_{prefix}' for prefix in ('from', 'to')]
      constr_args.update({an : kwargs[an] for an in arg_names if ((an in kwargs) and (kwargs[an] is not None))})
      for an in arg_names:
        kwargs.pop(an, None)
        
    if kwargs:
      self.log_error(f'{kwargs} are unrecognised arguments for {self.__class__.__name__}')
      return FDStatus.Error

    for type_, arg_name in args_inputs:
      if type_ is None:
        _args = [a for a in args if isinstance(a, type) and issubclass(a, StorageBase)]
      else:
        _args = [a for a in args if isinstance(a, type_)]
      arg_names = arg_name if type_ is None else [f'{arg_name}_{prefix}' for prefix in ('from', 'to')]
      _a_counter = 0
      for i, an in enumerate(arg_names):
        if an in constr_args:
          continue
        if (type_ in (None, dict)) and (i == 0) and ('storage_from' in constr_args):
          continue
        if _a_counter < len(_args):
          constr_args[an] = _args[_a_counter]
          _a_counter += 1
      if _a_counter != len(_args):
        self.log_error(f"Wrong number of {arg_name} arguments: there should be at most two")  

    errors = [f'path_{prefix} is not provided' for prefix in ('from', 'to') if f'path_{prefix}' not in constr_args]
    if errors:
      self.log_critical(errors)
    
    self.root_path_from = constr_args['path_from']
    self.root_path_to = constr_args['path_to']

    self.__storage_from = constr_args['storage_from']     if 'storage_from'    in constr_args else None
    self.__storage_to   = constr_args['storage_to']       if 'storage_to'      in constr_args else None
    StorageFromType   = constr_args['StorageFromType']  if 'StorageFromType' in constr_args else None
    StorageToType     = constr_args['StorageToType']    if 'StorageToType'   in constr_args else None
    kwargs_from       = constr_args['kwargs_from']      if 'kwargs_from'     in constr_args else {}
    kwargs_to         = constr_args['kwargs_to']        if 'kwargs_to'       in constr_args else {}
    
    self.index_comp_df = pd.MultiIndex.from_tuples(creates_multi_index(self.index_listing_df, self.status_names_complete[:-1]))

    errors = StorageBase._check_storage_or_type(storage=self.__storage_from, StorageType=StorageFromType, kwargs=kwargs_from) \
           + StorageBase._check_storage_or_type(storage=self.__storage_to  , StorageType=StorageToType, kwargs=kwargs_to, both_nones_ok=True)

    if errors:
      self.log_critical(errors)
    

    if self.__storage_from and not self.__storage_to and StorageToType == type(self.__storage_from) and self.__storage_from.check_if_constructor_kwargs_are_the_same(kwargs_to):
      self.__storage_to = self.__storage_from
    if self.__storage_to and not self.__storage_from and StorageFromType == type(self.__storage_to) and self.__storage_to.check_if_constructor_kwargs_are_the_same(kwargs_from):
      self.__storage_from = self.__storage_to

    if self.__storage_to and self.__storage_from:
      self.__common_part_of_constructor()
    elif self.__storage_to and (not self.__storage_from):
      with StorageFromType(**kwargs_from, objects_to_sync_logger_with=[self.__storage_to]) as self.__storage_from:
        self.__common_part_of_constructor()
    elif self.__storage_from and (not self.__storage_to):
      if not StorageToType:
        self.__storage_to = self.__storage_from
        self.__common_part_of_constructor()
      else:
        with StorageToType(**kwargs_to, objects_to_sync_logger_with=[self.__storage_from]) as self.__storage_to:
          self.__common_part_of_constructor()
    else:
      with StorageFromType(**kwargs_from) as self.__storage_from:
        if (StorageFromType == StorageToType and kwargs_from == kwargs_to) or (StorageToType is None and (not kwargs_to)):
          self.__storage_to = self.__storage_from
          self.__common_part_of_constructor()
        else:
          with StorageToType(**kwargs_to, objects_to_sync_logger_with=[self.__storage_from]) as self.__storage_to: 
            self.__common_part_of_constructor()

  ###############################################################################
  def __common_part_of_constructor(self):

    str_from = self.__storage_from.str(self.root_path_from)
    str_to = self.__storage_to.str(self.root_path_to)

    self.log_title(title = f'{self.enter_123[0]} {str_from} {self.enter_123[2]} {str_to}')

    path_exist_is_dir_not_file_from = self.__storage_from._check_path_exist_is_dir_not_file(self.root_path_from)
    path_exist_is_dir_not_file_to   = self.__storage_to._check_path_exist_is_dir_not_file(self.root_path_to)

    if (path_exist_is_dir_not_file_from == 'both'):
      self.log_error(f"{str_from} is both a directory and a file")
    if path_exist_is_dir_not_file_to == 'both':
      self.log_error(f"{str_to} are both a directory and a file")

    if (path_exist_is_dir_not_file_from) is None:
      self.log_error(f"{str_from} does not exist")
    if (path_exist_is_dir_not_file_to) is None:
      if self.require_path_to:
        self.log_error(f"{str_to} does not exist")
    
    if self.add_basename_to_to:
      if path_exist_is_dir_not_file_from is not True:
        self.log_error(f"{str_to} must be a directory")

    if (path_exist_is_dir_not_file_from is True) and (path_exist_is_dir_not_file_to is False):
      self.log_error(f"{str_from}, the source, is a directory but {str_to}, the destination, is a file")
      
    if (path_exist_is_dir_not_file_from is False) and (path_exist_is_dir_not_file_to is True):
      error_msg = f"{str_from}, the source, is a file but {str_to}, the destination, is a directory"
      class_name = type(self.__storage_to).__name__
      if class_name.lower() in ('copy', "move"):
        error_msg += f'. Try using {class_name}Into class or {class_name.lower()}_into method instead'
      self.log_error(error_msg)

    if self.get_errors_count():
      return

    if path_exist_is_dir_not_file_from is True:
      if (path_exist_is_dir_not_file_to) is None:
        if self.add_basename_to_to:
          try:
            bn = os.path.basename(self.root_path_from)
            self.root_path_to = os.path.join(self.root_path_to, bn)
          except Exception as e:
            self.log_error(f'Cannot join `{self.root_path_to}` and `{bn}`, the basename of `{self.root_path_from}`', e)
            return
          self.__storage_to._create_directory(self.root_path_to)
        else:
          self.__storage_to._create_directory(self.root_path_to)

      self._action_files_directories_recursive(common_dir_appendix='')
    else:
      when_started = self.start_file(path=(str_from + " -> " + str_to), 
                                     message_to_print=self.enter_123[0], 
                                     message2=self.enter_123[2])
      
      this_file_result = self._action_file(
        file_from=self.root_path_from, 
        file_to=self.root_path_to,
        files_to_matched=None)
      
      self.print_complete_file(data=this_file_result, when_started=when_started)

  ###############################################################################
  def _action_right_only_file(self, file_to):
    try:
      if self.delete_if_right_only:
        self.__storage_to._delete_file(file_to)
        size_to = 0
      else:
        size_to, _ = self.__storage_to._get_file_size_or_content(path=file_to)
      return [os.path.basename(file_to), size_to, FDStatus.RightOnly_or_Deleted]
    except Exception as e:
      raise e # self.log_error(f'{self.enter_123[0]} {self.enter_123[1]} {self.__storage_to.str(file_to)} {self.enter_123[1]} failed, {e}')

  ###############################################################################
  def _action_file(self, file_from, file_to_or_dir_to, files_to_matched):

    def _action_new_file(path, content):
      if self.create_if_left_only:
        self.__storage_to._write_file(path=path, content=content)
      return FDStatus.LeftOnly_or_New

    def _action_existing_file(path, content):
      if self.change_if_both_exist is not None:
        status = self.__storage_to._write_file(path=path, content=content, check_if_contents_is_the_same_before_writing=self.change_if_both_exist) 
      else:
        size_to_current, cont_to_current = self.__storage_to._get_file_size_or_content(path=path)
        status = FDStatus.Different_or_Updated
        if len(content) == size_to_current:
          if cont_to_current is None:
            cont_to_current = self.__storage_to._read_file(path) 
          if content == cont_to_current:
            status = FDStatus.Identical
      return status
      
    basename_from, size_from, status = file_from, math.nan, FDStatus.Error
    try:
      basename_from = os.path.basename(file_from)
      if self.filename_contents_transform == idem:
        pass # start by checking sizes
          
      from_contents = self.__storage_from._read_file(file_from)
      size_from = len(from_contents)

      files_to_contents = self.filename_contents_transform(path=basename_from, content=from_contents, files_to_matched=files_to_matched, change_if_same_name_exist=self.change_if_both_exist is False)
      result_outputs = []
      if files_to_contents and isinstance(files_to_contents[0], str):
        files_to_contents = [files_to_contents]

      for file_to, content_to in files_to_contents:
        path = os.path.join(file_to_or_dir_to, file_to)
        status = self.__storage_to._method_with_check_path_exist_is_dir_not_file(
                       path=path,
                       mN=partial(_action_new_file, path=path, content=content_to),
                       mF=partial(_action_existing_file, path=path, content=content_to))            
        result_outputs.append([os.path.basename(file_to), len(content_to), status])
          
      if self.delete_left_afterwards:
          self.__storage_from._delete(file_from)
          
      return basename_from, size_from, result_outputs
    except Exception as e:
      raise e # self.log_error(f'{self.enter_123[0]} {self.enter_123[1]} {self.__storage_from.str(file_from)} {self.__storage_to.str(file_to_or_dir_to)} {self.enter_123[1]} failed, {e}')
      return [basename_from, size_from, status]
    
  ###############################################################################
  def _action_files_directories_recursive(self, common_dir_appendix):
  
    self.log_enter_level(common_dir_appendix, self.enter_123[0])

    _dir_from = os.path.join(self.root_path_from, common_dir_appendix) if common_dir_appendix else self.root_path_from
    files_from, dirs_from = self.__storage_from._get_filenames_and_dirnames(_dir_from, filenames_filter=self.filenames_filter, sort_key=self.sort_key, sort_reverse=self.sort_reverse, sort_resume=self.sort_resume)
    _dir_to = os.path.join(self.root_path_to, common_dir_appendix) if common_dir_appendix else self.root_path_to
    files_to, dirs_to   = self.__storage_to._get_filenames_and_dirnames(  _dir_to, filenames_filter=self.filenames_filter, sort_key=self.sort_key, sort_reverse=self.sort_reverse, sort_resume=self.sort_resume)

    max_fn_length = max([len(os.path.basename(f)) for f in files_from + files_to]) if (files_from or files_to) else 0
    max_files =  [os.path.basename(f) for f in (files_from + files_to) if len(os.path.basename(f)) == max_fn_length]
    max_files2 = [os.path.basename(f) for f in (files_from + files_to) if os.path.basename(f)[:100] == max_files[0][:100]]
    dir_info_first_level = np.zeros((5, 3), float)
    dir_info_total = np.zeros((5, 3), float)
    # dir_info_first_level[3][0] = math.nan # no information about deleted files' size 

    files_to_matched = {os.path.basename(f) : [] for f in files_to}
    row_header_array = [[], [], []]
    files_data_data = []
    files_from.sort(key=self.sort_key, reverse=self.sort_reverse)
    rows_printed_so_far = 0
    columns = (['Result Filename', 'Result Size', 'Status'] 
      if self.filename_contents_transform != filename_contents_transform_default else ['Size', 'Status'])
    index_names = (['Filename']
                      if self.filename_contents_transform == filename_contents_transform_default
                                           else ['Initial Filename', 'Initial Size', ''])

    def to_df_and_print(fn, fsize, fdata, files_data_data, rows_printed_so_far, max_fn_length):
      row_header_array[0] += [fn] * len(fdata)
      row_header_array[1] += [fsize] * len(fdata)
      row_header_array[2] += range(1, len(fdata) + 1)

      for this_file_result in fdata:
        status = this_file_result[-1].value
        dir_info_first_level[status][1] += 1
        dir_info_first_level[status][0] += this_file_result[-2]
        this_file_result[-1] = self.status_names_complete[status]
      
      files_data_data += fdata
      files_df = pd.DataFrame(
        files_data_data if self.filename_contents_transform != filename_contents_transform_default else [l[1:] for l in files_data_data], 
        index=[np.array(row_header_array[i]) for i in range(3 if self.filename_contents_transform != filename_contents_transform_default else 1)], 
        columns=columns) 

      files_df.index.names = index_names
      rows_printed_so_far = self.print_files_df(data=files_df, rows_printed_so_far=rows_printed_so_far, resume=self.sort_resume, path=common_dir_appendix, max_fn_length=max_fn_length)
      return rows_printed_so_far
      
    
    for f in files_from:
      fn, fsize, fdata = self._action_file(file_from=f, file_to_or_dir_to=_dir_to, files_to_matched=files_to_matched)

      for this_file_result in fdata:
        if this_file_result[0] not in files_to_matched:
          files_to_matched[os.path.basename(this_file_result[0])] = [os.path.basename(f)]
        else:
          files_to_matched[os.path.basename(this_file_result[0])].append(os.path.basename(f))
      
      rows_printed_so_far = to_df_and_print(fn, fsize, fdata, files_data_data, rows_printed_so_far, max_fn_length=max_fn_length)
      
    for f, v in files_to_matched.items():
      if not v:
        this_file_result = self._action_right_only_file(os.path.join(_dir_to, f))
        rows_printed_so_far = to_df_and_print(None, math.nan, [this_file_result], files_data_data, rows_printed_so_far, max_fn_length=max_fn_length)

    dirs_from.sort(key=self.sort_key, reverse=self.sort_reverse)
    dirs_to.sort(  key=self.sort_key, reverse=self.sort_reverse)
    
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
          self.__storage_to.create_directory(path=os.path.join(_dir_to, basename_from))
          subdir_info_total = self._action_files_directories_recursive(
            common_dir_appendix=os.path.join(common_dir_appendix, basename_from))
          dir_info_total += subdir_info_total
        else:
          subdir_list_total, _, _ = self.__storage_from._list_files_directories_recursive(path=dir_from, 
                                                                                          message2=f"Exists in {_dir_from} but not in {_dir_to}",
                                                                                          sort_key=self.sort_key, sort_reverse=self.sort_reverse,
                                                                                          enforce_size_fetching=ENFORCE_SIZE_FETCHING_WHEN_COMPARING) 
          dir_info_total[0] += subdir_list_total
        id_from += 1
      elif (id_from == 0) or ((basename_from is not None) and (basename_to is not None) and (basename_to < basename_from)):
        dir_info_first_level[1][2] += 1
        if self.delete_if_right_only:
          self.log_mention_directory(dirname=dir_to, message_to_print="Deleting", message2=f"in {self.__storage_to.str(_dir_to)}")
          self.__storage_to.delete_(dir_to)
          dir_info_first_level[1] += np.array([math.nan] * 3)
        else:
          subdir_list_total, _, _ = self.__storage_to._list_files_directories_recursive(path=dir_to, 
                                                                                        message2=f"Exists in {_dir_to} but not in {_dir_from}", 
                                                                                        sort_key=self.sort_key, sort_reverse=self.sort_reverse,
                                                                                        enforce_size_fetching=ENFORCE_SIZE_FETCHING_WHEN_COMPARING)
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

    if self.delete_left_afterwards:
      self.__storage_from._delete(_dir_from)

    data = np.vstack((dir_info_first_level, dir_info_total))
    self.log_exit_level(dir_details_df=pd.DataFrame(data, index=self.index_comp_df, columns=self.columns_df))
    return dir_info_total


#################################################################################
class Compare(StorageAction2):

  create_if_left_only = False
  delete_if_right_only = False
  require_path_to = True
  
  status_names = ["Left Only", "Right Only", "Different", "Identical"]

  enter_123 = ['Comparing', '', 'against']
  
  #################################################################################
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

#################################################################################
class Synchronize(StorageAction2):

  create_if_left_only = True
  delete_if_right_only = True
  change_if_both_exist = True

  enter_123 = ['Synchronizing', '', 'and']

  status_names = ["New", "Deleted", "Updated", "Identical"]

  #################################################################################
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

#################################################################################
class Transform(Synchronize):
  
  enter_123 = ['Transforming', '', 'to']

  #################################################################################
  def __init__(self, *args, filename_contents_transform, **kwargs):
    super().__init__(*args, filename_contents_transform=filename_contents_transform, **kwargs)

#################################################################################
class Copy(StorageAction2):

  create_if_left_only = True
  delete_if_right_only = False
  change_if_both_exist = True

  enter_123 = ['Copying', 'from', 'to']

  status_names = ["New", "Pre-existing", "Updated", "Identical"]
  
  #################################################################################
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

#################################################################################
class CopyAndTransform(Copy):

  enter_123 = ['Transforming', '', 'to']

  #################################################################################
  def __init__(self, *args, filename_contents_transform, **kwargs):
    super().__init__(*args, filename_contents_transform=filename_contents_transform, **kwargs)
    
#################################################################################
class CopyInto(Copy):
  add_basename_to_to = True
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
#################################################################################
class Move(StorageAction2):

  create_if_left_only = True
  delete_if_right_only = False
  change_if_both_exist = True
  delete_left_afterwards = True

  enter_123 = ['Moving', 'from', 'to']

  status_names = ["New", "Deleted", "Updated", "Identical"]
  
  #################################################################################
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
#################################################################################
class MoveInto(Move):
  add_basename_to_to = True
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

from datetime import datetime
from settings import log_file
from StorageLocal import StorageLocal
from utils import put_together_framed_message

#################################################################################
class Logger():

  ###############################################################################
  def _check_storage_or_type(storage, StorageType, kwargs):
    errors = []
    if (storage is None) == (StorageType is None):
      errors.append(f"storage_from {storage} and StorageFromType {StorageType} mustn't be both None or both not None")
    if (StorageType is None) and kwargs:
      errors.append(f"StorageFromType is not provided, but arguments {kwargs} are")
    return errors
  
  ###############################################################################
  def log_print_framed(self, message, char):
    msg = put_together_framed_message(message=message, char=char)
    self.log_print_basic(msg)

  ###############################################################################
  def __init__(self, title, log_filename=None, log_storage=None, log_StorageType=None, log_storage_kwargs={}):
    if log_storage is None and log_StorageType is None and (not log_storage_kwargs):
      log_StorageType = StorageLocal
      
    errors = Logger._check_storage_or_type(storage=log_storage, StorageType=log_StorageType, kwargs=log_storage_kwargs)
    assert not errors, '.\n'.join(['ERRORS:'] + errors)

    self.log_storage = log_storage
    self.log_StorageType = log_StorageType
    self.log_storage_kwargs = log_storage_kwargs
    
    self.log_text = []
    self.log_filename = log_filename
    self.level_start_times_dirnames = []
    self.log_print_framed(message=title, char='*')
    self.error_count = 0

  ###############################################################################
  def __del__(self):
    log_kwargs = dict(filename = self.log_filename, 
                       content = '\n'.join(self.log_text), 
                       check_if_contents_is_the_same_before_writing = False)
    
    if self.log_storage:
      self.log_storage.create_file_given_content(**log_kwargs)
    else:
      st = self.log_StorageType(self.log_storage_kwargs)
      st.create_file_given_content(**log_kwargs)

  ###############################################################################
  def get_errors_count(self):
    return self.error_count

  ###############################################################################
  def log_error(self, message):
    self.log_print_framed(message='ERROR: ' + message, char='!')
    self.error_count += 1

  ###############################################################################
  def log_warning(self, message):
    self.log_print_framed(message='WARNING: ' + message, char='.')
    
  ###############################################################################
  def log_mention_directory(self, dirname, message_to_print, message2='', now_=None):
    if now_ is None:
      now_ = datetime.now()
    self.log_print(message_to_print + ' directory ', dirname, message2, 'at', now_)

  ###############################################################################
  def log_enter_level(self, dirname, message_to_print, message2=''):
    now_ = datetime.now()
    self.level_start_times_dirnames.append((now_, dirname))
    self.log_mention_directory(dirname=dirname, message_to_print=message_to_print, message2=message2, now_=now_)

  ###############################################################################
  def log_exit_level(self, dir_details_df):
    now_ = datetime.now()
    time_elapsed = now_ - self.level_start_times_dirnames[-1][0]
    self.log_print('exited directory ', self.level_start_times_dirnames[-1][1], 'at', now_, 'time elapsed:', time_elapsed, dir_details_df)
    self.level_start_times_dirnames.pop(-1)

  ###############################################################################
  def log_print_basic(self, message):
    self.log_text.append(message)
    print(message)

  ###############################################################################
  def log_print_df(self, df, extra_prefix, last_chars_last_prefix=''):
    if df.index.empty:
      return
    df_str = df.to_string().split('\n')
    level = len(self.level_start_times_dirnames)
    prefix = '║' * (level - 1) + extra_prefix
    for i, df_str_ in enumerate(df_str):
        if i == (len(df_str) - 1) and last_chars_last_prefix:
          prefix = prefix[:-len(last_chars_last_prefix)] + last_chars_last_prefix
        self.log_print_basic(prefix + df_str_)

  ###############################################################################
  def log_print(self, message0, name, *args):

    level = len(self.level_start_times_dirnames)
  
    prefix = '╟──── '
    if 'dir' in message0:
      prefix = prefix.replace('─', '═')
      prefix = ('╚' if 'exit' in message0.lower() else ('╠' if 'DELETED' in message0 else '╔')) + prefix[1:]
    if message0.lower().startswith('exited'):
      prefix = prefix[:-2] + '╦ ' 
      dir_details_df = args[-1]
      args_to_use = args[:-1]
    else:
      dir_details_df = None
      args_to_use = args
    # boxy symbols https://www.ncbi.nlm.nih.gov/staff/beck/charents/unicode/2500-257F.html
    string_ = '║' * (level - 1) + prefix + message0 + '`' + name + '` ' + ' '.join([str(a) for a in args_to_use if a])
    
    self.log_print_basic(string_)

    if dir_details_df is not None:
      self.log_print_df(df=dir_details_df, extra_prefix=' ' * (len(prefix) - 2) + '╠═ ', last_chars_last_prefix='╚═ ')

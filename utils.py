import typing
import io
import pillow_avif
from PIL import Image
from settings import AVIF_QUALITY, wp_images_extensions

wp_images_extensions_with_dot = tuple([f'.{ext.lower()}' for ext in wp_images_extensions])

###############################################################################
def idem(x):
  return x

###############################################################################
def get_file_extention(filename):
  dot_pos = filename.rfind('.')
  if dot_pos < 0:
    return None
  return filename[dot_pos+1:]
  
def is_an_image(filename):
  result = filename.lower().endswith(wp_images_extensions_with_dot)
  return result

def filter_out_extra_wp_images(files_):
  qty_files = len(files_)
  i = 0
  while i < qty_files:
    this_file_name = files_[i].lower()
    if not is_an_image(this_file_name):
      continue
    i += 1 # as if it's already the next iteration
    pos = {c : this_file_name.rfind(c) for c in ('.', 'x', '-')}
    if min(pos.values()) < 0:
      continue
    if not ((pos['-'] + 4) <= (pos['x'] + 2) <= pos['.']):
      continue
    maybe_numbers = this_file_name[pos['-'] + 1:pos['x']] + this_file_name[pos['x'] + 1:pos['.']]
    not_numbers = [c for c in maybe_numbers if not ('0' <= c <= '9')]
    if not_numbers:
      continue

    presumed_original = this_file_name[:pos['-']] + this_file_name[pos['.']:]
    for j in range(i, qty_files):
      if files_[j] == presumed_original:
        qty_files -= 1
        i -= 1 #rolling back
        files_.pop(i)
        break
      if files_[j] > presumed_original:
        break
  
  return files_

###############################################################################
# SOURCE: https://stackoverflow.com/questions/33101935/convert-pil-image-to-byte-array
###############################################################################
def convert_image_to_AVIF(another_image_bytes, quality=AVIF_QUALITY):
  from_img = Image.open(io.BytesIO(another_image_bytes))
  result_img_stream = io.BytesIO()
  from_img.save(result_img_stream, format='AVIF', quality=quality)
  result = result_img_stream.getvalue()
  return result

###############################################################################
# source: https://stackoverflow.com/questions/73498143/checking-for-equality-if-either-input-can-be-str-or-bytes
###############################################################################
def is_equal_str_bytes(
  a: typing.Union[str, bytes],
  b: typing.Union[str, bytes],
) -> bool:
  if len(a) != len(b):
    return False
  if hash(a) != hash(b):
    return False
  if type(a) is type(b):
    return a == b
  if isinstance(a, bytes):  # make a=str, b=bytes
    a, b = b, a
  if a[:1000] != b[:1000].decode():
    return False
  if a[::1000] != b[::1000].decode():
    return False
  return a == b.decode()

###############################################################################
def put_together_framed_message(message, char='*', max_chars=60):
  chars = char * min(max_chars, len(message) + 6)
  result = '\n'.join(['', chars, char * 2 + ' ' + message + ' ' + char * 2, chars, ''])
  return result

###############################################################################
def remove_char_and_after(s, c):
  i = s.find(c)
  return s[:i] if i > 0 else s
  
###############################################################################
def remove_duplicates(a_list, transform_func=None):
  if transform_func:
    dict_ = {transform_func(v) : v for v in a_list}
    result = [v for v in dict_.values()]
  else:
    result = [x for n, x in enumerate(a_list) if a_list.index(x) == n]
  return result

###############################################################################
def find_duplicates(a_list):
  result = [x for n, x in enumerate(a_list) if a_list.index(x) < n]
  return result


#################################################################################
def creates_multi_index(index_1, index_2):
  index_1_expanded = [i1  for i1 in index_1 for _ in index_2]
  index_2_expanded = index_2 * len(index_1)
  result = list(map(list, zip(index_1_expanded, index_2_expanded)))
  return result

#################################################################################
def partial_with_moving_back(func, func_for_args_to_move_back, kwargnames_to_move_back, /, *args, **keywords):
  def newfunc(*fargs, **fkeywords):
    keywords_to_move_back = {a : keywords.pop(a) for a in keywords if a in kwargnames_to_move_back}
    newkeywords = {**keywords, **fkeywords, **keywords_to_move_back}
  
    args_to_move_back = [a for a in args if func_for_args_to_move_back(a)]
    args0 = [a for a in args if not func_for_args_to_move_back(a)]
  
    return func(*args0, *fargs, *args_to_move_back, **newkeywords)

  return newfunc
  
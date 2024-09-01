import typing
import io
import pillow_avif
from PIL import Image
from settings import DEFAULT_AVIF_QUALITY, DEFAULT_IMAGE_RESIZING_FILTER, wp_images_extensions

wp_images_extensions_with_dot = tuple([f'.{ext.lower()}' for ext in wp_images_extensions])
# https://stackoverflow.com/questions/4354543/determining-jpg-quality-in-python-pil
image_saving_settings = {'jpeg' : dict(quality='keep', optimize=True, progressive=True), 
                         'avif' : dict(quality=DEFAULT_AVIF_QUALITY)}
sizes_for_wp = [[None, h] for h in [150, 180, 200, 220, 250, 300, 400]] + [[w, None] for w in [500, 700]] + [[None, None]]

###############################################################################
def idem(*args, **kwargs):
  if not kwargs:
    if len(args) == 1:
      return args[0]
    if len(args) == 2:
      return args[0], args[1]
  return (*args, *(kwargs.values()))

###############################################################################
def get_file_extention(filename):
  dot_pos = filename.rfind('.')
  if dot_pos < 0:
    return None
  return filename[dot_pos+1:].lower()

###############################################################################
def is_an_image(filename):
  result = filename.lower().endswith(wp_images_extensions_with_dot)
  return result

###############################################################################
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
def _to_image_image(image_in_some_format):
  result = image_in_some_format if isinstance(image_in_some_format, Image.Image) \
                                  else Image.open(io.BytesIO(image_in_some_format))
  return result

def convert_image(image_bytes, target_extention, kwargs={}):
  from_img = _to_image_image(image_bytes)
  result_img_stream = io.BytesIO()
  from_img.save(result_img_stream, target_extention.upper() if target_extention.lower() != "jpg" else "JPEG", **kwargs)
  result = result_img_stream.getvalue()
  return result

def resize_image(image_bytes, max_size, max_ratio=None, filter=DEFAULT_IMAGE_RESIZING_FILTER):
  img = image_bytes if isinstance(image_bytes, Image.Image) else Image.open(io.BytesIO(image_bytes))
  ratio = min([1.] + [max_size[i] / float(img.size[i]) for i in range(2) if max_size[i]])
  if max_ratio is not None:
    if ratio > max_ratio:
      return None
  new_size = [int(float(img.size[i]) * ratio) for i in range(2)]
  img = img.resize(new_size, filter)
  return img

def convert_image_to_AVIF_if_another_format_image(path, content, *args, **kwargs):
  if is_an_image(path):
    if not path.lower().endswith(("avif", 'svg')):
      path_result = path[:path.rfind('.')] + ".avif"
      return path_result, convert_image(content, "avif")
  return path, content

def batch_resize_images(init_filename, init_content, max_ratio=.99):

  if not is_an_image(init_filename):
    raise Exception(f"The extension of {init_filename} suggests that this file is not an image")
    
  ext = get_file_extention(init_filename)
  if ext.lower() == 'svg':
    return [[init_filename, init_content]]
    
  target_extentions = ['avif', ext] if ext.lower() != 'avif' else ['avif']
  init_fn = init_filename[:init_filename.rfind('.')]
  
  filenames_contents = []
  for w, h in sizes_for_wp:
    appendix = '.w' + str(w) if w else '.h' + str(h) if h else ''
    img_content_resized = init_content if not appendix else resize_image(init_content, [w, h], max_ratio=max_ratio)
    if img_content_resized:
      filenames_contents += [[init_fn + appendix + '.' + target_extention,
                               convert_image(img_content_resized, target_extention=target_extention)] 
                                                                   for target_extention in target_extentions]

  return filenames_contents

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
  
#import typing
import io
import pillow_avif # https://pypi.org/project/pillow-avif-plugin/, pip install pillow-avif-plugin
from PIL import Image
from listdiffcopy.jpg_quality_pil_magick import get_jpg_quality

from listdiffcopy.settings import DEFAULT_AVIF_QUALITY, DEFAULT_IMAGE_RESIZING_FILTER, wp_images_extensions

wp_images_extensions_with_dot = tuple([f'.{ext.lower()}' for ext in wp_images_extensions])
# https://stackoverflow.com/questions/4354543/determining-jpg-quality-in-python-pil
jpeg_saving_settings = dict(optimize=True, progressive=True) # quality='keep', 
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
def __get_presumed_original_x(this_file_name):
  pos = {c : this_file_name.rfind(c) for c in ('.', 'x', '-')}
  if (min(pos.values())) < 0 or not ((pos['-'] + 4) <= (pos['x'] + 2) <= pos['.']):
    return None
  maybe_numbers = this_file_name[pos['-'] + 1:pos['x']] + this_file_name[pos['x'] + 1:pos['.']]
  not_numbers = [c for c in maybe_numbers if not ('0' <= c <= '9')]
  if not_numbers:
    return None
  presumed_original = this_file_name[:pos['-']] + this_file_name[pos['.']:]
  return presumed_original

def __get_presumed_original_wh(this_file_name):
  dot0 = this_file_name.rfind('.')
  if dot0 < 0:
    return None
  dot1 = this_file_name.rfind('.', 0, dot0)
  if (dot1 < 0) or (dot1+2 >= dot0) or this_file_name[dot1+1] not in ['h', 'w']:
    return None
  
  not_numbers = [c for c in this_file_name[dot1+2:dot0] if not ('0' <= c <= '9')]
  if not_numbers:
    return None
  presumed_original = this_file_name[:dot1] + this_file_name[dot0:]
  return presumed_original


def filter_out_extra_wp_images(files_, is_hw_style=None):
  files_.sort()
  qty_files = len(files_)
  i = 0
  while i < qty_files:
    this_file_name = files_[i]
    i += 1 # as if it's already the next iteration
    if not is_an_image(this_file_name.lower()):
      continue
    presumed_originals = []
    if is_hw_style is not True:
      presumed_originals.append(__get_presumed_original_x(this_file_name))
    if is_hw_style is not False:
      presumed_originals.append(__get_presumed_original_wh(this_file_name))
    presumed_originals = [po for po in presumed_originals if po is not None]
    if not presumed_originals:
      continue
    found = False
    for j in range(i, qty_files):
      if files_[j] in presumed_originals:
        qty_files -= 1
        i -= 1 #rolling back
        files_.pop(i)
        found = True
        break
      if files_[j] > max(presumed_originals):
        break
    if found:
      continue
    for j in range(i-1, -1, -1):
      if files_[j] in presumed_originals:
        qty_files -= 1
        i -= 1 #rolling back
        files_.pop(i)
        break
      if files_[j] < min(presumed_originals):
        break

  return files_

###############################################################################
# SOURCE: https://stackoverflow.com/questions/33101935/convert-pil-image-to-byte-array
###############################################################################
def _to_image_image(image_in_some_format):
  result = image_in_some_format if isinstance(image_in_some_format, Image.Image) \
                                  else Image.open(io.BytesIO(image_in_some_format))
  return result

def convert_image(image_bytes, target_extention, **kwargs):
  from_img = _to_image_image(image_bytes)
  result_img_stream = io.BytesIO()
  ext = target_extention.upper() if target_extention.lower() != "jpg" else "JPEG"
  kwargs_ = jpeg_saving_settings if (ext == "JPEG") and (not kwargs) else kwargs
  from_img.save(result_img_stream, ext, **kwargs_)
  result = result_img_stream.getvalue()
  return result

def resize_image(image_bytes, max_size, max_ratio=None, filter=DEFAULT_IMAGE_RESIZING_FILTER):
  img = image_bytes if isinstance(image_bytes, Image.Image) else Image.open(io.BytesIO(image_bytes))
  ratios_array = [(max_size[i] / float(img.size[i]) if max_size[i] is not None else None)  for i in range(2)] + [1.]
  ratio = min([a for a in ratios_array if a is not None])
  if max_ratio is not None:
    if ratio > max_ratio:
      return None
  # approximate size
  new_size = [int(float(img.size[i]) * ratio) for i in range(2)]
  # adjusting
  i = None
  if (ratios_array[0] is not None) and (ratios_array[1] is not None):
    i = min(range(2), key=lambda x : ratios_array[x])
  elif ratios_array[0] is not None:
    i = 0
  elif ratios_array[1] is not None:
    i = 1
  if i is not None:
    new_size[i] = max_size[i]

  img = img.resize(new_size, filter)
  return img

def convert_image_to_AVIF_if_another_format_image(path, content, files_to_matched=None, change_if_same_name_exist=None):
  if is_an_image(path):
    if not path.lower().endswith(("avif", 'svg')):
      path_result = path[:path.rfind('.')] + ".avif"
      return path_result, convert_image(content, "avif")
  return path, content

def batch_resize_images(path, content, max_pixel_ratio=.99, min_avif_compression=.95, avif_quality=DEFAULT_AVIF_QUALITY,
                       files_to_matched=None, change_if_same_name_exist=None):

  ext = get_file_extention(path)
  if (ext.lower() == 'svg') or (not is_an_image(path)):
    return [[path, content]]

  if ext.upper() in ("JPG", "JPEG"):
    c = _to_image_image(content)
    print('image quality', get_jpg_quality(c))
  
  filenames_contents = []
  failed_to_convert = []
  for w, h in sizes_for_wp:
    appendix = '.w' + str(w) if w else '.h' + str(h) if h else ''
    img_content_resized = content if not appendix else resize_image(content, [w, h], max_ratio=max_pixel_ratio)
    
    if not img_content_resized:
      continue

    init_fn = path[:path.rfind('.')] + appendix + '.'
    kwargs_ = dict(quality=avif_quality)  if ext.lower() == 'avif' else {}
    converted_img_original_ext = convert_image(img_content_resized, target_extention=ext, **kwargs_)
    if ext.lower() != 'avif':
      try:
        converted_img_avif = convert_image(img_content_resized, target_extention='avif', quality=avif_quality)
      except Exception as e:
        failed_to_convert.append([path, 'avif', e])
        converted_img_avif = []
      print( len(converted_img_original_ext), len(converted_img_avif), init_fn)
      if (converted_img_avif) and len(converted_img_avif) < min_avif_compression * len(converted_img_original_ext):
        filenames_contents.append([init_fn + 'avif', converted_img_avif])
    
    filenames_contents.append([init_fn + ext, converted_img_original_ext])
  if failed_to_convert:
    print('failed_to_convert', failed_to_convert)
  return filenames_contents

###############################################################################
# source: https://stackoverflow.com/questions/73498143/checking-for-equality-if-either-input-can-be-str-or-bytes
###############################################################################
def is_equal_str_bytes(a, b):
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
  
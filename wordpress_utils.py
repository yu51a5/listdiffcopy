# SOURCES:
# https://stackoverflow.com/questions/33101935/convert-pil-image-to-byte-array
# https://codelabs.developers.google.com/codelabs/avif#3
# there should be two dashes before `min` and `max`

import subprocess
import io
import os
from PIL import Image
import pillow_avif
from StorageSFTP import StorageSFTP
from storage_actions import list, rename, delete, compare, synchronize, copy
from settings import AVIF_QUALITY, recommended_avifenc_parameters

d = "www/yu51a5.xyz/public_html/wp-content/uploads/hamlet"
s_path = os.path.join(d, 'test7')
JPGimg = Image.open('l.jpg', mode='r')
img_byte_arr = io.BytesIO()
print(type(img_byte_arr))
JPGimg.save(img_byte_arr, format='AVIF', quality=AVIF_QUALITY)

list(StorageSFTP, d)

with StorageSFTP() as s:
    print(s, type(s))
    s.create_directory(s_path)
    s.write_file(os.path.join(s_path, 'l.avif'), content=img_byte_arr.getvalue())

assert 0

s_path = os.path.join(d, "testfile.avif")
list(StorageSFTP, d)



# img_byte_arr = 

def convert_to_avif(input_file, output_file=None, avifenc_parameters=recommended_avifenc_parameters):
    subprocess.run(f"avifenc {avifenc_parameters} {input_file} {output_file if output_file else input_file[:input_file.rfind('.')]}.avif", shell=True)

convert_to_avif('l.jpg')



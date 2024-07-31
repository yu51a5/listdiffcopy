import subprocess

# https://codelabs.developers.google.com/codelabs/avif#3
# there should be two dashes before `min` and `max`
recommended_avif_parameters = "--min 0 --max 63 -a end-usage=q -a cq-level=32 -a tune=ssim -a deltaq-mode=3 -a sharpness=3 -y 420"

input_file = 'filename.jpg'
subprocess.run(f"avifenc {recommended_avif_parameters} {input_file} {input_file[:input_file.rfind('.')]}.avif", shell=True)

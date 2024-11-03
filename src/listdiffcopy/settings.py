from PIL import Image

pcloud_urls_are_eapi = True
fetch_github_modif_timestamps = True
wp_images_extensions = ('jpg', 'jpeg', 'gif', 'png', 'svg', 'webp', 'avif') # small letters only
log_file = 'log.txt'
list_directories_that_exist_in_one_storage_only = True
list_identical_files = True
ENFORCE_SIZE_FETCHING_WHEN_LISTING = True
ENFORCE_SIZE_FETCHING_WHEN_COMPARING = False
DEFAULT_SORT_KEY = lambda x : x.lower()

DEFAULT_AVIF_QUALITY = 63
# https://codelabs.developers.google.com/codelabs/avif#3
# there should be two dashes before `min` and `max`
recommended_avifenc_parameters = f"--min 0 --max {DEFAULT_AVIF_QUALITY} -a end-usage=q -a cq-level=32 -a tune=ssim -a deltaq-mode=3 -a sharpness=3 -y 420"
DEFAULT_IMAGE_RESIZING_FILTER = Image.Resampling.LANCZOS

log_dirname = 'logs'
PATH_FOR_RESUMING = "filename_started.txt"

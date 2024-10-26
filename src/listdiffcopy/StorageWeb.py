import os
import requests
import math
import time

#################################################################################
#In Shell,
# 1. run chromedriver --help - this will add chromedriver to your replit.nix;
# 2. run chromium --help - this will add chromium to your replit.nix. 
# There are two installation options, ungoogled-chromium.out and chromium.out. I have chosen ungoogled-chromium.out

# sources: https://medium.com/analytics-vidhya/using-python-and-selenium-to-scrape-infinite-scroll-web-pages-825d12c24ec7
# and # https://stackoverflow.com/questions/71201650/how-to-use-selenium-on-repl-it/77616859
import bs4

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from listdiffcopy.utils import remove_duplicates
from listdiffcopy.StorageBase import StorageBase

#################################################################################
class StorageWeb(StorageBase):

  ###############################################################################
  def get_browser_options():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')

    options.add_argument("start-maximized"); 
    options.add_argument("disable-infobars"); 
    options.add_argument("--disable-extensions"); 
    options.add_argument("--disable-gpu"); 
    options.add_argument("--disable-dev-shm-usage"); 

    return options

  chrome_options = get_browser_options()

  ###############################################################################
  def __init__(self, logger_name=None, objects_to_sync_logger_with=[]):
    super().__init__(constructor_kwargs={}, 
                     logger_name=logger_name, 
                     objects_to_sync_logger_with=objects_to_sync_logger_with,
                     connection_var_name='_requests_session')
    self.__fake_directories = [{}, [], []]
    self.__fake_files = {}
    self.__name_content_type_is_content = {}
    self.__fake_paths_to_urls = {}

  ###############################################################################
  @classmethod
  def get_headers(cls):
    return {}

  ###############################################################################
  def _open(self):
    self._requests_session = requests.Session()
    self._requests_session.headers.update(self.get_headers())

  ###############################################################################
  def path_to_str(self, path):
    return self.__fake_paths_to_urls[path] if path in self.__fake_paths_to_urls else path

  ###############################################################################
  def transformer_for_comparison(self, s):
    return s

  ###############################################################################
  def get_response_code(self, url):
    with self._get_connection_var().get(url) as response:
      return response.status_code

  ###############################################################################
  def check_urls(self, urls, print_ok=False):
    by_resp_code = {}
    for url in urls:
      try:
        response_code = self.get_response_code(url)
      except:
        response_code = 418
      if response_code in by_resp_code:
        by_resp_code[response_code].append(url)#[url, pages_where_referenced])
      else:
        by_resp_code[response_code] = [url]#[url, pages_where_referenced]]

    for code, urls_ in by_resp_code.items():
      if code == 200:
        if print_ok:
          self.log_info("\nOK URL:\n" + "\n".join(urls_) + "\n\n")
      elif code == 403:
        self.log_warning("\nURL that cannot be automatically checked (code 403):\n" + "\n".join(urls_) + "\n\n")
      else:
        self.log_error(f"\nURL check failed (code {code}):\n" + "\n".join(urls_) + "\n\n")


      # [("\n" + u + ": this URL is referenced in:\n" + "\n".join(p)) for u, p in

  ###############################################################################
  def _read_file(self, path, length=None, use_content_not_text=None): # filename is url
    if path in self.__fake_files:
      return self.__fake_files[filename]
    with self._get_connection_var().get(path) as response:
      if response.status_code == 200:
        use_content = use_content_not_text if use_content_not_text is not None else self.__name_content_type_is_content[filename] if filename in self.__name_content_type_is_content else True
        return response.content if use_content else (response.text[:length] if length else response.text)
      else:
        self.log_error(f'Downloading of {filename} failed, code {response.status_code}') 

  ###############################################################################
  def _get_filenames_and_directories(self, path : str):
    files_, directories_ = [], []
    if not path:
      directories_, urls, fake_filename_contents = self.__fake_directories
    else:
      root_folders = self.split_path_into_dirs_filename(path=path)
      what = self.__fake_directories
      for rf in root_folders:
        if rf not in what[0]:
          return [], []
        what = what[0][rf]
      directories_, urls, fake_filename_contents = what

    directories_ = [os.path.join(path, k) for k in directories_.keys()]
    files_ = [u for u in urls] + [os.path.join(path, k) for k in fake_filename_contents]
    return files_, directories_

  ###############################################################################
  def _get_root_url_other(self, url):
    return os.path.dirname(url), os.path.basename(url)

  ###############################################################################
  def url_or_urls_to_fake_directory(self, url_or_urls, path, 
                                          do_same_root_urls=True, 
                                          check_other_urls=True,
                                          save_texts=True,
                                          save_assets=True):
    urls = [url_or_urls] if isinstance(url_or_urls, str) else [s for s in url_or_urls]

    self.log_title(f"Analysing {len(urls)} URL{'' if {len(urls)==1} else 's'} {'and other linked URLs' if do_same_root_urls else ''}")

    # removing duplicates
    comp_dict = { self.transformer_for_comparison(u) : u for u in urls} 
    urls = [u for u in comp_dict.values()]
    # making sure the root is the same
    root_url, _ = self._get_root_url_other(urls[0])
    faulty_urls = [u for u in urls if not u.startswith(root_url)]
    urls = [u for u in urls if u not in faulty_urls]
    completed_urls = set()
    external_urls = set()
    backup_names_so_far = set()
    while urls:
      url = urls.pop(0)

      if self.get_response_code(url) != 200:
        external_urls.add(url)
        continue

      tu =  self.transformer_for_comparison(url)
      if tu in completed_urls:
        continue
      completed_urls.add(tu)

      source, contents, assets_urls, urls_to_add, backup_name = self._url_to_backup_content_hrefs(url=url, save_texts=save_texts, save_assets=save_assets)

      for u in urls_to_add:
        if do_same_root_urls and (u.startswith(root_url)):
          urls.append(u)
        if check_other_urls and (not u.startswith(root_url)):
          external_urls.add(u)

      if not backup_name:
        continue

      if backup_name in backup_names_so_far:
        self.log_error(f"URL {url} has duplicate backup name {backup_name}")
        continue
      backup_names_so_far.add(backup_name)
      self.log_info(f'Analysing "{url}".\nResults saved as directory "{backup_name}"\n')



      fake_filename_contents_text = {'contents_'+backup_name+'.txt' : contents,
                                       'source_'+backup_name+'.txt' : str(source)}

      self.__fake_files.update({os.path.join(path, backup_name, k) : v for k, v in fake_filename_contents_text.items()})
      self.__fake_paths_to_urls[os.path.join(path, backup_name)] = url

      root_folders = self.split_path_into_dirs_filename(path=os.path.join(path, backup_name))
      dict_to_use = self.__fake_directories
      for rf in root_folders:
        if rf not in dict_to_use[0]:
          dict_to_use[0][rf] = [{}, [], []]
        dict_to_use = dict_to_use[0][rf]

      if save_assets:
        dict_to_use[1] = assets_urls
        self.__name_content_type_is_content.update({k: True for k in assets_urls})

      if save_texts:
        dict_to_use[2] = fake_filename_contents_text.keys()      
        self.__name_content_type_is_content.update({k: False for k in fake_filename_contents_text})

    return external_urls

  ###############################################################################
  def _url_to_backup_content_hrefs(self, url, save_texts, save_assets):
    self.__please_override()

  ###############################################################################
  def _get_page_source_with_scrolling(url, init_sleep=2, scroll_pause_time=1):

    driver = webdriver.Chrome(options=StorageWeb.chrome_options)

    driver.get(url)
    time.sleep(init_sleep)  # Allow init_sleep seconds for the web page to open
    screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web
    i = 1

    scroll_height = math.inf
    while (screen_height) * i <= scroll_height:
      # scroll one screen height each time
      driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
      
      time.sleep(scroll_pause_time)
      # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
      scroll_height = driver.execute_script("return document.body.scrollHeight;")  
      # Break the loop when the height we need to scroll to is larger than the total scroll height
      print(f'Completed {i} scroll{"s" if i > 1 else ""} of {url}')
      i += 1

    html = driver.page_source
    driver.quit()

    return i, html

  ###############################################################################
  def _url_to_part_of_source(self, url, tag):
    response_text = self._read_file(filename=url, use_content_not_text=False)
    soup = bs4.BeautifulSoup(response_text, 'html.parser')
    if isinstance(tag, str):
      result = soup.find(tag)
    else: # list
      result = soup.find_all(tag)
    return result
    
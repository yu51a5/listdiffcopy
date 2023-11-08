import bs4
import html2text
import os

from SomeAction1 import SomeAction1
from SomeAction2 import synchronize
from StorageWeb import StorageWeb

h = html2text.HTML2Text()
h.ignore_links = False
h.body_width = 0
h.ignore_images = False # DOESN'T WORK

# inspirations: https://gist.github.com/bgoonz/217ba804d2b3aabe8415c9c99d8f9224
# and           https://github.com/gunar/medium-parser/blob/master/src/processElement.js

#################################################################################
class ScrappingMediumPage(SomeAction1):
  
  __start_ing_url = 'https://miro.medium.com/v2/'

  def __init__(self, url, StorageType, path, kwargs_storage, backup_name_override=None, main_tag='article'):
    super().__init__(title=f'Scrapping {url} -> ', StorageType=StorageType, path=path, kwargs_storage=kwargs_storage)

    backup_name = url.split('/')[-1]
    backup_name = backup_name[:backup_name.find("?")] if backup_name_override is None else backup_name_override
    assets_dir = os.path.join(path, backup_name)
    self.hrefs = []
    
    with StorageWeb() as self.instanceStorageWeb:
      func = lambda response: self.inner_func(instanceStorageWeb=self.instanceStorageWeb, response=response, 
                                              StorageType=StorageType, assets_dir=assets_dir, kwargs_storage=kwargs_storage,  
                                              main_tag=main_tag, title='Backing up ' + url)
      self.instanceStorageWeb.get_contents(filename=url, func=func)

  def inner_func(self, instanceStorageWeb, response, StorageType, kwargs_storage, assets_dir, main_tag, title):
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
  
    article_html = soup.find(main_tag)
    
    captions_images = []
    all_divs = article_html.find_all("div")
    all_pic_urls = []
    for ad in all_divs:
      figcaptions = ad.find_all("figcaption")
      all_figures = ad.find_all("figure")
      divs_inside_figures_qty = sum([len(f.find_all("div"))  for f in all_figures])
      divs_qty = len(ad.find_all("div")) 
      if (len(figcaptions) > 1) or (not all_figures) or (divs_inside_figures_qty != divs_qty):
        continue
      figcaption = figcaptions[0].text if figcaptions else ''
      captions_images.append((figcaption, []))
      pictures = ad.find_all('picture')
      for p in pictures:
        splints = str(p).split(', ')
        splints = [s[:s.find(' ')] for s in splints if s.startswith(ScrappingMediumPage.__start_ing_url)]
        splints = [ScrappingMediumPage.__start_ing_url + s[s.rfind('/')+1:] for s in splints]
        divergent = [s for s in splints if s != splints[0]]
        assert not divergent, splints
        url_pic = splints[0]
        captions_images[-1][1].append(os.path.basename(url_pic))
        all_pic_urls.append(url_pic)
        
    article_text = h.handle(str(article_html))
    article_text = article_text[:article_text.find('\n[![')] + article_text[article_text.find('Share\n')+6:] 
    back_up_content = (SomeAction1.put_together_framed_message(message=title)
                       + article_text
                       + SomeAction1.put_together_framed_message(message='Pictures')
                       + ''.join([f'{i+1}. {ci[0]} : {ci[1]}\n' for i, ci in enumerate(captions_images)]))

    StorageWeb.create_fake_directory(dir_name=assets_dir, 
                                             urls=all_pic_urls, 
                                             fake_filename_contents={os.path.basename(assets_dir)+'.txt' : back_up_content})
    synchronize(storage_from=self.instanceStorageWeb, storage_to=self.storage, path_from=assets_dir, path_to=assets_dir)

    self.storage.create_directory(path=assets_dir)
    for url_pic in all_pic_urls:
      target_path = os.path.join(assets_dir, os.path.basename(url_pic))
      self.log_print_basic(f'Downloading {url_pic} -> {target_path}')
      func_pic = lambda response: self.storage.create_file_given_content(filename=target_path, content=response.content)
      instanceStorageWeb.get_contents(filename=url_pic, func=func_pic)
      
    self.storage.create_file_given_content(filename=assets_dir+'.txt', content=back_up_content)
    
    all_as = article_html.find_all("a")
    self.hrefs = [a_tag['href'] for a_tag in all_as]
  
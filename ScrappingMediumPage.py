import requests
import bs4
import html2text
import os

from SomeAction1 import SomeAction1

h = html2text.HTML2Text()
h.ignore_links = False
h.body_width = 0
h.ignore_images = False # DOESN'T WORK

# inspirations: https://gist.github.com/bgoonz/217ba804d2b3aabe8415c9c99d8f9224
# and           https://github.com/gunar/medium-parser/blob/master/src/processElement.js

#################################################################################
class ScrappingMediumPage(SomeAction1):
  
  __start_ing_url = 'https://miro.medium.com/v2/'
  def __get_picture_url(html_text):
    splints = str(html_text).split(', ')
    splints = [s[:s.find(' ')] for s in splints if s.startswith(ScrappingMediumPage.__start_ing_url)]
    splints = [ScrappingMediumPage.__start_ing_url + s[s.rfind('/')+1:] for s in splints]
    divergent = [s for s in splints if s != splints[0]]
    assert not divergent, splints
    return splints[0]

  def __init__(self, url, StorageType, path, kwargs_storage, backup_name_override=None, main_tag='article'):
    super().__init__(title=f'Scrapping {url} -> ', StorageType=StorageType, path=path, kwargs_storage=kwargs_storage)
  
    response = requests.get(url)
    if response.status_code != 200:
      self.log_error(f'Downloading of {url} failed, code {response.status_code}') 
      self.hrefs = []
    else:
      soup = bs4.BeautifulSoup(response.text, 'html.parser')
    
      article_html = soup.find(main_tag)
      article_text = h.handle(str(article_html))
      article_text = article_text[:article_text.find('\n[![')] + article_text[article_text.find('Share\n')+6:] 
    
      backup_name = url.split('/')[-1]
      backup_name = backup_name[:backup_name.find("?")] if backup_name_override is None else backup_name_override
      assets_dir = os.path.join(path, backup_name)
      self.storage.create_directory(path=assets_dir)
      captions_images = []
      all_divs = article_html.find_all("div")
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
          url_pic = ScrappingMediumPage.__get_picture_url(html_text=str(p))
          filename = url_pic.split('/')[-1]
          captions_images[-1][1].append(filename)
          target_path = os.path.join(assets_dir, filename)
          self.log_print_basic(f'Downloading {url_pic} -> {target_path}') 
          with requests.get(url_pic, stream=True) as response:
            if response.status_code == 200:
              self.storage.create_file_given_content(filename=target_path, content=response.content)
            else:
              self.log_error(f'Downloading of {url} failed, code {response.status_code}') 
    
      back_up_content = self.put_together_framed_message(message='Backing up ' + url)
      back_up_content += article_text
      back_up_content += self.put_together_framed_message(message='Pictures')
      back_up_content += ''.join([f'{i+1}. {ci[0]} : {ci[1]}\n' for i, ci in enumerate(captions_images)])
    
      self.storage.create_file_given_content(filename=os.path.join(path, backup_name+'.txt'), content=back_up_content)
      
      all_as = article_html.find_all("a")
      self.hrefs = [a_tag['href'] for a_tag in all_as]
  
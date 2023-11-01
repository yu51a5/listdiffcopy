import requests
import bs4
import html2text
import os

from SomeActionLogger import Logger

h = html2text.HTML2Text()
h.ignore_links = False
#h.ignore_images = False # DOESN'T WORK

# inspirations: https://gist.github.com/bgoonz/217ba804d2b3aabe8415c9c99d8f9224
# and           https://github.com/gunar/medium-parser/blob/master/src/processElement.js

start_ing_url = 'https://miro.medium.com/v2/'

def get_picture_url(html_text):
  splints = str(html_text).split(', ')
  splints = [s[:s.find(' ')] for s in splints if s.startswith(start_ing_url)]
  splints = [start_ing_url + s[s.rfind('/')+1:] for s in splints]
  divergent = [s for s in splints if s != splints[0]]
  assert not divergent, splints
  return splints[0]


def backup_a_url(url, storage, storage_dir):
  
  backup_name = url.split('/')[-1]
  backup_name = backup_name[:backup_name.find("?")]
  
  logger = Logger(title='Backing up ' + url)

  response = requests.get(url)
  
  soup = bs4.BeautifulSoup(response.text, 'html.parser')

  article_html = soup.find('article')
  article_str = str(article_html)
  article_text = h.handle(article_str)
  article_text = article_text[:article_text.find('\n[![')] + article_text[article_text.find('Share\n')+6:] 

  assert storage.check_directory_exists(path=storage_dir)
  assets_dir = os.path.join(storage_dir, backup_name)
  storage.create_directory_in_existing_directory(path=assets_dir)
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
      url = get_picture_url(html_text=str(p))
      filename = url.split('/')[-1]
      captions_images[-1][1].append(filename)
      logger.log_print_basic(f'Downloading {url}') 
      with requests.get(url, stream=True) as response:
        storage.create_file_given_content(filename=os.path.join(assets_dir, filename), content=response)

  back_up_content = Logger.put_together_framed_message(message='Backing up ' + url)
  back_up_content += article_text
  back_up_content += Logger.put_together_framed_message(message='Pictures ' + url)
  back_up_content += ''.join([f'{i+1}. {ci[0]} : {ci[1]}\n' for i, ci in enumerate(captions_images)])

  storage.create_file_given_content(filename=os.path.join(storage_dir, backup_name+'.txt'), content=back_up_content)
  
  
import os 
import bs4
import html2text

h = html2text.HTML2Text()
h.ignore_links = False
h.body_width = 0
h.ignore_images = False # DOESN'T WORK

from utils import put_together_framed_message, remove_char_and_after
from StorageWeb import StorageWeb

#################################################################################
class StorageWebMedium(StorageWeb):

  __start_ing_url = 'https://miro.medium.com/v2/'

  ###############################################################################
  def transformer_for_comparison(s):
    return remove_char_and_after(s=s, c='?')

  ###############################################################################
  def __init__(self, logger_name=None, objects_to_sync_logger_with=[]):
    super().__init__(logger_name=logger_name, objects_to_sync_logger_with=objects_to_sync_logger_with)

  ###############################################################################
  def url_to_backup_content_hrefs(self, url):
    try:
      backup_name = StorageWebMedium.transformer_for_comparison(os.path.basename(url))
      main_tag = 'article' if backup_name.lower() != 'about' else 'main'
      
      response_text = self.get_content(filename=url, use_content_not_text=False)
      soup = bs4.BeautifulSoup(response_text, 'html.parser')
      article_html = soup.find(main_tag)
  
      captions_images = []
      all_divs = article_html.find_all("div")
      assets_urls = []
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
          splints = [s[:s.find(' ')] for s in splints if s.startswith(StorageWebMedium.__start_ing_url)]
          splints = [StorageWebMedium.__start_ing_url + s[s.rfind('/')+1:] for s in splints]
          divergent = [s for s in splints if s != splints[0]]
          assert not divergent, splints
          url_pic = splints[0]
          captions_images[-1][1].append(os.path.basename(url_pic))
          assets_urls.append(url_pic)
  
      article_text = h.handle(str(article_html))
      article_text = article_text[:article_text.find('\n[![')] + article_text[article_text.find('Share\n')+6:] 
      back_up_content = (put_together_framed_message(message='Backing up ' + url)
                         + article_text
                         + put_together_framed_message(message='Pictures')
                         + ''.join([f'{i+1}. {ci[0]} : {ci[1]}\n' for i, ci in enumerate(captions_images)]))
      all_as = article_html.find_all("a")
      urls_to_add = [a_tag['href'] for a_tag in all_as]
      for i, u in enumerate(urls_to_add):
        if u.startswith('/@'):
          urls_to_add[i] = "https://medium.com" + u

      url_following = os.path.join(os.path.dirname(url), 'following')
      urls_to_add = [u for u in urls_to_add if not (u.startswith(url_following) or os.path.dirname(url).startswith(StorageWebMedium.transformer_for_comparison(u)) or (u.startswith('/m/signin')))]
  
      return back_up_content, assets_urls, urls_to_add, backup_name
    except Exception as e:
      raise Exception(f"Cannot back up '{url}': {e}")

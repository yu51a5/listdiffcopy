import os 
import bs4
import html2text

h = html2text.HTML2Text()
h.ignore_links = False
h.body_width = 0
h.ignore_images = False # DOESN'T WORK

from listdiffcopy.utils import put_together_framed_message, remove_char_and_after
from listdiffcopy.StorageWeb import StorageWeb

#################################################################################
class StorageWebMedium(StorageWeb):

  __start_ing_url = 'https://miro.medium.com/v2/'
  __medium_dot_com = 'medium.com'

  ###############################################################################
  def transformer_for_comparison(self, s):
    return remove_char_and_after(s=s, c='?')

  ###############################################################################
  def __init__(self, logger_name=None, objects_to_sync_logger_with=[]):
    super().__init__(logger_name=logger_name, objects_to_sync_logger_with=objects_to_sync_logger_with)

  ###############################################################################
  @classmethod
  def get_headers(cls):
    return {'User-Agent': "Mozilla/5.0 (compatible; Rigor/1.0.0; http://rigor.com)"}
    
  ###############################################################################
  def __get_url_pic(p):
    splints = str(p).split(', ')
    splints = [s[:s.find(' ')] for s in splints if s.startswith(StorageWebMedium.__start_ing_url)]
    splints = [StorageWebMedium.__start_ing_url + s[s.rfind('/')+1:] for s in splints]
    divergent = [s for s in splints if s != splints[0]]
    assert not divergent, splints
    url_pic = splints[0]
    return url_pic

  ###############################################################################
  def _get_root_url_other(self, url):

    __medium_dot_com_at = 'https://medium.com/@'

    if ('.' + StorageWebMedium.__medium_dot_com) in url:
      root_url = url[:url.find('.' + StorageWebMedium.__medium_dot_com)+len(StorageWebMedium.__medium_dot_com)+1]
    elif url.startswith(__medium_dot_com_at):
      next_slash = url.find('/', len(__medium_dot_com_at))
      root_url = url if next_slash < 0 else url[:next_slash]

    other = url[len(root_url):]
    if other.startswith('/'):
      other = other[1:]

    return root_url, other

  ###############################################################################
  def __find_all_linked_urls(self, source, root_url):
    what_to_add = {1 : root_url, 2 :  'https://medium.com'}

    all_as = source.find_all("a")
    urls_to_add = [a_tag['href'] for a_tag in all_as]

    for i, u in enumerate(urls_to_add):
      if (u[0] == '/') and (u.count('/') in (1, 2)):
        urls_to_add[i] = os.path.join(what_to_add[2 if '@' in u else u.count('/')], u[1:])

    wrong_starts = [os.path.join(a, b) for a in ('', 'https://medium.com', root_url, '/') for b in ('m/signin', 'tag', 'following', 'followers', 'lists', 'list/')]

    urls_to_add = [u for u in urls_to_add if not (self.transformer_for_comparison(u) in (root_url, root_url+'/')
                    or any([u.startswith(s) for s in wrong_starts]))]

    return urls_to_add

  ###############################################################################
  def _url_to_backup_content_hrefs(self, url, save_texts, save_assets):
    try:

      errors = []
      if not url.startswith('https://'):
        errors.append(f'{url} does not start with "https://"')
      if StorageWebMedium.__medium_dot_com not in url:
        errors.append(f'{url} does not containt "{StorageWebMedium.__medium_dot_com}"')
      assert not errors, f'{url} is not valid: ' + ', '.join(errors)

      root_url, other = self._get_root_url_other(url)
      if not other: # home page
        _, source_string = StorageWeb._get_page_source_with_scrolling(url=url)
        source = bs4.BeautifulSoup(source_string, "html.parser")
        all_articles = source.find_all("article")
        urls_to_add = [root_url+'/about']
        for aa in all_articles:
          urls_to_add += self.__find_all_linked_urls(source=aa, root_url=root_url)
        return None, None, None, urls_to_add, None

      backup_name = self.transformer_for_comparison(other)
      main_tag = 'article' if backup_name.lower() != 'about' else 'main'
      source = self._url_to_part_of_source(url=url, tag=main_tag)

      assets_urls = set()
      if save_assets:
        pictures = source.find_all('picture')
        for p in pictures:
          url_pic = StorageWebMedium.__get_url_pic(p)
          assets_urls.add(url_pic)

      contents = None
      if save_texts:
        captions_images = []
        all_divs = source.find_all("div")

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
            url_pic = StorageWebMedium.__get_url_pic(p)
            captions_images[-1][1].append(os.path.basename(url_pic))

        article_text = h.handle(str(source))
        article_text = article_text[:article_text.find('\n[![')] + article_text[article_text.find('Share\n')+6:] 
        contents = (put_together_framed_message(message='Backing up ' + url)
                           + article_text
                           + put_together_framed_message(message='Pictures')
                           + ''.join([f'{i+1}. {ci[0]} : {ci[1]}\n' for i, ci in enumerate(captions_images)]))



      urls_to_add = self.__find_all_linked_urls(source=source, root_url=root_url)

      return source, contents, assets_urls, urls_to_add, backup_name
    except Exception as e:
      raise Exception(f"Cannot back up '{url}': {e}")

  ###############################################################################
  def generate_toc(self, url):
    cont = self._url_to_part_of_source(url=url, tag='article')
    headers = cont.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    result = [f'#{ c["id"] } {"--" * int(c.name[1])} {c.text}' for c in headers]
    #[f'<a href="#{ c["id"] }"> {"-" * int(c.name[1])} {c.text} </a>' for c in headers]
    return result

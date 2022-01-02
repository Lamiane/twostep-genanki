import urllib.request
from tqdm import tqdm
from bs4 import BeautifulSoup
from .card import ensure_guid_uniqueness

# Here are general functions for all scrapers.
# Moreover, each specific scraper should define the following functions:
# - get_link(search_word) -> str
# - get_cards(soup_content) -> List(api.CardContent)

def get_web_content(url):
    with urllib.request.urlopen(url) as f:
        html_doc = f.read()
    content = BeautifulSoup(html_doc, 'html.parser')
    return content


def scrap(words, scraper, **kwargs):
    """Scrap words with scraper."""
    all_cards = []
    for search_word in tqdm(words, desc='Scraping...'):
        some_url = scraper.get_link(search_word, **kwargs)
        soup = get_web_content(some_url)
        all_cards.extend(scraper.get_cards(soup))

    ensure_guid_uniqueness(all_cards)
    return all_cards


def make_finder(tag_name, attr_name, attr_val):
    """
    finds <tag_name attr_name="attr_val" ...>...</tag_name>
    use with BeautifulSoup.find_all
    """
    return lambda tag: tag.name==tag_name and tag.has_attr(attr_name) and attr_val in tag.attrs[attr_name]


def peel(x):
    """often used on BeautifulSoup.find_all results"""
    assert len(x) == 1, f"Length should be 1, is {len(x)}."
    return x[0]

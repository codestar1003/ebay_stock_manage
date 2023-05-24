# import re
from importlib import import_module
# List Scraping Sites
scraping_site = [
    'auctions',
    'mercari',
    'fril',
    'amazon',
    'rakuten',
    'shopping',
    '2ndstreet',
    'hardoff',
    'suruga-ya',
    'yodobashi',
]

def select_engine(url):
    result = ''
    for site in scraping_site:
        if(site in url):
            result = site
            break

    if result:
        module = import_module(f'product.scrape.{result}')
        engine = getattr(module, 'ScrapingEngine')
        return engine
    
    return None
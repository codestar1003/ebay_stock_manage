import json
from django.conf import settings
from importlib import import_module

def select_engine(url):
    scraping_site = {}

    with open(file=str(settings.BASE_DIR / 'utils/scrape_site.txt'),  mode='r', encoding='utf-8') as f:
        scraping_site = json.loads(f.read())

    result = ''
    for site in scraping_site.keys():
        if site in url:
            result = site
            break
        
    if result:
        module = import_module(f'product.scrape.{result}')
        engine = getattr(module, 'ScrapingEngine')
        return engine
    
    return None
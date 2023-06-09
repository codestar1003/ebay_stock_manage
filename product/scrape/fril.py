import requests
from bs4 import BeautifulSoup as bs

from utils.converttext import convert_text


class ScrapingEngine:
    def scrape_data(self, source_url):
        resp = requests.get(
            url=source_url,
        )
        dom = bs(resp.content, 'html.parser')
        item_detail = dom.find('div', attrs={'class': 'item_detail'})
        data = {}
        data['title_jp'] = convert_text(item_detail.find('h1', attrs={'class': 'item__name'}).text)
        data['price'] = int(item_detail.find('span', attrs={'class': 'item__value'}).text[1:].replace(',', ''))
        data['description_jp'] = []
        descriptions = item_detail.find('div', attrs={'class': 'item__description__line-limited'}).a.span.contents
        for description in descriptions:
            if(isinstance(description, str) and description.isspace() is not True):
                data['description_jp'].append(convert_text(description))
        data['photos'] = []
        photos = item_detail.find('div', attrs={'id': 'photoFrame'}).find_all('img')
        for photo in photos:
            data['photos'].append(
                {
                    'url': photo['src']
                }
            )
        return data

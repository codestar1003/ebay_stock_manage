import requests
from bs4 import BeautifulSoup as bs

from utils.converttext import convert_text


class ScrapingEngine:
    def scrape_data(self, source_url):
        resp = requests.get(
            url=source_url,
        )
        dom = bs(resp.content, 'html.parser')
        data = {}
        data['title'] = convert_text(dom.find('div', attrs={'itemprop': 'name'}).text)
        data['price'] = int(dom.find('span', attrs={'itemprop': 'price'})['content'])
        data['description'] = [convert_text(dom.find('div', attrs={'itemprop': 'description'}).text)]
        data['photos'] = []
        photos = dom.find('div', attrs={'id': 'goodsImages'}).find('div', attrs={'id': 'sliderWrap'}).find('ul', attrs={'id': 'sliderThumbnail'}).find_all('img')
        for photo in photos:
            data['photos'].append(photo['src'])

        return data

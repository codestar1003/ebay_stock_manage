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

        isValid = True

        try:
            data['purchase_price'] = int(item_detail.find('span', attrs={'class': 'item__value'}).text[1:].replace(',', ''))
        except:
            isValid = False
            data['nothing'] = True

        if isValid:
            data['product_name'] = item_detail.find('h1', attrs={'class': 'item__name'}).text
            data['nothing'] = False

        return data

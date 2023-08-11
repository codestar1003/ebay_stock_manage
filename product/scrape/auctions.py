# import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs

# from django.conf import settings

from utils.converttext import convert_text


class ScrapingEngine:
    def scrape_data(self, source_url):
        # with open(file=str(settings.BASE_DIR / 'utils/settings_attrs.txt'),  mode='r', encoding='utf-8') as f:
        #     settings_attrs = f.read()

        # res = json.loads(settings_attrs)

        resp = requests.get(
            url=source_url,
        )
        dom = bs(resp.content, 'html.parser')
        data = {}

        try:
            data['purchase_price'] = int(convert_text(dom.find('dd', attrs={'class': 'Price__value'}).contents[0].strip('円')).replace(',', ''))

            data['product_name'] = convert_text(dom.find('h1', attrs={'class': 'ProductTitle__text'}).text)
            product_date = convert_text(dom.find_all('td', attrs={'class': 'Section__tableData'})[-2].text).replace('（月）', ' ')

            data['nothing'] = False

            date_format = '%Y.%m.%d %H:%M'
            date1 = datetime.strptime(product_date, date_format)
            date2 = datetime.now()

            if date1 < date2:
                data['nothing'] = True

        except:
            data['nothing'] = True
            
        return data

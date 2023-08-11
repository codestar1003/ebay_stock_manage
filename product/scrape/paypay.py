import json
from django.conf import settings
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from utils.converttext import convert_text


class ScrapingEngine:
    def scrape_data(self, source_url):
        with open(file=str(settings.BASE_DIR / 'utils/settings_attrs.txt'),  mode='r', encoding='utf-8') as f:
            settings_attrs = f.read()

        res = json.loads(settings_attrs)

        options = webdriver.ChromeOptions() 
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.get(source_url)

        driver.implicitly_wait(5)
        dom = bs(driver.page_source, "html.parser")
        data = {}

        try:
            price = dom.find('span', attrs={'class': 'sc-f27eb67d-0 euzCBb ItemPrice__Component'}).text.replace(',', '')
            data['purchase_price'] = price.replace('円', '')
            data['product_name'] = dom.find('span', attrs={'class': 'sc-5ea3dbc3-0 bdURdq'}).text
            data['nothing'] = False

            date = dom.find('span', attrs={'class': 'sc-5ea3dbc3-0 dguVSe'}).text

            if date != None and date.find(res['paypay']) != -1:
                data['nothing'] = False

        except:
            data['nothing'] = True
            
        return data

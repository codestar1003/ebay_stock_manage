import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver

from utils.converttext import convert_text


class ScrapingEngine:
    def scrape_data(self, source_url):
        options = webdriver.ChromeOptions() 
        options.headless = True
        driver = webdriver.Chrome()
        driver.get(source_url)
        data = {}
        time.sleep(10)
        dom = bs(driver.page_source, "html.parser")

        data['title_jp'] = convert_text(dom.find('span', attrs={'class': 'normal_reserve_item_name'}).b.text)
        data['price'] = int(dom.find('div', attrs={'id': 'priceCalculationConfig'})['data-price'])
        data['description_jp'] = []
        descriptions = dom.find('span', attrs={'class': 'item_desc'})
        if descriptions:
            for description in descriptions:
                description = convert_text(description.text)
                if(description):
                    data['description_jp'].append(description)
        data['photos'] = []
        photos = dom.find_all('meta', attrs={'itemprop': 'image'})
        for photo in photos:
            data['photos'].append(
                {
                    'url': photo['content']
                }
            )

        return data
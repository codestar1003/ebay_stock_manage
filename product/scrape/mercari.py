import json
import requests
from bs4 import BeautifulSoup as bs

from utils.converttext import convert_text
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager 

class ScrapingEngine:
    def scrape_data(self, source_url):
        # product_id = source_url.split('/')[-1]
        # url = f'https://api.mercari.jp/items/get?id={product_id}&include_product_page_component=true'
        # headers = {
        #     "authority": "api.mercari.jp",
        #     "method": "GET",
        #     "dpop": "eyJ0eXAiOiJkcG9wK2p3dCIsImFsZyI6IkVTMjU2IiwiandrIjp7ImNydiI6IlAtMjU2Iiwia3R5IjoiRUMiLCJ4IjoiU20ycU4xVG1wUVBxLTdlVW5EanNtSThVbGtONFYzQkVKYUhBbFN4VlhCbyIsInkiOiJrazBuVlc0N1VGbmJnSjBtNGN3NWlDamxFLVl1dlF1RV9rLTVNTDNsRjhVIn19.eyJpYXQiOjE2ODQ1NDkzNjcsImp0aSI6Ijc5ZmM3YzM4LTVjNTAtNDc4Ni05NDM3LWVhZjAyZjQwMTc5ZSIsImh0dSI6Imh0dHBzOi8vYXBpLm1lcmNhcmkuanAvaXRlbXMvZ2V0IiwiaHRtIjoiR0VUIiwidXVpZCI6IjYwNWI4ZGY1LTNjYTctNGY2NC04MDdlLTk0ODQ2YzljNDhjYiJ9.bez2b_nUo3F9vsZci1_QKLwGhVYBqqsRxQDokj4tqXisYTlpuw-B4HVjFG_qlNBcE52G061MFKKR2OLJpGIGng",
        #     "x-platform": "web",
        # }
        # resp = requests.get(
        #     url=url,
        #     headers=headers
        # )
        # object = json.loads(resp.text)
        # data = {}
        # data['title_jp'] = convert_text(object['data']['name'])
        # data['price'] = object['data']['price']
        # data['description_jp'] = [convert_text(object['data']['description'])]
        # data['photos'] = []
        # for photo in object['data']['photo']:
        #     data['photos'].append(
        #         {
        #             'url': photo
        #         }
        #     )
        # return data
        options = webdriver.ChromeOptions() 
        options.headless = True
        
        with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install())) as driver:
            driver.get(source_url)
            dom = bs(driver.page_source, "html.parser")
            data = {}
            data['title_jp'] = convert_text(dom.find('div', attrs={'data-testid': 'name'}).div.h1.text)
            data['price'] = int(dom.find('div', attrs={'data-testid': 'price'}).find_all('span')[-1].text)
            data['description_jp'] = [convert_text(dom.find('pre', attrs={'data-testid': 'description'}).text)]
            data['photos'] = dom.find('script', attrs={'type': 'application/ld+json'})

import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from utils.converttext import convert_text


class ScrapingEngine:
    def scrape_data(self, source_url):
        options = webdriver.ChromeOptions() 
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.get(source_url)

        driver.implicitly_wait(5)
        dom = bs(driver.page_source, "html.parser")
        data = {}
        isValid = True

        try:
            price = dom.find('span', attrs={'class': 'sc-f27eb67d-0 euzCBb ItemPrice__Component'}).text.replace(',', '')
            data['purchase_price'] = price.replace('円', '')
        except:
            isValid = False
            data['nothing'] = True

        if isValid:
            data['product_name'] = dom.find('span', attrs={'class': 'sc-5ea3dbc3-0 bdURdq'}).text
            data['nothing'] = False

        return data

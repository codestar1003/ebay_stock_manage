import time
# from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By

# from utils.converttext import convert_text


class ScrapingEngine:
    def scrape_data(self, source_url):
        options = webdriver.ChromeOptions() 
        options.headless = True
        driver = webdriver.Chrome(options=options)

        driver.get(source_url)

        driver.implicitly_wait(5)
        data = {}
        # dom = bs(driver.page_source, "html.parser")

        try:
            data['purchase_price'] = int(driver.find_element(By.XPATH, "//*[@id='item-info']/section[1]/section[1]/div/div/span[2]").text.replace(',', ''))
            data['product_name'] = driver.find_element(By.XPATH, "//*[@id='item-info']/section[1]/div[1]/div/div/h1").text
            product_date = driver.find_element(By.XPATH, "//*[@id='item-info']/section[2]/p").text

            data['nothing'] = False

            if product_date == '半年以上前':
                data['nothing'] = True
        except:
            data['nothing'] = True

        return data

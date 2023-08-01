import time
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
        data = {}
        dom = bs(driver.page_source, "html.parser")

        isValid = False

        try:
            driver.find_element(By.CLASS_NAME, "merEmptyState")
            # element = driver.find_element(By.XPATH, "//*[@id='main']/div/div[1]/p")
            
        except:
            isValid = True
            data['nothing'] = True
        
        if isValid == True:
            data['product_name'] = convert_text(dom.find('div', attrs={'data-testid': 'name'}).div.h1.text)
            data['purchase_price'] = int(dom.find('div', attrs={'data-testid': 'price'}).find_all('span')[-1].text.replace(',', ''))
            product_date = convert_text(dom.find('p', attrs={'class': 'merText body__5616e150 secondary__5616e150'}).text)

            data['nothing'] = False

            if product_date == '半年以上前':
                data['nothing'] = True

        return data

import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager 

from utils.converttext import convert_text


class ScrapingEngine:
    def scrape_data(self, source_url):
        # headers = {
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        #     'Accept-Encoding': 'gzip, deflate, br',
        #     'Accept-Language': 'en-US,en;q=0.9',
        #     'Cache-Control': 'max-age=0',
        #     'Cookie': 'Rt=78aedf5d1452eb075598b9cf62ae8e55; _ra=1678777081921|103df8e5-1470-4e3d-a893-3dee7d4df659; __lt__cid.3df24f5b=f7e4ff28-f578-424c-866c-9a8e838abe8d; __adtdpuid2=7c08a893-e5da-4aed-9522-28e5f58810f2; _gcl_au=1.1.693553807.1683527017; s_pers=%20s_mrcr%3D1100400000000000%257C4000000000000%257C4000000000000%257C4000000000000%7C1841207236721%3B; Rp=2519c5a7aad2169a68a7d312a064641b54bae91; Re=1.7.1.0.0.303656.2:16.7.2.6.0.100276.1:10.15.1.1.10.402055.1:10.15.1.1.7.402037.1:10.15.1.1.3.204952.1:21.6.1.0.0.215698.1:26.1.2.0.0.568377.2:13.2.1.0.0.303078.1:32.5.1.9.0.208207.1:21.5.1.0.0.215476.1:22.7.15.0.0.508456.10-1.7.1.0.0.303656.2:16.7.2.6.0.100276.1:10.15.1.1.10.402055.1:10.15.1.1.7.402037.1:10.15.1.1.3.204952.1:21.6.1.0.0.215698.1:26.1.2.0.0.568377.2:13.2.1.0.0.303078.1:32.5.1.9.0.208207.1:21.5.1.0.0.215476.1:22.7.15.0.0.508456.10; ak_bmsc=5C3A12545AB559D2575EB7A0901AB15A~000000000000000000000000000000~YAAQnutGaC/knASIAQAAqoexNxP0etEQ2b1rEKAOFq831SMF3ajMpgU2GKIQR861crFV78+6ggU8sMdcYA3Z6gYx9dVc06UbeVELLqs2s7BlVJ/9ZiCY1JoOBYoot3FY6vz8ZdtzI7rkKU7HwwbnxdVs49LFKuXsvMk6kiJKPYUqKaO/iv4mvRS6gavKr8uj+QUPC/4qsqBaToE0efsVhuN3ZRXNC+5ajU2Eiw9BNBkuMgxMOnSSnbWbZ1ik0rE0aRsXZPMb8dg627l5B29wJ9vLtHRYCn5nYCcjzkT7k/Gpf2etJGISaN9pNHgsuJtPH1oahifRuJwWqmuIboqOqDFRFSo1xUrkpbGTizYJsuM5MHss7ICUIPGKEshSG7VX0F47VUB/bBGAI8LIzA18ytbLqVlQmf05K/gj7oV6GFGgG6V/q9UGNecLnWhklc/ONpV+2HgaJg1aw+AzGuAI7HQpqCPzAqoK9rrK4mPUMyAG2F5oa7AqXMX4HFE=; rat_v=9c2497c27942e8fbd8ce11234964685e9a5060a; __lt__sid.3df24f5b=04fa9369-399600ba; cto_bundle=i-2XUF9jdFpmS0dZUHpGZlpBemZxOTZUbFZTc1FaTmluN1NEZiUyRklzR0hTUmVCYlJYNkZ3SUloMkJlTktYV3E3MnROdW5nZHFkVSUyRiUyQk5qSUJyeEl3TFFXYiUyQnpIdCUyRnZNMlZIJTJGVXVTT2JTUGw2bzVLJTJGdjJJUXZUVVZoVU1WcjJBYUZPZ2slMkJhckI2TGdrdGdqRSUyRlhqbnpBJTJGbWxFdyUzRCUzRA',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        # }
        # resp = requests.get(
        #     url=source_url,
        #     headers=headers
        # )
        options = webdriver.ChromeOptions() 
        options.headless = True
        with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options) as driver:
            driver.get(source_url)
            dom = bs(driver.page_source, "html.parser")
            data = {}
            data['title_jp'] = convert_text(dom.find('span', attrs={'class': 'normal_reserve_item_name'}).b.text)
            data['price'] = int(dom.find('div', attrs={'id': 'priceCalculationConfig'})['data-price'])
            data['description_jp'] = []
            descriptions = dom.find('span', attrs={'class': 'item_desc'}) 
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
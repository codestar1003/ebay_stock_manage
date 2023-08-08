import environ
import os
import sys

from pathlib import Path

import time
import datetime
import json

from django.conf import settings
from utils.convertcurrency import convert
from product.scrape.engineselector import select_engine

from ebaysdk.trading import Connection

import psycopg2

def config():
    env = environ.Env()
    BASE_DIR = Path(__file__).resolve().parent
    env.read_env(str(BASE_DIR / ".env"))

    databases = {
        'host': env('DB_HOST'),
        'db_name': env('DB_NAME'),
        'user': env('DB_USER'),
        'password': env('DB_PASSWORD'),
        'port': env('DB_PORT'),
    }

    return databases

def scrape_data(url):
    engine = select_engine(url=url)
    if engine:
        engine = engine()
        try:
            data = engine.scrape_data(source_url = url)
            # data['price_en'] = convert('JPY', 'USD', data['purchase_price'])

        except Exception as err:
            raise err
        
        return data

def revise_item(ebay_url):
    item_number = ''
    ebay_setting = {}

    if ebay_url == '':
        return False
    
    item_number = ebay_url.split("/", -1)

    with open(file=str('utils/ebay_settings.txt'), mode='r', encoding='utf-8') as f:
        ebay_setting = json.loads(f.read())
    
    try:
        # Set up the API connection
        api = Connection(appid = ebay_setting['app_id'], devid = ebay_setting['dev_id'], certid = ebay_setting['cert_id'], token = ebay_setting['ebay_token'], config_file=None)

        item = {
            'Item': {
                'ItemID': item_number,
                'Quantity': 0
            }
        }
        api.execute('ReviseItem', item)

        return True
    
    except:
        return False

def send_mail():

    return True
            

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'productmanage.settings')

    setting = {}
    params = config()

    with open(file=str('utils/settings_attrs.txt'), mode='r', encoding='utf-8') as f:
        setting = json.loads(f.read())

    varience = setting['variable_price']

    sql = "SELECT * FROM product_product ORDER BY id ASC"
     
    while True:
        """ query data from the vendors table """
        conn = None

        try:
            conn = psycopg2.connect(
                database = params['db_name'],
                host = params['host'],
                user = params['user'],
                password = params['password'],
                port = params['port']
            )

            cur = conn.cursor()
            cur.execute(sql)

            rows = cur.fetchall()

            for row in rows:
                url = row[5]
                ebay_url = row[6]
                price = row[7]

                if url == '':
                    continue
                
                data = scrape_data(url)

                if data['nothing']:
                    sql = "INSERT INTO product_deletedlist (created_at, updated_at, product_name, ec_site, purchase_url, ebay_url, purchase_price, sell_price_en, profit, profit_rate, prima, shipping, quantity, notes, created_by, deleted_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], datetime.datetime.now())
                    
                    cur.execute(sql, val)

                    # delete record
                    sql = "DELETE FROM product_product WHERE id='" + row[0] + "'" + row[0] + "'"
                    cur.execute(sql)

                    # set ebay product quantity 0
                    if ebay_url != '':
                        revise_item(ebay_url)

                # check variance change
                if data['purchase_price'] > 0 and abs(data['purchase_price'] - price) > int(varience):
                    send_mail()

            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
            
        # monitering variable change and send mail
        # if abs(data['price_jp'] - item.price) > setting.variable_price:
        #     send_mail() 
                

        time.sleep(600)

    return True

if __name__ == '__main__':
    main()

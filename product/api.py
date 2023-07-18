import csv
import json
import requests
import uuid

from django.conf import settings
from io import BytesIO
from PIL import Image
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from dry_rest_permissions.generics import DRYPermissions

from ebaysdk.trading import Connection
from .models import Product, DeletedList
from .serializers import ProductSerializer, DeletedListSerializer
from product.scrape.engineselector import select_engine
from utils.convertcurrency import convert
from utils.ebay_policy import DISPATCHTIMEMAX, RETURN_POLICY, SHIPPING_POLICY
from utils.scrape_site import scraping_site
from utils.profit_formula import profit_formula
from .filterbackend import FilterBackend

class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = (DRYPermissions, )
    # filter_backends = [FilterBackend, SearchFilter]
    # filterset_fields = ['status']
    # search_fields = ['item_number', 'title_en', 'url', 'price_en', 'shipping_policy']

    def get(self, request):
        print(request.GET.get())

        print(data)
        return Response(data, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['GET'])
    def products(self, request):
        products = Product.objects.all()
        
        return Response(
            {'products': products},
            status=200
        )
        

    @action(detail=False, methods=['POST'])
    def scrape_data(self, request):
        url = request.data['url']
        engine = select_engine(url=url)
        if engine:
            engine = engine()
            try:
                data = engine.scrape_data(source_url=url)
                data['price_en'] = convert('JPY', 'USD', data['price_jp'])

                return Response(
                    data=data,
                    status=200
                )
            except Exception as err:
                raise err
        
        return Response(
            data='入力したサイトへのサービスはまだサポートされていません。',
            status=400
        )

            
    @action(detail=False, methods=['POST'])
    def validate_product(self, request):
        info = request.data['product_info']
        ecsite = info['ecsite_url']
        ebay = info['ebay_url']
        itemID = info['item_id']

        # validate duplicate
        products = Product.objects.filter(ebay_url=ebay)

        if len(products) > 0:
            return Response({'valid': False, 'error': 'すでに存在しています！'}, status=200) 

        # Get ebay information
        # try:
            # Set up the API connection
            # api = Connection(appid=request.user.app_id, devid=request.user.dev_id, certid=request.user.cert_id, token=request.user.ebay_token, config_file=None)

            # response = api.execute(
            #     'GetItem',
            #     {
            #         'ItemID': itemID,
            #         'IncludeItemSpecifics': 'True'
            #     }
            # )

            # item_specifics = response.reply.Item.ItemSpecifics.NameValueList
            # required_specifics = []
            # optional_specifics = []
            
            # for item_specific in item_specifics:
            #     if(getattr(item_specific, 'Name') == 'Brand' or getattr(item_specific, 'Name') == 'Type'):
            #         required_specifics.append(
            #             {
            #                 'Name': item_specific.Name,
            #                 'Value': item_specific.Value,
            #                 'Condition': 'Required',
            #             }
            #         )
            #     else:
            #         optional_specifics.append(
            #             {
            #                 'Name': item_specific.Name,
            #                 'Value': item_specific.Value,
            #                 'Condition': 'Optional',
            #             }
            #         )
            # result = required_specifics + optional_specifics

        #     return Response(
        #         data=result,
        #         status=200
        #     )
        # except Exception as err:
        #     return Response({'error': 'Invalid eBay product info!'})

        # Scraping data
        # engine = select_engine(url=ecsite)
        # if engine:
        #     engine = engine()
        #     try:
        #         data = engine.scrape_data(source_url=ecsite)
        #         # data['price_en'] = convert('JPY', 'USD', data['price_jp'])

        #         print(data['price_jp'])

        #         return Response(
        #             data=data,
        #             status=200
        #         )
        #     except Exception as err:
        #         raise err
        
        # return Response(
        #     {'valid': False, 'error': '入力したサイトへのサービスはまだサポートされていません。'}, status=200
        # )

        return Response({'valid': True}, status=200)
        


    @action(detail=False, methods=['POST'])
    def get_item_specific(self, request):
        item_number = request.data['item_number']

        try:
            # Set up the API connection
            api = Connection(appid=request.user.app_id, devid=request.user.dev_id, certid=request.user.cert_id, token=request.user.ebay_token, config_file=None)
            response = api.execute(
                'GetItem',
                {
                    'ItemID': item_number,
                    'IncludeItemSpecifics': 'True'
                }
            )
            item_specifics = response.reply.Item.ItemSpecifics.NameValueList
            required_specifics = []
            optional_specifics = []
            for item_specific in item_specifics:
                if(getattr(item_specific, 'Name') == 'Brand' or getattr(item_specific, 'Name') == 'Type'):
                    required_specifics.append(
                        {
                            'Name': item_specific.Name,
                            'Value': item_specific.Value,
                            'Condition': 'Required',
                        }
                    )
                else:
                    optional_specifics.append(
                        {
                            'Name': item_specific.Name,
                            'Value': item_specific.Value,
                            'Condition': 'Optional',
                        }
                    )
            result = required_specifics + optional_specifics
            return Response(
                data=result,
                status=200
            )
        except Exception as err:
            raise err
    
    @action(detail=False, methods=['POST'])
    def add_item(self, request):
        # Product
        item = request.data['product']
        order = request.data['order']

        product = ()

        if order == '0':
            product = Product(
                created_at=item['created_at'],
                product_name=item['product_name'],
                ec_site=item['ec_site'],
                purchase_url=item['purchase_url'],
                ebay_url=item['ebay_url'],
                purchase_price=item['purchase_price'],
                sell_price_en=item['sell_price_en'],
                profit=item['profit'],
                prima=item['prima'],
                shipping=item['shipping'],
                quantity=item['quantity'],
                created_by=item['created_by'],
                notes=item['notes']
            )
            
        else:
            product = Product(
                created_at=item['created_at'],
                updated_at='',
                product_name=item['product_name'],
                ec_site=item['ec_site'],
                purchase_url=item['purchase_url'],
                ebay_url=item['ebay_url'],
                purchase_price=item['purchase_price'],
                sell_price_en=item['sell_price_en'],
                profit=item['profit'],
                prima=item['prima'],
                shipping=item['shipping'],
                quantity=item['quantity'],
                order_num=item['order_num'],
                ordered_at=item['ordered_at'],
                created_by=item['created_by'],
                notes=item['notes']
            )
        print(item['created_at'])
        
        product.save()

        return Response(
            {'Success!'},
            status=200
        )
        
        # except Exception as err:
        #     return Response(
        #         {'error': '商品登録作業が失敗しました！'}, status=200
        #     )

    @action(detail=True, methods=['POST'])
    def revise_item(self, request, pk):
        product = Product.objects.get(pk=pk)
        sku = request.data['sku']
        sell_price = request.data['sell_price']
        quantity = request.data['quantity']
        profit = request.data['profit']
        result = ''
        for site in scraping_site.keys():
            if site in sku:
                result = scraping_site[site]
                break

        try:
            # Set up the API connection
            api = Connection(appid=request.user.app_id, devid=request.user.dev_id, certid=request.user.cert_id, token=request.user.ebay_token, config_file=None)
            item = {
                'Item': {
                    'ItemID': product.item_number,
                    'StartPrice': product.price_en,
                    'Quantity': product.quantity
                }
            }
            api.execute('ReviseItem', item)
            
            # Update Product
            product.url = sku
            product.site = result
            product.price_en = sell_price
            product.quantity = quantity
            product.profit = profit
            product.save()
            return Response(
                data='Success',
                status=200
            )

        except Exception as err:
            raise err

    @action(detail=False, methods=['POST'])
    def bulk_update_product(self, request):
        products = request.data['products']
        try:
            # Set up the API connection
            api = Connection(appid=request.user.app_id, devid=request.user.dev_id, certid=request.user.cert_id, token=request.user.ebay_token, config_file=None)
            
            for product in products:
                result = ''
                for site in scraping_site.keys():
                    if site in product['url']:
                        result = scraping_site[site]
                        break
                point = 0
                if product['point']:
                    point = int(product['point'])
                already_product = Product.objects.get(pk=product['id'])
                item = {
                    'Item': {
                        'ItemID': product['item_number'],
                        'StartPrice': product['price_en'],
                        'Quantity': product['quantity']
                    }
                }
                api.execute('ReviseItem', item)

                already_product.url = product['url']
                already_product.site = result
                already_product.quantity = product['quantity']
                already_product.price_en = float(product['price_en'])
                already_product.profit = profit_formula(
                    float(product['price_en']),
                    product['price_jp'],
                    'JPY',
                    str(product['item_category']),
                    point,
                    product['shipping_policy']
                )
                already_product.save()

            return Response(
                data='Success',
                status=200
            )
        except Exception as err:
            raise err

    @action(detail=True, methods=['POST'])
    def end_item(self, request, pk):
        product = Product.objects.get(pk=pk)
        try:
            # Set up the API connection
            api = Connection(appid=request.user.app_id, devid=request.user.dev_id, certid=request.user.cert_id, token=request.user.ebay_token, config_file=None)
            item = {
                'ItemID': product.item_number,
                'EndingReason': 'Incorrect'
            }
            api.execute('EndItem', item)
            
            # Update Product
            product.status = 'End'
            product.save()
            return Response(
                data='Success',
                status=200
            )
        except Exception as err:
            raise err

    # @action(detail=False, methods=['POST'])
    # def upload_product(self, request):
    #     data = request.data['product']
    #     for item in data:
    #         result = ''
    #         for site in scraping_site.keys():
    #             if site in item['SKU']:
    #                 result = scraping_site[site]
    #                 break

    #         product = Product(
    #             status='Publish',
    #             item_number=item['Item No'],
    #             url=item['SKU'],
    #             site=result,
    #             title_en=item['品名'],
    #             item_category=item['カテゴリNo'],
    #             price_en=item['売価($)'],
    #             price_jp=item['仕入値（円）'],
    #             quantity=item['数量'],
    #             point=item['ポイント'],
    #             shipping_policy=item['配送ポリシー'],
    #             profit=item['利益'],
    #             created_by=request.user,
    #             comment=item['備考']
    #         )
    #         product.save()
    #     return Response(
    #         data='Success',
    #         status=200
    #     )
    
    @action(detail=False, methods=['POST'])
    def upload_shipping_fee(self, request):
        fee = {}
        for shipping in request.data['shipping']:
            fee[list(shipping.items())[0][-1]] = list(shipping.items())[-1][-1]

        fee = json.dumps(fee, indent=4, ensure_ascii=False)
        with open(file=str(settings.BASE_DIR / 'utils/shipping_fee.txt'),  mode='w', encoding='utf-8') as f:
            f.write(fee)
        
        return Response(
            data='Success',
            status=200
        )

    
    @action(detail=False, methods=['GET'])
    def shipping_fee(self, request):
        with open(file=str(settings.BASE_DIR / 'utils/shipping_fee.txt'),  mode='r', encoding='utf-8') as f:
            fee = f.read()
        
        return Response(
            data=json.loads(fee),
            status=200
        )
    
    @action(detail=False, methods=['GET'])
    def settings_attr(self, request):
        with open(file=str(settings.BASE_DIR / 'utils/settings_attrs.txt'),  mode='r', encoding='utf-8') as f:
            settings_attrs = f.read()
        
        return Response(
            data=json.loads(settings_attrs),
            status=200
        )
    
    @action(detail=False, methods=['POST'])
    def update_settings_attr(self, request):
        settings_attr = request.data['settings_attr']
        with open(file=str(settings.BASE_DIR / 'utils/settings_attrs.txt'),  mode='w', encoding='utf-8') as f:
            f.write(json.dumps(settings_attr, indent=4))

        return Response(
            data='Success',
            status=200
        )
    
    @action(detail=False, methods=['GET'])
    def get_ecsites(self, request):
        with open(file=str(settings.BASE_DIR / 'utils/ecsites.txt'),  mode='r', encoding='utf-8') as f:
            ecsites = f.read()
        
        return Response(
            data=json.loads(ecsites),
            status=200
        )
    
    @action(detail=False, methods=['POST'])
    def update_ecsites(self, request):
        ecsites = request.data['ecsites']
        with open(file=str(settings.BASE_DIR / 'utils/ecsites.txt'),  mode='w', encoding='utf-8') as f:
            f.write(json.dumps(ecsites, indent=4))

        return Response(
            data='Success',
            status=200
        )
    
    @action(detail=False, methods=['POST'])
    def download_product(self, request):
        with open(file=str(settings.BASE_DIR / 'media/products.csv'),  mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ['Item No', '品名', 'SKU', 'eBay', '数量', '仕入値（円）', 'ポイント', '売価($)', '利益', 'カテゴリNo', '配送ポリシー', '備考']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for product in Product.objects.all():
                writer.writerow({
                    'Item No': product.item_number, 
                    '品名': product.title_en, 
                    'SKU': product.url, 
                    'eBay': '販売先', 
                    '数量': product.quantity, 
                    '仕入値（円）': product.price_jp, 
                    'ポイント': product.point, 
                    '売価($)': product.price_en, 
                    '利益': product.profit, 
                    'カテゴリNo': product.item_category, 
                    '配送ポリシー': product.shipping_policy, 
                    '備考': product.comment,
                })
        return Response(
            data='Success',
            status=200
        )
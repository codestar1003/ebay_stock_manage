import csv
import json
import requests
import translators as ts
import uuid

from django.conf import settings
from io import BytesIO
from PIL import Image
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from dry_rest_permissions.generics import DRYPermissions

from ebaysdk.trading import Connection
from .models import Product, ProductDescription, ProductPhoto
from .serializers import ProductSerializer, ProductDescriptionSerializer, ProductPhotoSerializer
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
    filter_backends = [FilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        else:
            return Product.objects.filter(created_by=self.request.user)

    @action(detail=False, methods=['POST'])
    def scrape_data(self, request):
        url = request.data['url']
        engine = select_engine(url=url)
        if engine:
            engine = engine()
            try:
                data = engine.scrape_data(source_url=url)
                data['title_en'] = ts.translate_text(query_text=data['title_jp'], from_language='ja', to_language='en')
                data['price_en'] = convert('JPY', 'USD', data['price_jp'])
                
                # Photo
                for photo in data['photos']:
                    response = requests.get(photo['url'])
                    image = Image.open(BytesIO(response.content))
                    photo['width'] = image.width
                    photo['height'] = image.height

                # Description
                data['description_en'] = []
                for description in data['description_jp']:
                    description_en = ts.translate_text(query_text=description, from_language='ja', to_language='en')
                    data['description_en'].append(description_en)

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
    def translate(self, request):
        text = request.data['text']
        try: 
            text_en = ts.translate_text(query_text=text, from_language='ja', to_language='en')
        except Exception as err:
            raise err
        else:
            return Response(
                data=text_en,
                status=200
            )

    @action(detail=False, methods=['POST'])
    def get_item_specific(self, request):
        item_number = request.data['item_number']
        
        # Set up the API connection
        api = Connection(appid=settings.APP_ID, devid=settings.DEV_ID, certid=settings.CERT_ID, token=settings.TOKEN, config_file=None)
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
    
    @action(detail=False, methods=['POST'])
    def add_item(self, request):
        # Product
        result = ''
        for site in scraping_site.keys():
            if site in request.data['sku']:
                result = scraping_site[site]
                break
        
        sell_price = float(request.data['price_en'])
        buy_price = request.data['price_jp']
        category_id = request.data['item_category']
        point = 0
        if request.data['point']:
            point = int(request.data['point'])
        shipping_policy = request.data['shipping_policy']
        profit = profit_formula(sell_price, buy_price, 'JPY', category_id, point, shipping_policy)

        product = Product(
            status='Draft',
            url=request.data['sku'],
            site=result,
            title_jp=request.data['title_jp'],
            title_en=request.data['title_en'],
            condition=request.data['condition'],
            condition_desc=request.data['condition_desc'],
            price_jp=request.data['price_jp'],
            price_en=request.data['price_en'],
            quantity=request.data['quantity'],
            location_country=request.data['location_country'],
            location_city=request.data['location_city'],
            item_category=request.data['item_category'],
            shipping_policy=request.data['shipping_policy'],
            profit=profit,
            created_by=request.user
        )
        if request.data['point']:
            product.point=request.data['point']
        product.save()

        # ProductPhoto
        photos = request.data['photos']
        for photo in photos:
            image = requests.get(photo['url'])
            random_name = uuid.uuid1()
            with open(f'{str(settings.BASE_DIR)}\\media\\productphoto\\{random_name}.png', 'wb') as f:
                f.write(image.content)
            image = Image.open(f'{str(settings.BASE_DIR)}\\media\\productphoto\\{random_name}.png')

            if(photo['width'] < 500):
                new_image = image.resize((500,500))
                new_image.save(f'{str(settings.BASE_DIR)}\\media\\productphoto\\{random_name}.png')
            elif(photo['width'] > 3000):
                new_image = image.resize((1600,1600))
                new_image.save(f'{str(settings.BASE_DIR)}\\media\\productphoto\\{random_name}.png')
            else:
                new_image = image.resize((photo['width'], photo['height']))
                new_image.save(f'{str(settings.BASE_DIR)}\\media\\productphoto\\{random_name}.png')

            productphoto = ProductPhoto(
                product=product,
                path=f'productphoto/{random_name}.png',
                width=photo['width'],
                height=photo['height']
            )
            productphoto.save()

        # ProductDescription
        productdescription = ProductDescription(
            product=product,
            description_jp=request.data['description_jp'],
            description_en=request.data['description_en']
        )
        productdescription.save()

        try:
            # Set up the API connection
            api = Connection(appid=settings.APP_ID, devid=settings.DEV_ID, certid=settings.CERT_ID, token=settings.TOKEN, config_file=None)
            
            # Authenticate and get a sesstion token
            # response = api.execute('GetSessionID', {})
            # session_id = response.reply.SessionID

            # Create a listing for the item
            namevaluelist = []
            for index, type in enumerate(request.data['item_specific_type']):
                namevaluelist.append({
                    'Name': type,
                    'Value': request.data['item_specific_value'][index]
                })
            with open(str(settings.BASE_DIR / 'product/descriptiontemplate/template1.txt')) as f:
                desc =f.read()
            content = productdescription.description_en.replace('\n', '<br/>')
            desc = desc.replace('<%DESC>', content)
            item = {
                'Item': {
                    'Title': product.title_en,
                    'Country': product.location_country,
                    'Location': product.location_city,
                    'ConditionID': product.condition,
                    'AutoPay': 'True',
                    'PrimaryCategory': {'CategoryID': product.item_category},
                    'Description': desc,
                    'ListingDuration': 'GTC',
                    'ListingType': 'FixedPriceItem',
                    'StartPrice': product.price_en,
                    'Currency': 'USD',
                    'Quantity': product.quantity,
                    'PictureDetails': {
                        'PictureURL': [f"{settings.SERVER_URL}{ProductPhotoSerializer(productphoto).data['path']}" for productphoto in product.productphoto_set.all()]  # Add at least one photo URL
                    },
                    'ItemSpecifics': {
                        'NameValueList': namevaluelist
                    },
                    'ReturnPolicy': RETURN_POLICY[request.data['return_policy']],
                    'ShippingDetails': SHIPPING_POLICY[request.data['shipping_policy']],
                    'DispatchTimeMax': DISPATCHTIMEMAX[request.data['shipping_policy']],
                    'PrivateListing': request.data['private_listing'],
                    'BestOfferDetails': {
                        'BestOfferEnabled': request.data['best_offer']
                    }
                }
            }
            response = api.execute('AddItem', item)

            product.status = 'Publish'
            product.item_number = response.reply.ItemID
            product.save()
            return Response(
                data='Success',
                status=200
            )
        except Exception as err:
            raise err

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
            api = Connection(appid=settings.APP_ID, devid=settings.DEV_ID, certid=settings.CERT_ID, token=settings.TOKEN, config_file=None)
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
            api = Connection(appid=settings.APP_ID, devid=settings.DEV_ID, certid=settings.CERT_ID, token=settings.TOKEN, config_file=None)
            
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
            api = Connection(appid=settings.APP_ID, devid=settings.DEV_ID, certid=settings.CERT_ID, token=settings.TOKEN, config_file=None)
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

    @action(detail=False, methods=['POST'])
    def upload_product(self, request):
        data = request.data['product']
        for item in data:
            result = ''
            for site in scraping_site.keys():
                if site in item['SKU']:
                    result = scraping_site[site]
                    break

            product = Product(
                status='Publish',
                item_number=item['Item No'],
                url=item['SKU'],
                site=result,
                title_en=item['品名'],
                item_category=item['カテゴリNo'],
                price_en=item['売価($)'],
                price_jp=item['仕入値（円）'],
                quantity=item['数量'],
                point=item['ポイント'],
                shipping_policy=item['配送ポリシー'],
                profit=item['利益'],
                created_by=request.user,
                comment=item['備考']
            )
            product.save()
        return Response(
            data='Success',
            status=200
        )
    
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
    def profit_attr(self, request):
        with open(file=str(settings.BASE_DIR / 'utils/profit_attrs.txt'),  mode='r', encoding='utf-8') as f:
            profit_attrs = f.read()
        
        return Response(
            data=json.loads(profit_attrs),
            status=200
        )
    
    @action(detail=False, methods=['POST'])
    def update_profit_attr(self, request):
        profit_attr = request.data['profit_attr']
        with open(file=str(settings.BASE_DIR / 'utils/profit_attrs.txt'),  mode='w', encoding='utf-8') as f:
            f.write(json.dumps(profit_attr, indent=4))

        return Response(
            data='Success',
            status=200
        )

    @action(detail=False, methods=['POST'])
    def currency_rate(self, request):
        currency = request.data['currency']
        url = 'https://api.exchangerate-api.com/v4/latest/USD'
        currencies = requests.get(url).json()['rates']
        rate = currencies[currency]

        return Response(
            data=rate,
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


class ProductPhotoViewSet(ModelViewSet):
    serializer_class = ProductPhotoSerializer
    queryset = ProductPhoto.objects.all()
    permission_classes = (DRYPermissions, )


    @action(detail=False, methods=['POST'])
    def upload_photo(self, request):
        random_name = uuid.uuid1()
        request.FILES['image'].name = f'{random_name}.png'
        productphoto = ProductPhoto(
            path=request.FILES['image']
        )
        productphoto.save()

        return Response(
            data=self.serializer_class(productphoto).data,
            status=200
        )

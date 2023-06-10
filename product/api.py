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


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = (DRYPermissions, )

    @action(detail=False, methods=['POST'])
    def scrape_data(self, request):
        url = request.data['url']
        engine = select_engine(url=url)()
        if engine:
            data = engine.scrape_data(source_url=url)
            data['title_en'] = ts.translate_text(query_text=data['title_jp'], from_language='ja', to_language='en')
            data['price'] = convert('JPY', 'USD', data['price'])
            
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
        
        return Response(
            data='入力したサイトへのサービスはまだサポートされていません。',
            status=400
        )

    @action(detail=False, methods=['POST'])
    def translate(self, request):
        text = request.data['text']
        try: 
            text_en = ts.translate_text(query_text=text, from_language='ja', to_language='en')
        except ConnectionError:
            raise ValueError('操作が失敗しました。もう一度お試しください。')
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
        product = Product(
            url=request.data['url'],
            title_jp=request.data['title_jp'],
            title_en=request.data['title_en'],
            brand=request.data['brand'],
            condition=request.data['condition'],
            condition_desc=request.data['condition_desc'],
            price=request.data['price'],
            quantity=request.data['quantity'],
            location_country=request.data['location_country'],
            location_city=request.data['location_city'],
        )
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
                'PrimaryCategory': {'CategoryID': request.data['item_category']},
                # 'PrimaryCategory': {'CategoryID': '33963'},
                'Description': desc,
                'ListingDuration': 'GTC',
                'ListingType': 'FixedPriceItem',
                'StartPrice': product.price,
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

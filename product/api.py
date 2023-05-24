import requests
import translators as ts
import uuid

from django.conf import settings
from PIL import Image
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from dry_rest_permissions.generics import DRYPermissions

from .models import Product, ProductDescription, ProductPhoto
from .serializers import ProductSerializer, ProductDescriptionSerializer, ProductPhotoSerializer
from product.scrape.engineselector import select_engine
from utils.convertcurrency import convert


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
            # Product
            title_en = ts.translate_text(query_text=data['title'], from_language='ja', to_language='en')
            price = convert('JPY', 'USD', data['price'])
            product = Product(
                url = url,
                title_jp = data['title'],
                title_en = title_en,
                condition='NEW',
                price = price,
                location_country='JAPAN'
            )
            product.save()

            # ProductPhoto
            for photo_url in data['photos']:
                image = requests.get(photo_url)
                random_name = uuid.uuid1()
                with open(f'{str(settings.BASE_DIR)}\\media\\productphoto\\{random_name}.png', 'wb') as f:
                    f.write(image.content)
                image = Image.open(f'{str(settings.BASE_DIR)}\\media\\productphoto\\{random_name}.png')
                width, height = image.size

                if(width < 500):
                    new_image = image.resize((500,500))
                    new_image.save(f'{str(settings.BASE_DIR)}\\media\\productphoto\\{random_name}.png')
                if(width > 3000):
                    new_image = image.resize((1600,1600))
                    new_image.save(f'{str(settings.BASE_DIR)}\\media\\productphoto\\{random_name}.png')
                
                photo = ProductPhoto(
                    product=product,
                    path=f'productphoto/{random_name}.png',
                    width=width,
                    height=height
                )
                photo.save()

            # ProductDescription
            for description in data['description']:
                description_en = ts.translate_text(query_text=description, from_language='ja', to_language='en', )
                product_description = ProductDescription(
                    product=product,
                    description_jp=description,
                    description_en=description_en
                )
                product_description.save()

            return Response(
                data=self.serializer_class(product).data,
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

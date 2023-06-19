from rest_framework import serializers
from .models import Product, ProductDescription, ProductPhoto
from users.serializers import UserSerializer

class ProductDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDescription
        exclude = ['created_at', 'updated_at']


class ProductPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhoto
        exclude = ['created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    productdescription_set = ProductDescriptionSerializer(
        many=True, read_only=False, required=False
    )

    productphoto_set = ProductPhotoSerializer(
        many=True, read_only=False, required=False
    )

    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
        depth = 1

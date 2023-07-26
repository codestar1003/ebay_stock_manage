from rest_framework import serializers
from .models import Product, DeletedList, ProductDescription, ProductPhoto

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"
        depth = 1

class DeletedListSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeletedList
        fields = "__all__"
        depth = 1

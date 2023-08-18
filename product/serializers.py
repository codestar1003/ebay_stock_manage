from rest_framework import serializers
from .models import Product, OrderList, DeletedList, MailList

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"
        depth = 1

class OrderListSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderList
        fields = "__all__"
        depth = 1

class DeletedListSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeletedList
        fields = "__all__"
        depth = 1

class MailListSerializer(serializers.ModelSerializer):

    class Meta:
        model = MailList
        fields = "__all__"
        depth = 1
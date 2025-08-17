from rest_framework import serializers
from .models import Customer, Product, Order


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order

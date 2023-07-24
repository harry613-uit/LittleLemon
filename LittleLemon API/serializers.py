from dataclasses import fields
from pkgutil import read_code
from pyexpat import model
from unicodedata import category
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import MenuItem, Category, Cart, OrderItem, Order

# serializer for customers and delivery team.
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']

# serializer for manager
class MenuItemSerializers(serializers.ModelSerializer):
    # category = serializers.StringRelatedField()
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']

class MenuItemSerializerPost(serializers.ModelSerializer):
    category = CategorySerializer(read_only = True)
    category_id = serializers.IntegerField(write_only = True)
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CartSerializer(serializers.ModelSerializer):
    # menuitem_id = serializers.IntegerField(write_only=True)
    price = serializers.SerializerMethodField(method_name= 'price')
    class Meta:
        model = Cart
        fields = ['id', 'quantity', 'unit_price','price', 'menuitem', 'user']
        read_only_fields = ['user', 'price']

    def price(self, object:Cart):
        return object.quantity * object.unit_price
    
    def create(self, validated_data):
        quantity = validated_data['quantity']
        unit_price = validated_data['unit_price']
        price = quantity*unit_price
        validated_data['price'] = price
        return super().create(validated_data)



class OrderSerializer(serializers.ModelSerializer):
    # order_item = OrderItemSerializer(read_only = True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']
        read_only_fields = ['user', 'total', 'date']

class OrderItemSerializer(serializers.ModelSerializer):
    order= OrderSerializer()
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']
        read_only_fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']
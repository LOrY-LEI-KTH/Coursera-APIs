from django.contrib.auth.models import User
from rest_framework import serializers

from .models import MenuItem, Cart, Category

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']
        read_only_fields = ('unit_price', 'price')  # Auto-calculated fields

    def create(self, validated_data):
        """ Automatically set unit_price and total price before saving """
        menuitem = validated_data['menuitem']
        quantity = validated_data.get('quantity', 1)

        unit_price = menuitem.price  # Get price from MenuItem
        total_price = unit_price * quantity

        cart_item = Cart.objects.create(
            user=self.context['request'].user,
            menuitem=menuitem,
            quantity=quantity,
            unit_price=unit_price,
            price=total_price
        )
        return cart_item

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']  # Fields you want to expose in the API
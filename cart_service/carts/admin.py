from django.contrib import admin

from carts.infrastructure.models import CartItemModel, CartModel

admin.site.register(CartModel)
admin.site.register(CartItemModel)

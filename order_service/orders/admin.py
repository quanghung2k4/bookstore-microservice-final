from django.contrib import admin

from orders.infrastructure.models import OrderItemModel, OrderModel

admin.site.register(OrderModel)
admin.site.register(OrderItemModel)

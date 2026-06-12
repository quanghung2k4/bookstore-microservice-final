from django.urls import path
from rest_framework.routers import DefaultRouter

from carts.presentation.views import CartItemViewSet, CartViewSet

router = DefaultRouter()
router.register("carts", CartViewSet, basename="cart")

cart_item_detail = CartItemViewSet.as_view({"patch": "partial_update", "delete": "destroy"})

urlpatterns = router.urls + [
    path("cart-items/<str:pk>/", cart_item_detail, name="cart-item-detail"),
]

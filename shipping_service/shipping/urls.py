from rest_framework.routers import DefaultRouter
from .views import ShippingAddressViewSet

router = DefaultRouter()
router.register("shipping", ShippingAddressViewSet, basename="shipping")

urlpatterns = router.urls

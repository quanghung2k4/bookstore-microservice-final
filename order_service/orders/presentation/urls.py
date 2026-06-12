from rest_framework.routers import DefaultRouter

from orders.presentation.views import OrderViewSet

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="order")

urlpatterns = router.urls

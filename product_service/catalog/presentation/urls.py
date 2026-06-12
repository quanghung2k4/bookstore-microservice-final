from rest_framework.routers import DefaultRouter

from catalog.presentation.views import BrandViewSet, CategoryViewSet, ProductTypeViewSet, ProductViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("brands", BrandViewSet)
router.register("product-types", ProductTypeViewSet)
router.register("products", ProductViewSet, basename="product")

urlpatterns = router.urls

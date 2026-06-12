from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from catalog.application.use_cases import ProductService
from catalog.infrastructure.models import BrandModel, CategoryModel, ProductModel, ProductTypeModel
from catalog.infrastructure.repositories import DjangoProductRepository
from catalog.presentation.serializers import BrandSerializer, CategorySerializer, ProductSerializer, ProductTypeSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = CategoryModel.objects.all()
    serializer_class = CategorySerializer


class BrandViewSet(viewsets.ModelViewSet):
    queryset = BrandModel.objects.all()
    serializer_class = BrandSerializer


class ProductTypeViewSet(viewsets.ModelViewSet):
    queryset = ProductTypeModel.objects.all()
    serializer_class = ProductTypeSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = ProductModel.objects.select_related("category", "brand", "product_type").prefetch_related("variants").all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "sku", "description"]
    ordering_fields = ["price", "created_at", "stock"]

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.query_params.get("category")
        brand_id = self.request.query_params.get("brand")
        brand_name = self.request.query_params.get("brand_name")
        product_type_id = self.request.query_params.get("product_type")
        product_type_name = self.request.query_params.get("product_type_name")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        is_active = self.request.query_params.get("is_active")

        if category_slug:
            queryset = queryset.filter(category_id=category_slug) if category_slug.isdigit() else queryset.filter(category__slug=category_slug)
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)
        if brand_name:
            queryset = queryset.filter(brand__name__icontains=brand_name)
        if product_type_id:
            queryset = queryset.filter(product_type_id=product_type_id)
        if product_type_name:
            queryset = queryset.filter(product_type__name__icontains=product_type_name)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = ProductService(DjangoProductRepository()).create_product(dict(serializer.validated_data))
        return Response(self.get_serializer(product).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        product = ProductService(DjangoProductRepository()).update_product(instance, dict(serializer.validated_data))
        return Response(self.get_serializer(product).data)

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        product = self.get_object()
        return Response(
            {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "stock": product.stock,
                "category": product.category.name,
                "attributes": product.attributes,
            }
        )

    @action(detail=True, methods=["post"])
    def reserve_stock(self, request, pk=None):
        """Reserve stock for checkout process"""
        quantity = request.data.get("quantity", 0)
        if quantity <= 0:
            return Response({"error": "Quantity must be positive"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = ProductService(DjangoProductRepository())
            product = service.reserve_stock(pk, quantity)
            return Response({"message": f"Reserved {quantity} units", "remaining_stock": product.stock})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def release_stock(self, request, pk=None):
        """Release reserved stock if order fails"""
        quantity = request.data.get("quantity", 0)
        if quantity <= 0:
            return Response({"error": "Quantity must be positive"}, status=status.HTTP_400_BAD_REQUEST)
        
        service = ProductService(DjangoProductRepository())
        product = service.release_stock(pk, quantity)
        return Response({"message": f"Released {quantity} units", "current_stock": product.stock})

    @action(detail=False, methods=["post"])
    def check_stock(self, request):
        """Check stock availability for multiple items"""
        items = request.data.get("items", [])
        if not items:
            return Response({"error": "Items list is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        service = ProductService(DjangoProductRepository())
        available, message = service.check_stock_availability(items)
        return Response({"available": available, "message": message})

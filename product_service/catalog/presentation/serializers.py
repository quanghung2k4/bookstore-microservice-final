from rest_framework import serializers

from catalog.infrastructure.models import BrandModel, CategoryModel, ProductModel, ProductTypeModel, VariantModel


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryModel
        fields = ["id", "name", "slug"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandModel
        fields = ["id", "name", "country"]


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTypeModel
        fields = ["id", "name", "description"]


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantModel
        fields = ["id", "name", "sku", "extra_price", "attributes"]
        read_only_fields = ["id"]


class ProductSerializer(serializers.ModelSerializer):
    variants = VariantSerializer(many=True, required=False)
    category_detail = CategorySerializer(source="category", read_only=True)
    brand_detail = BrandSerializer(source="brand", read_only=True)
    product_type_detail = ProductTypeSerializer(source="product_type", read_only=True)

    class Meta:
        model = ProductModel
        fields = [
            "id",
            "name",
            "sku",
            "description",
            "price",
            "stock",
            "image",
            "category",
            "brand",
            "product_type",
            "attributes",
            "is_active",
            "variants",
            "category_detail",
            "brand_detail",
            "product_type_detail",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

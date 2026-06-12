from django.contrib import admin
from django.utils.html import format_html

from catalog.infrastructure.models import BrandModel, CategoryModel, ProductModel, ProductTypeModel, VariantModel


@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")


@admin.register(BrandModel)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "country")


@admin.register(ProductTypeModel)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


class VariantInline(admin.TabularInline):
    model = VariantModel
    extra = 0


@admin.register(ProductModel)
class ProductAdmin(admin.ModelAdmin):
    def product_id(self, obj):
        return obj.sku

    product_id.short_description = "ID"
    product_id.admin_order_field = "sku"

    def image_preview(self, obj):
        if not obj.image:
            return ""
        return format_html('<img src="{}" style="height:48px;width:48px;object-fit:cover;border-radius:4px;" />', obj.image)

    image_preview.short_description = "Image"

    list_display = (
        "id",
        "image_preview",
        "name",
        "sku",
        "price",
        "stock",
        "category",
        "brand",
        "product_type",
        "is_active",
    )
    exclude = ("id",)

    list_filter = ("id","category", "brand", "product_type", "is_active")
    search_fields = ("name", "sku", "description")
    inlines = [VariantInline]

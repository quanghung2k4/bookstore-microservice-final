from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CategoryModel(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        db_table = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class BrandModel(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=120, blank=True)

    class Meta:
        db_table = "brands"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductTypeModel(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "product_types"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductModel(TimestampedModel):
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.URLField(max_length=500, blank=True, null=True)
    category = models.ForeignKey(CategoryModel, on_delete=models.PROTECT, related_name="products")
    brand = models.ForeignKey(BrandModel, on_delete=models.PROTECT, related_name="products")
    product_type = models.ForeignKey(ProductTypeModel, on_delete=models.PROTECT, related_name="products")
    attributes = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "products"
        ordering = ["id"]

    def __str__(self):
        return self.name
    # === CHÈN THÊM HÀM NÀY VÀO TRONG CLASS PRODUCTMODEL ===
    def save(self, *args, **kwargs):
        if not self.id:  # Chỉ tự sinh mã khi tạo mới sản phẩm
            # Tìm sản phẩm có mã P... lớn nhất hiện tại
            last_product = ProductModel.objects.filter(id__startswith='P').order_by('-id').first()
            if last_product:
                try:
                    last_number = int(last_product.id[1:])  # Tách lấy phần số, ví dụ '0005' -> 5
                    next_number = last_number + 1
                except ValueError:
                    next_number = 1
            else:
                next_number = 1
            
            self.id = f"P{next_number:04d}"  # Format thành P0001, P0002...
            
        super().save(*args, **kwargs)


class VariantModel(TimestampedModel):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=120)
    sku = models.CharField(max_length=64, unique=True)
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    attributes = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "variants"
        ordering = ["id"]

    def __str__(self):
        return f"{self.product.name} - {self.name}"
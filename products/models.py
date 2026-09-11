from django.db import models


class Product(models.Model):
    product_number = models.CharField(
        max_length=255,
        unique=True,
    )

    model_number = models.CharField(
        max_length=255,
        blank=True,
    )

    # Existing/source categorization
    product_category = models.CharField(
        max_length=255,
        blank=True,
    )

    product_sub_category = models.CharField(
        max_length=255,
        blank=True,
    )

    collection_name = models.CharField(
        max_length=255,
        blank=True,
    )

    color_collection = models.CharField(
        max_length=255,
        blank=True,
    )

    product_color = models.CharField(
        max_length=255,
        blank=True,
    )

    # Product information
    brand = models.CharField(
        max_length=255,
        blank=True,
    )

    product_name = models.CharField(
        max_length=500,
    )

    product_description = models.TextField(
        blank=True,
    )

    bullets = models.TextField(
        blank=True,
    )

    set_includes = models.TextField(
        blank=True,
    )

    materials = models.TextField(
        blank=True,
    )

    product_dimensions = models.CharField(
        max_length=500,
        blank=True,
    )

    product_weight = models.CharField(
        max_length=255,
        blank=True,
    )

    # Additional properties
    assembly_required = models.BooleanField(blank=True)
    is_set = models.BooleanField(blank=True)
    stackable = models.BooleanField(blank=True)

    country_of_origin = models.CharField(
        max_length=255,
        blank=True,
    )

    # Images
    image_urls = models.JSONField(
        default=list,
        blank=True,
    )

    product_url = models.URLField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "products"
        indexes = [
            models.Index(fields=["model_number"]),
            models.Index(fields=["product_category"]),
            models.Index(fields=["product_sub_category"]),
        ]

    def __str__(self):
        return self.product_name


class ProductBatch(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    name = models.CharField(
        max_length=255,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    total_products = models.PositiveIntegerField(
        default=0,
    )

    processed_products = models.PositiveIntegerField(
        default=0,
    )

    failed_products = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "product_batches"

    def __str__(self):
        return self.name
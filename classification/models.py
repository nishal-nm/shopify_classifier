from django.db import models

from products.models import Product
from taxonomy.models import (
    TaxonomyCategory,
    TaxonomyAttribute,
    TaxonomyAttributeValue,
)


class Classification(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("REVIEW", "Manual Review"),
        ("FAILED", "Failed"),
        ("APPROVED", "Approved"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="classifications",
    )

    category = models.ForeignKey(
        TaxonomyCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="classifications",
    )

    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    error = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "classifications"
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.product} - {self.category}"


class ClassificationAlternative(models.Model):
    classification = models.ForeignKey(
        Classification,
        on_delete=models.CASCADE,
        related_name="alternatives",
    )

    category = models.ForeignKey(
        TaxonomyCategory,
        on_delete=models.CASCADE,
    )

    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=4,
    )

    rank = models.PositiveIntegerField()

    class Meta:
        db_table = "classification_alternatives"
        ordering = ["rank"]


class ProductAttribute(models.Model):
    classification = models.ForeignKey(
        Classification,
        on_delete=models.CASCADE,
        related_name="attributes",
    )

    attribute = models.ForeignKey(
        TaxonomyAttribute,
        on_delete=models.CASCADE,
    )

    value = models.ForeignKey(
        TaxonomyAttributeValue,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=4,
    )

    class Meta:
        db_table = "product_attributes"
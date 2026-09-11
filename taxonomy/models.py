from django.db import models


class TaxonomyCategory(models.Model):
    external_id = models.CharField(
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=255)
    full_name = models.TextField(blank=True)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children",
    )

    level = models.PositiveIntegerField(default=0)
    is_leaf = models.BooleanField(default=False)
    is_root = models.BooleanField(default=False)

    class Meta:
        db_table = "taxonomy_categories"
        indexes = [
            models.Index(fields=["parent"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.full_name or self.name


class TaxonomyAttribute(models.Model):
    external_id = models.CharField(
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "taxonomy_attributes"

    def __str__(self):
        return self.name


class TaxonomyAttributeValue(models.Model):
    external_id = models.CharField(
        max_length=255,
        unique=True,
    )

    attribute = models.ForeignKey(
        TaxonomyAttribute,
        on_delete=models.CASCADE,
        related_name="values",
    )

    name = models.CharField(max_length=255)

    class Meta:
        db_table = "taxonomy_attribute_values"
        indexes = [
            models.Index(fields=["attribute"]),
        ]

    def __str__(self):
        return self.name


class CategoryAttribute(models.Model):
    category = models.ForeignKey(
        TaxonomyCategory,
        on_delete=models.CASCADE,
        related_name="attributes",
    )

    attribute = models.ForeignKey(
        TaxonomyAttribute,
        on_delete=models.CASCADE,
        related_name="categories",
    )

    class Meta:
        db_table = "category_attributes"
        constraints = [
            models.UniqueConstraint(
                fields=["category", "attribute"],
                name="unique_category_attribute",
            )
        ]

    def __str__(self):
        return f"{self.category} - {self.attribute}"
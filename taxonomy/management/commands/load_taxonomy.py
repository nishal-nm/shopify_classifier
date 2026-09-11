import gzip
import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from taxonomy.models import (
    TaxonomyCategory,
    TaxonomyAttribute,
    TaxonomyAttributeValue,
    CategoryAttribute,
)
from django.conf import settings

class Command(BaseCommand):
    help = "Loads Shopify taxonomy from data/taxonomy JSON files"

    def handle(self, *args, **options):
        base_dir = settings.BASE_DIR / "data" / "taxonomy"
        
        attributes_file = base_dir / "attributes.en.json.gz"
        categories_file = base_dir / "categories.en.json.gz"
        
        self.stdout.write(f"Loading attributes from {attributes_file}...")
        with gzip.open(attributes_file, "rt", encoding="utf-8") as f:
            attr_data = json.load(f)
        
        self.stdout.write("Saving attributes and values to DB...")
        with transaction.atomic():
            for attr in attr_data.get("attributes", []):
                attribute_obj, _ = TaxonomyAttribute.objects.update_or_create(
                    external_id=attr["id"],
                    defaults={"name": attr["name"]}
                )
                
                # Update/Create values for this attribute
                for val in attr.get("values", []):
                    TaxonomyAttributeValue.objects.update_or_create(
                        external_id=val["id"],
                        defaults={
                            "attribute": attribute_obj,
                            "name": val["name"]
                        }
                    )
        
        self.stdout.write(f"Loading categories from {categories_file}...")
        with gzip.open(categories_file, "rt", encoding="utf-8") as f:
            cat_data = json.load(f)
            
        self.stdout.write("Saving categories to DB...")
        
        # We need to process in order of level to ensure parent exists
        with transaction.atomic():
            all_cats = []
            for vertical in cat_data.get("verticals", []):
                all_cats.extend(vertical.get("categories", []))
                
            all_cats.sort(key=lambda x: x["level"])
            
            for cat_dict in all_cats:
                parent_obj = None
                if cat_dict.get("parent_id"):
                    parent_obj = TaxonomyCategory.objects.get(external_id=cat_dict["parent_id"])
                    
                cat_obj, _ = TaxonomyCategory.objects.update_or_create(
                    external_id=cat_dict["id"],
                    defaults={
                        "name": cat_dict["name"],
                        "full_name": cat_dict.get("full_name", ""),
                        "level": cat_dict["level"],
                        "parent": parent_obj,
                        "is_leaf": not bool(cat_dict.get("children", [])),
                        "is_root": parent_obj is None,
                    }
                )
                
                for attr_info in cat_dict.get("attributes", []):
                    attr_id = attr_info.get("id") if isinstance(attr_info, dict) else attr_info
                    try:
                        attr_obj = TaxonomyAttribute.objects.get(external_id=attr_id)
                        CategoryAttribute.objects.get_or_create(category=cat_obj, attribute=attr_obj)
                    except TaxonomyAttribute.DoesNotExist:
                        pass
        
        self.stdout.write(self.style.SUCCESS("Successfully loaded taxonomy data!"))

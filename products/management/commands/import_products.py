import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import Product, ProductBatch

class Command(BaseCommand):
    help = "Imports products from an Excel file into the database"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the Excel file")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        
        self.stdout.write(f"Reading file {file_path}...")
        df = pd.read_excel(file_path)
        
        # Replace NaN with empty string/None where appropriate
        df = df.replace({np.nan: None})
        
        batch = ProductBatch.objects.create(
            name=f"Import {file_path}",
            status="PENDING",
            total_products=len(df)
        )
        
        products_to_create = []
        for index, row in df.iterrows():
            # Gather image URLs
            image_urls = []
            for i in range(1, 21):
                col = f"Image {i}"
                if col in df.columns and row[col]:
                    image_urls.append(str(row[col]))
                    
            def get_bool(val):
                if val in ["Y", "y", "Yes", "yes", True, 1]:
                    return True
                return False

            product = Product(
                product_number=str(row.get("Product Number", "")),
                model_number=str(row.get("Model Number", "") or ""),
                product_category=str(row.get("Product Category", "") or ""),
                product_sub_category=str(row.get("Product Sub Category", "") or ""),
                collection_name=str(row.get("Collection Name", "") or ""),
                color_collection=str(row.get("Color Collection", "") or ""),
                product_color=str(row.get("Product Color", "") or ""),
                product_name=str(row.get("Product Name", "")),
                product_description=str(row.get("Product Description ", "") or ""), # Notice trailing space in col name
                bullets=str(row.get("Bullets", "") or ""),
                set_includes=str(row.get("Set Includes", "") or ""),
                materials=str(row.get("Materials", "") or ""),
                product_dimensions=str(row.get("Product Dimensions", "") or ""),
                product_weight=str(row.get("Product Weight", "") or ""),
                assembly_required=get_bool(row.get("Assembly Required")),
                is_set=get_bool(row.get("Is a Set")),
                stackable=get_bool(row.get("Stackable")),
                country_of_origin=str(row.get("Country Of Origin", "") or ""),
                image_urls=image_urls,
                product_url=str(row.get("Product URL", "") or "")
            )
            products_to_create.append(product)
            
        self.stdout.write(f"Saving {len(products_to_create)} products to database...")
        with transaction.atomic():
            # We could use bulk_create but product_number must be unique, so let's handle duplicates carefully
            Product.objects.all().delete() # Optional: Clear existing for this prototype
            Product.objects.bulk_create(products_to_create, ignore_conflicts=True)
            
        batch.status = "COMPLETED"
        batch.processed_products = len(products_to_create)
        batch.save()
        
        self.stdout.write(self.style.SUCCESS("Successfully imported products!"))

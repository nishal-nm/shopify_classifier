import time
from django.core.management.base import BaseCommand
from products.models import Product
from taxonomy.models import TaxonomyCategory, CategoryAttribute
from classification.models import Classification, ClassificationAlternative, ProductAttribute
from django.db import transaction

class Command(BaseCommand):
    help = "Classify pending products"

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=100, help="Batch size for processing")
        parser.add_argument("--limit", type=int, default=0, help="Limit total products to process (0 for unlimited)")

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        limit = options["limit"]
        
        products_query = Product.objects.exclude(
            classifications__status__in=["COMPLETED", "APPROVED"]
        )
        
        total_count = products_query.count()
        if limit > 0:
            total_count = min(total_count, limit)
            
        self.stdout.write(f"Found {total_count} products to classify.")
        
        processed = 0
        
        while True:
            chunk_size = batch_size
            if limit > 0:
                remaining = limit - processed
                if remaining <= 0:
                    break
                chunk_size = min(batch_size, remaining)
                
            batch_products = list(products_query[:chunk_size])
            if not batch_products:
                break
                
            for product in batch_products:
                try:
                    self.classify_product(product)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing {product.product_number}: {e}"))
                    
            processed += len(batch_products)
            self.stdout.write(f"Processed {processed}/{total_count}...")
            
    def classify_product(self, product):
        classification, _ = Classification.objects.update_or_create(
            product=product,
            defaults={"status": "PROCESSING"}
        )
        
        try:
            # Image handling validation
            if product.image_urls:
                for url in product.image_urls:
                    try:
                        if not isinstance(url, str) or not url.strip() or not url.startswith('http'):
                            raise ValueError(f"Invalid or malformed image URL: {url}")
                    except Exception as img_err:
                        err_msg = f"Image validation failed: {img_err}\n"
                        classification.error = (classification.error or "") + err_msg
                        classification.save()

            search_text = f"{product.product_name} {product.product_category} {product.product_sub_category} {product.product_description}".lower()
            words = set([w for w in search_text.split() if len(w) > 3])
            
            matching_categories = TaxonomyCategory.objects.filter(is_leaf=True)
            
            # Gather candidates
            candidate_qs = matching_categories.filter(name__icontains=product.product_category)[:10]
            if not candidate_qs:
                candidate_qs = matching_categories.filter(name__icontains=product.product_sub_category)[:10]
            if not candidate_qs and words:
                first_word = list(words)[0]
                candidate_qs = matching_categories.filter(name__icontains=first_word)[:5]
                
            candidates = []
            for cat in candidate_qs:
                cat_text = f"{cat.name} {cat.full_name}".lower()
                cat_words = set(cat_text.replace('>', ' ').split())
                overlap = words.intersection(cat_words)
                score = len(overlap) / max(len(words), 1) if words else 0
                # Give a baseline score if we found it via icontains
                score = min(score + 0.4, 0.99)
                candidates.append((cat, score))
                
            if not candidates:
                classification.status = "REVIEW"
                classification.error = (classification.error or "") + "No matching category found\n"
                classification.save()
                return
                
            candidates.sort(key=lambda x: x[1], reverse=True)
            best_cat, best_score = candidates[0]
            
            classification.category = best_cat
            classification.confidence = best_score
            classification.status = "COMPLETED" if best_score > 0.5 else "REVIEW"
            classification.save()
            
            # Save alternatives
            ClassificationAlternative.objects.filter(classification=classification).delete()
            for idx, (alt_cat, score) in enumerate(candidates[1:4]):
                ClassificationAlternative.objects.create(
                    classification=classification,
                    category=alt_cat,
                    confidence=score,
                    rank=idx + 1
                )
                
            # Attribute detection
            ProductAttribute.objects.filter(classification=classification).delete()
            product_full_text = f"{product.product_name} {product.product_description} {product.bullets} {product.materials}".lower()
            
            cat_attrs = CategoryAttribute.objects.filter(category=best_cat).select_related('attribute')
            for cat_attr in cat_attrs:
                attribute = cat_attr.attribute
                matched_val = None
                
                # Check taxonomy values
                for val in attribute.values.all():
                    if val.name.lower() in product_full_text:
                        matched_val = val
                        break
                        
                ProductAttribute.objects.create(
                    classification=classification,
                    attribute=attribute,
                    value=matched_val,
                    confidence=0.8 if matched_val else 0.1
                )
                
        except Exception as e:
            classification.status = "FAILED"
            classification.error = (classification.error or "") + f"Exception: {str(e)}\n"
            classification.save()
            raise e

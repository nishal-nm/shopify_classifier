import time
from django.core.management.base import BaseCommand
from products.models import Product
from taxonomy.models import TaxonomyCategory
from classification.models import Classification, ClassificationAlternative
from django.db import transaction

class Command(BaseCommand):
    help = "Classify pending products"

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=100, help="Batch size for processing")
        parser.add_argument("--limit", type=int, default=0, help="Limit total products to process (0 for unlimited)")

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        limit = options["limit"]
        
        # Get products that haven't been successfully classified or approved
        # This allows resuming processing
        products_query = Product.objects.exclude(
            classifications__status__in=["COMPLETED", "APPROVED"]
        )
        
        if limit > 0:
            products_query = products_query[:limit]
            
        total_count = products_query.count()
        self.stdout.write(f"Found {total_count} products to classify.")
        
        processed = 0
        
        for i in range(0, total_count, batch_size):
            batch_products = products_query[i:i+batch_size]
            
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
            # Simulate a 2 second API call if we were using AI
            # time.sleep(2)  # Commented out for fast execution in demo
            
            # Simple heuristic classification based on title/category keywords
            search_text = f"{product.product_name} {product.product_category} {product.product_sub_category}".lower()
            
            # Very basic search logic
            # In a real scenario, this would call an LLM with product text and image URLs
            matching_categories = TaxonomyCategory.objects.filter(is_leaf=True)
            
            best_match = None
            best_score = 0
            
            # Just grab some categories to simulate matches
            # Let's search if any words match
            words = set([w for w in search_text.split() if len(w) > 3])
            
            candidates = []
            for cat in matching_categories.filter(name__icontains=product.product_category)[:10]:
                candidates.append((cat, 0.8))
            
            if not candidates:
                for cat in matching_categories.filter(name__icontains=product.product_sub_category)[:10]:
                    candidates.append((cat, 0.6))
                    
            if not candidates and words:
                # fallback
                first_word = list(words)[0]
                for cat in matching_categories.filter(name__icontains=first_word)[:5]:
                    candidates.append((cat, 0.4))
                    
            if not candidates:
                # If still nothing, assign a default or mark for review
                classification.status = "REVIEW"
                classification.error = "No matching category found"
                classification.save()
                return
                
            # Sort candidates by score
            candidates.sort(key=lambda x: x[1], reverse=True)
            best_cat, best_score = candidates[0]
            
            classification.category = best_cat
            classification.confidence = best_score
            classification.status = "COMPLETED" if best_score > 0.7 else "REVIEW"
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
                
        except Exception as e:
            classification.status = "FAILED"
            classification.error = str(e)
            classification.save()
            raise e

# Python Developer Online Test - Candidate Questions & Answers

## 1. What approach would you use to automatically identify the Shopify category, attributes, and attribute values? Explain your approach and why you selected it.
**Approach**: I would use a hybrid approach combining heuristic text search and a Large Language Model (LLM). First, I would match explicit category keywords from the product's internal `Product Category` and `Product Sub Category` with Shopify taxonomy categories. If an exact match is found, we can assign it instantly. For items that don't match or have ambiguous titles/descriptions, I would pass the product details (Title, Description, Brand, Product Type) to an LLM (like OpenAI's GPT-4o-mini or Gemini 1.5 Flash). We can prompt the LLM to output the closest matching category ID from the taxonomy.
**Why**: Heuristics solve the majority of easy cases quickly and cheaply. LLMs excel at understanding context and semantics (e.g. mapping "Sofa" to "Furniture > Sofas") even with missing or unstructured data.

## 2. How would you handle a product that has a title but no description and no image?
The LLM or classification logic relies on the title, product category, and sub-category. Often, a product title like "Empress Bonded Leather Sofa" contains enough semantic information (e.g. "Sofa") to identify the category. If the information is too sparse, the system will mark the product's classification status as `REVIEW` with a low confidence score, flagging it for manual approval by a human.

## 3. How would you use product images to improve classification when an image is available?
When using an LLM that supports vision (like GPT-4o or Gemini 1.5 Pro), product images can be included in the prompt. The visual context allows the model to correctly identify products where the text description is vague or misleading, ensuring a much higher confidence classification.

## 4. How would you design the application to process 10,000+ products efficiently? Explain your approach for batch/background processing.
I would implement background task processing using **Celery** and a message broker like **Redis** or **RabbitMQ**. 
- Products are broken down into manageable chunks (e.g., batches of 100).
- Celery worker nodes pull these chunks from the queue, allowing concurrent processing.
- Database transactions would be handled efficiently using `bulk_create` and `bulk_update` to reduce database overhead.
- This decoupling ensures the main web application remains responsive.

## 5. How would you store the Shopify taxonomy and its category hierarchy in the database?
I would use a relational database model with a self-referential foreign key for categories.
```python
class TaxonomyCategory(models.Model):
    external_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, related_name='children')
    level = models.PositiveIntegerField(default=0)
    is_leaf = models.BooleanField(default=False)
```
This enables querying full category paths and finding leaf nodes. For attributes, a many-to-many relationship mapping categories to attributes works best.

## 6. How would you calculate or determine the confidence score for a classification?
If using an LLM, the model can be prompted to return a confidence score (0.0 to 1.0) along with its classification. 
For heuristic search, the score can be calculated based on the matching criteria:
- Exact match on category + sub-category: `0.9 - 1.0`
- Match on title keywords: `0.6 - 0.8`
- Fuzzy/partial match: `0.3 - 0.5`

## 7. What would you do when the system cannot confidently identify a single category?
The system would store the top N most likely categories as `ClassificationAlternative` records in the database. The classification status would be set to `REVIEW`. In the UI, the admin will see these alternative suggestions and can quickly approve the correct one.

## 8. How would you handle a broken or inaccessible product image without stopping the complete batch?
The background task would be wrapped in a `try...except` block when downloading or passing the image to the LLM. If an image fails to load (e.g. 404 error, timeout), the exception is caught, logged as a warning, and the system gracefully falls back to classifying the product using its text data only. The overall batch loop continues seamlessly.

## 9. How would you design the API and database structure for this application?
**Database**:
- `Product`: Stores imported product data.
- `TaxonomyCategory` / `TaxonomyAttribute`: Stores the Shopify taxonomy.
- `Classification`: Links a Product to a TaxonomyCategory. Fields: `confidence`, `status` (PENDING, PROCESSING, COMPLETED, REVIEW, FAILED), `error`.
- `ClassificationAlternative`: Stores fallback categories.

**API (Django REST Framework)**:
- `GET /api/classifications/` - List classifications (can filter by status e.g. `?status=REVIEW`).
- `PATCH /api/classifications/{id}/` - Update category manually.
- `POST /api/classifications/{id}/approve/` - Mark as approved.

## 10. If the application needs to process 10,000 products and each external AI/API request takes approximately 2 seconds, how would you optimize the processing time?
10,000 products * 2s = ~5.5 hours sequentially. 
To optimize:
- **Concurrency**: Use Celery with multiple worker processes, or `asyncio` (`aiohttp`) to make concurrent API requests (e.g., 50 parallel requests). This can reduce the time from 5.5 hours to ~7 minutes.
- **Batching APIs**: If the LLM API supports batch requests, group multiple products into a single API call.
- **Caching**: Cache identical or highly similar product classifications to avoid redundant API calls.

## 11. How would you design the system so that if processing fails after 6,000 products, it can resume from the remaining products instead of starting again?
The batch script or Celery task queries the database for products that have `status='PENDING'` or `status='FAILED'`. As each product is successfully processed, its status is updated to `COMPLETED` or `REVIEW` and saved to the database. If the process crashes at 6,000, restarting the task will automatically fetch the remaining 4,000 `PENDING` products.

## 12. What technologies/frameworks would you choose for this application, and why?
- **Backend**: Python & Django. Excellent ORM, built-in admin panel, and rapid development capabilities.
- **Database**: MySQL/MariaDB for structured data storage, optimized index querying.
- **API**: Django REST Framework.
- **Task Queue**: Celery + Redis for reliable background processing.
- **Frontend**: React (or simple Django Templates/Bootstrap for a prototype) to quickly build a responsive UI for review.

## 13. Provide a high-level architecture/design for the complete application.
1. **User Interface**: React SPA or Django Views for uploading files and reviewing classifications.
2. **API Layer**: DRF endpoints handling file uploads, triggering batch jobs, and fetching paginated results.
3. **Task Queue**: Celery workers picking up tasks to parse Excel, load taxonomy, and process classification.
4. **Classification Engine**: A module that first attempts heuristic matching, then prepares a prompt with text + images and calls the LLM API asynchronously.
5. **Data Layer**: MariaDB storing Products, Taxonomy, and Classifications.

## 14. Provide a realistic development effort estimation in hours, including a task-wise breakdown for developing this as a production-ready application.
- **Database & Models setup**: 4 hours
- **Taxonomy Import scripts**: 4 hours
- **Product Import & Data Cleaning**: 4 hours
- **Classification Engine (Heuristics + LLM integration)**: 12 hours
- **Background Jobs (Celery/Redis setup)**: 6 hours
- **API endpoints**: 4 hours
- **Frontend Dashboard & Review UI**: 12 hours
- **Testing & Error Handling**: 8 hours
- **Deployment & CI/CD**: 6 hours
**Total**: ~60 hours.

## 15. Practical Task: Develop a working prototype...
*(See implemented codebase in this project.)*

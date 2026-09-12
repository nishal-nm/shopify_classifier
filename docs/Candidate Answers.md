1. **What approach would you use to automatically identify the Shopify category, attributes, and attribute values? Explain your approach and why you selected it.**\
   I implemented a keyword-based set intersection algorithm. The system loads all Shopify leaf categories into memory, tokenizes their names into keywords, and performs a mathematical intersection against a massive string built from the product's title, description, brand, and type. I chose this approach over paid third-party AI APIs because it is incredibly fast, deterministic, doesn't rely on internet latency, and allows for manual heuristic tuning (like giving score boosts for exact substring matches).

2. **How would you handle a product that has a title but no description and no image?**\
   Our scoring engine treats all available text fields as a single pool of searchable words. If the description and image are missing, the algorithm seamlessly operates using just the words from the product title and brand, gracefully falling back without throwing any errors.

3. **How would you use product images to improve classification when an image is available?**\
   Since processing raw images through computer vision is heavy, I extract semantic value from the image URL itself. For example, a URL like `.../Mens-Running-Shoes-123.jpg` is parsed and cleaned using regex to extract keywords like "Mens Running Shoes". These keywords are directly injected into the text-matching algorithm to heavily boost accuracy.

4. **How would you design the application to process 10,000+ products efficiently? Explain your approach for batch/background processing.**\
   I utilized a decoupled asynchronous approach. When an Excel file is uploaded, an API endpoint uses Pandas to synchronously read the file and execute a high-speed database `bulk_create`. It immediately returns a success response and spawns a background Python daemon thread. This background thread processes the classifications in database chunks (e.g., 100 products at a time) to prevent memory bloat, while the frontend continuously polls a lightweight status API to show a live progress bar.

5. **How would you store the Shopify taxonomy and its category hierarchy in the database?**\
   I used a normalized relational database design via Django Models. A `TaxonomyCategory` model handles the hierarchy using a self-referential `parent` ForeignKey. Attributes and their allowed values are stored in `TaxonomyAttribute` and `TaxonomyAttributeValue` models, which are linked to categories through a many-to-many `CategoryAttribute` mapping table.

6. **How would you calculate or determine the confidence score for a classification?**\
   I calculate it using a tiered mathematical heuristic. First, I award a base score (e.g., +30% confidence) for every overlapping keyword between the product and the category name. Then, I apply a tiny mathematical penalty based on the length of the product description so that highly precise matches win ties. Finally, I apply massive percentage boosts (e.g., +40%) if the exact category name appears in the original "Product Type" column.

7. **What would you do when the system cannot confidently identify a single category?**\
   If a product's highest confidence score falls below a set threshold (50%), the system assigns the product a `REVIEW` status rather than `COMPLETED`. Additionally, the system captures the 2nd and 3rd place runner-up categories and saves them into a `ClassificationAlternative` table. The frontend UI then displays these alternatives in a dropdown, allowing a human administrator to quickly select the correct category.

8. **How would you handle a broken or inaccessible product image without stopping the complete batch?**\
   Every individual product classification is wrapped in a dedicated `try/except` block inside the chunk loop. If an image parsing step or database commit throws an exception, the system catches it, flags that specific product's status as `FAILED`, saves the error trace, and immediately moves on to the next product. A single bad row will never crash the batch.

9. **How would you design the API and database structure for this application?**\
   **Database:** Separated into `Product` (raw imported data), `TaxonomyCategory` (the Shopify master list), and `Classification` (the mapping between the two).\
   **API:** Designed as RESTful endpoints using Django REST Framework. Includes `/api/upload/` for file parsing, `/api/status/` for live background tracking, and a paginated `/api/classifications/` viewset that serves the data in chunks of 50 to prevent frontend browser freezing.

10. **If the application needs to process 10,000 products and each external AI/API request takes approximately 2 seconds, how would you optimize the processing time?**\
    Instead of processing them sequentially (which would take 20,000 seconds / ~5.5 hours), I would integrate a message broker like Redis and a task queue like Celery. By spinning up a pool of 20 to 50 concurrent worker threads, the system can fire off API requests in parallel, slashing the processing time down to a matter of minutes.

11. **How would you design the system so that if processing fails after 6,000 products, it can resume from the remaining products instead of starting again?**\
    Our background script is fully stateless and database-driven. The core query asks the database for `Product.objects.exclude(classifications__status__in=["COMPLETED", "APPROVED", "REVIEW", "FAILED"])`. Because it strictly queries for rows that have absolutely no status, restarting the server or script automatically ignores the first 6,000 processed items and seamlessly resumes processing from product 6,001.

12. **What technologies/frameworks would you choose for this application, and why?**

- **Backend:** Python + Django + Django REST Framework. Chosen for its robust built-in ORM, excellent management commands (for cron/background tasks), and blazing-fast API scaffolding.
- **Frontend:** Vanilla HTML + JavaScript + Tailwind CSS. Chosen because the UI requirements (tables, progress bars) can be built incredibly cleanly and professionally without the heavy overhead and build-steps of React or Vue.
- **Database:** SQLite (easily upgradable to PostgreSQL for production) due to its zero-configuration local setup.

13. **Provide a high-level architecture/design for the complete application.**

- **Client Layer:** A responsive Tailwind UI that posts files and polls for JSON status updates.
- **API Layer:** Django views that securely handle file uploads, trigger background tasks, and serve paginated data.
- **Worker Layer:** Python threading executing the classification engine in memory-safe chunks.
- **Data Layer:** A relational SQL database enforcing strict foreign keys between raw products, calculated classifications, and the Shopify taxonomy tree.

14. **Provide a realistic development effort estimation in hours, including a task-wise breakdown for developing this as a production-ready application. Mention your assumptions and major dependencies/risks.**\

- **Database Architecture & Models:** 4 hours
- **Shopify Taxonomy Parsing/Loading Script:** 3 hours
- **Core Classification Engine & Heuristics:** 6 hours
- **REST APIs & Background Processing:** 4 hours
- **Frontend UI (Skeleton loaders, pagination, status bars):** 6 hours
- **Testing, Error Handling & Refactoring:** 4 hours
- **Total:** ~27 hours.
- _Assumptions:_ The provided Shopify JSON taxonomy is well-formed.
- _Risks:_ Highly generic product titles with massive descriptions could dilute keyword matching, requiring ongoing fine-tuning of the heuristic math.

15. **Practical Task: Develop a working prototype that demonstrates the above functionality using the sample product list provided.**\
    Completed. The system accurately imports products, visually tracks background processing progress, applies mathematical heuristics to match against the Shopify taxonomy, and provides a polished UI for reviewing alternatives and approving results.

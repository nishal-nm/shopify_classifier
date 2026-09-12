# Shopify Product Taxonomy Classifier

A lightweight, high-performance Python web application designed to automatically import large product catalogs (10,000+ items) and accurately map them to the official Shopify product taxonomy using a smart heuristic classification engine.

## Features
- **Fast Heuristic Classification:** Uses memory-optimized token intersection and intelligent penalty math to map generic products to specific Shopify leaf categories.
- **Asynchronous Background Processing:** Upload massive Excel files without freezing the browser. The system delegates processing to a background daemon thread while streaming live progress.
- **Sleek Tailwind UI:** A clean, modern dashboard with skeleton loading, pagination, and real-time live progress bars.
- **Automated Human Review:** Products with confidence scores below 50% are automatically flagged for manual review with the top 3 alternative candidate categories pre-calculated.
- **Fault-Tolerant Engine:** Gracefully handles missing descriptions, broken image URLs, and incomplete data rows without interrupting the bulk process.

---

## Quick Start Setup

### 1. Environment & Dependencies
Create a virtual environment and install the required packages:
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database Initialization
By default, the app uses SQLite for zero-configuration setup, but you can configure MySQL/MariaDB in `config/settings.py` if preferred. Run the migrations to build the schema:
```bash
python manage.py migrate
```

### 3. Load Shopify Taxonomy
*Important:* You must seed the database with the official Shopify categories and attributes before processing products.
```bash
python manage.py load_taxonomy
```

### 4. Launch the Application
Start the Django development server:
```bash
python manage.py runserver
```

Navigate to **`http://127.0.0.1:8000/`** to open the Classification Dashboard.

---

## Usage

### Web Dashboard (Recommended)
1. Open the dashboard at `http://127.0.0.1:8000/`.
2. Click **Import Products** and upload your Excel catalog (`.xlsx`).
3. The system will synchronously map the file into the database and seamlessly transition into an animated live progress bar as the background classification thread runs.
4. Once completed, review your products using the paginated table. Approved classifications highlight in green, while low-confidence matches highlight in amber for manual review.

### Terminal Commands (For CLI usage)
If you prefer to bypass the web UI, you can trigger the engine directly via the terminal:

**To import products from an Excel file:**
```bash
python manage.py import_products "data\Product_List.xlsx"
```

**To run the classification engine on unclassified products:**
```bash
python manage.py classify_products
```

**To clear bad classifications and start over:**
```bash
python manage.py shell -c "from classification.models import Classification; Classification.objects.all().delete()"
```

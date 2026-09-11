# Shopify Classifier

This project provides a system to import products from an Excel list and automatically map them to the Shopify taxonomy categories and attributes using heuristic matching.

## Setup Instructions

1. **Virtual Environment**: Create and activate a Python virtual environment.
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. **Install Requirements**: Install dependencies from `requirements.txt`.
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Configuration**: Configure a MySQL/MariaDB database in `config/settings.py` (default: database `shopify_classifier`, user `root`, password `root`).

4. **Run Migrations**: Create necessary tables in the database.
   ```bash
   python manage.py migrate
   ```

5. **Load Shopify Taxonomy**: Load categories and attributes from JSON into the database.
   ```bash
   python manage.py load_taxonomy
   ```

6. **Import Products**: Import the Excel list of products.
   ```bash
   python manage.py import_products "docs\Product List.xlsx"
   ```

7. **Classify Products**: Run the classification engine.
   ```bash
   python manage.py classify_products
   ```

8. **Start Server**: Run the Django dev server to access the API or Admin UI.
   ```bash
   python manage.py runserver
   ```
   - API endpoint: `http://127.0.0.1:8000/api/classifications/`
   - Admin panel: `http://127.0.0.1:8000/admin/`

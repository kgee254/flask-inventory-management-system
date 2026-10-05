# Flask Inventory Management System

A small Flask API and interactive command-line client for managing inventory. The API stores items in the in-memory `app.data.inventory` list and can look up or import product information from OpenFoodFacts.

> **Storage note:** Inventory is held in memory. Items added during a run are lost when the process stops. Use a database for persistent or production use.

## Features

- List, retrieve, create, update, and delete inventory items.
- Look up a product by barcode through OpenFoodFacts.
- Import an OpenFoodFacts product into the local inventory.
- Use the API directly or through the interactive CLI.
- Test routes and API integrations with pytest and mocked HTTP requests.

## Project structure

```text
.
├── app/
│   ├── __init__.py          # Flask app factory and blueprint registration
│   ├── data.py              # In-memory inventory data
│   ├── routes.py            # Inventory and OpenFoodFacts API routes
│   └── openfoodfacts.py     # OpenFoodFacts HTTP integration
├── cli.py                   # Interactive command-line client
├── tests/
│   ├── test_routes.py
│   ├── test_openfoodfacts.py
│   └── test_cli.py
└── README.md
```

Your repository may include additional files such as a virtual environment or dependency list.

## Requirements

- Python 3.10 or later
- pip
- Internet access for live OpenFoodFacts lookups (not needed for mocked tests)

## Installation and setup

From the project directory, create and activate a virtual environment.

**Linux/macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the application and test dependencies:

```bash
python -m pip install Flask requests pytest
```

If the project has a `requirements.txt`, install from it instead:

```bash
python -m pip install -r requirements.txt
```

Start the Flask development server from the project root:

```bash
flask --app app run --debug
```

If the package does not expose a Flask app in a way the Flask command can discover, use the project's app entry point (for example, `python run.py`) if present. The CLI client defaults to `http://127.0.0.1:5000`; keep the API on that address and port unless `cli.py`'s `BASE_URL` is changed.

In a second terminal, activate the same virtual environment and run:

```bash
python cli.py
```

## API

Base URL: `http://127.0.0.1:5000`

All routes return JSON. For POST and PATCH requests, send a JSON body with the `Content-Type: application/json` header.

### Inventory routes

| Method | Path | Description | Success |
|---|---|---|---|
| GET | `/inventory` | Return all inventory items. | `200 OK` |
| GET | `/inventory/<item_id>` | Return the item with the integer ID. | `200 OK` |
| POST | `/inventory` | Create an inventory item. Requires all fields below. | `201 Created` |
| PATCH | `/inventory/<item_id>` | Update supplied fields on an existing item. | `200 OK` |
| DELETE | `/inventory/<item_id>` | Delete an existing item. | `200 OK` |

A missing inventory item returns `404` with an error message. POST requires these fields:

- `barcode`
- `product_name`
- `brand`
- `category`
- `ingredients_text`
- `price`
- `stock`

If required fields are missing, the API returns `400` with an error and a `fields` list.

Example create request:

```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "3017624010701",
    "product_name": "Hazelnut spread",
    "brand": "Example Brand",
    "category": "Spreads",
    "ingredients_text": "Sugar, palm oil, hazelnuts, cocoa",
    "price": 5.99,
    "stock": 12
  }'
```

Example partial update:

```bash
curl -X PATCH http://127.0.0.1:5000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 6.25, "stock": 9}'
```

Example delete:

```bash
curl -X DELETE http://127.0.0.1:5000/inventory/1
```

### OpenFoodFacts routes

| Method | Path | Description | Success |
|---|---|---|---|
| GET | `/products/external/<barcode>` | Fetch product data from OpenFoodFacts for the barcode. | `200 OK` |
| POST | `/products/import/<barcode>` | Look up a barcode and add the product to inventory. | `201 Created` |

The lookup route returns `404` if the product cannot be found or OpenFoodFacts is unavailable. The import route also handles a barcode that is already in inventory; check the returned status and JSON response for the outcome.

Example lookup:

```bash
curl http://127.0.0.1:5000/products/external/3017624010701
```

Example import:

```bash
curl -X POST http://127.0.0.1:5000/products/import/3017624010701
```

OpenFoodFacts data is retrieved from its v3 product API. The integration sends a `User-Agent` and uses a 10-second request timeout. Network request errors are handled as an unavailable/not-found result.

## Command-line client

Run `python cli.py` while the API server is running. The menu provides these actions:

1. View all inventory.
2. View one inventory item by ID.
3. Add an item by entering its details.
4. Update an item by ID.
5. Delete an item by ID.
6. Search OpenFoodFacts by barcode.
7. Import a product from OpenFoodFacts by barcode.
8. Exit.

For example, to add an item, choose **3** and enter its barcode, product name, brand, category, ingredients, price, and stock when prompted. To search an external product, choose **6** and enter a barcode. To import it into local inventory, choose **7**. Numeric prompts repeat when the input cannot be parsed as an integer or decimal number.

The client sends requests to `http://127.0.0.1:5000` (the `BASE_URL` in `cli.py`). Start or configure the API accordingly.

## Testing

Install pytest if it is not already available, activate the virtual environment, then run the full suite from the project root:

```bash
python -m pytest -v
```

Run an individual module when working on one area:

```bash
python -m pytest tests/test_routes.py -v
python -m pytest tests/test_openfoodfacts.py -v
python -m pytest tests/test_cli.py -v
```

The route tests use Flask's test client and restore the in-memory inventory after each test. Tests for the OpenFoodFacts integration and CLI should mock HTTP calls with `unittest.mock` (`Mock` and `patch`). This keeps unit tests repeatable, avoids network dependency, and allows success and error responses to be simulated. Patch the object where the code under test looks it up; for example, patch `app.openfoodfacts.requests.get` when testing `app.openfoodfacts`.

A mock response can supply JSON and simulate HTTP errors:

```python
from unittest.mock import Mock, patch

fake_response = Mock()
fake_response.json.return_value = {"product": {"product_name": "Example"}}

with patch("app.openfoodfacts.requests.get", return_value=fake_response):
    ...
```

Do not make tests depend on a live Flask server or live OpenFoodFacts service. For CLI tests, mock `cli.requests.get`, `cli.requests.post`, `cli.requests.patch`, and `cli.requests.delete` as needed, and provide input with pytest's `monkeypatch` or `unittest.mock.patch`.

## Validate manually with Flask and Postman

1. Start the Flask development server with debug mode enabled as described above.
2. Confirm the server reports that it is listening at `http://127.0.0.1:5000`.
3. In Postman, send `GET http://127.0.0.1:5000/inventory`; expect a JSON list.
4. Send the example POST request as a raw JSON body and verify the created item and generated ID.
5. Try GET, PATCH, and DELETE for that item's ID.
6. Try an unknown ID and confirm the API returns a 404.
7. Test the OpenFoodFacts lookup and import routes with a valid barcode while internet access is available.
8. Stop the development server when finished.

Debug mode is intended for local development only. Do not expose the debug server to an untrusted network.

## Maintainability and code comments

- Keep route handlers focused on HTTP validation and responses; keep external API communication in `openfoodfacts.py`.
- Keep inventory storage separate from route logic. For long-term use, replace the in-memory list with a database and add migrations.
- Add short comments where they explain a non-obvious decision or constraint. Prefer descriptive function and variable names over comments that repeat the code.
- Keep API field names and route paths consistent between `routes.py`, `cli.py`, tests, and this README.
- Add tests for new success cases, validation errors, not-found cases, and external-service failures.
- Handle network timeouts and service errors explicitly; avoid embedding credentials or environment-specific secrets in source code.
- If the server URL, API paths, required item fields, or response behavior change, update this documentation and the CLI tests together.


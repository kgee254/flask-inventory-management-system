import pytest

from app import create_app
from app.data import inventory


@pytest.fixture
def app():
    app = create_app()

    app.config.update({
        "TESTING": True
    })

    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_inventory():
    original_inventory = inventory.copy()

    yield

    inventory.clear()
    inventory.extend(original_inventory)


def test_get_inventory(client):
    response = client.get("/inventory")

    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_get_inventory_item(client):
    response = client.get("/inventory/1")

    assert response.status_code == 200
    assert response.json["id"] == 1


def test_get_inventory_item_not_found(client):
    response = client.get("/inventory/9999")

    assert response.status_code == 404
    assert response.json["error"] == "Inventory item not found"


def test_create_inventory_item(client):
    new_item = {
        "barcode": "123456789",
        "product_name": "Test Product",
        "brand": "Test Brand",
        "category": "Test Category",
        "ingredients_text": "Test ingredients",
        "price": 200,
        "stock": 10
    }

    response = client.post(
        "/inventory",
        json=new_item
    )

    assert response.status_code == 201
    assert response.json["product_name"] == "Test Product"
    assert response.json["price"] == 200
    assert response.json["stock"] == 10


def test_create_inventory_item_missing_fields(client):
    incomplete_item = {
        "barcode": "123456789",
        "product_name": "Test Product"
    }

    response = client.post(
        "/inventory",
        json=incomplete_item
    )

    assert response.status_code == 400
    assert response.json["error"] == "Missing required fields"

    assert "brand" in response.json["fields"]
    assert "category" in response.json["fields"]
    assert "price" in response.json["fields"]


def test_update_inventory_item(client):
    update_data = {
        "price": 750,
        "stock": 50
    }

    response = client.patch(
        "/inventory/1",
        json=update_data
    )

    assert response.status_code == 200
    assert response.json["id"] == 1
    assert response.json["price"] == 750
    assert response.json["stock"] == 50


def test_update_inventory_item_not_found(client):
    update_data = {
        "price": 750
    }

    response = client.patch(
        "/inventory/9999",
        json=update_data
    )

    assert response.status_code == 404
    assert response.json["error"] == "Inventory item not found"


def test_delete_inventory_item(client):
    response = client.delete("/inventory/1")

    assert response.status_code == 200
    assert response.json["message"] == (
        "Inventory item deleted successfully"
    )

    # Confirm that the item is actually gone
    get_response = client.get("/inventory/1")

    assert get_response.status_code == 404


def test_delete_inventory_item_not_found(client):
    response = client.delete("/inventory/9999")

    assert response.status_code == 404
    assert response.json["error"] == "Inventory item not found"


def test_get_external_product(client, monkeypatch):
    fake_product = {
        "code": "123456789",
        "product_name": "Test Product",
        "brands": "Test Brand"
    }

    def mock_get_product(barcode):
        return fake_product

    monkeypatch.setattr(
        "app.routes.get_product_by_barcode",
        mock_get_product
    )

    response = client.get(
        "/products/external/123456789"
    )

    assert response.status_code == 200
    assert response.json["product_name"] == "Test Product"
    assert response.json["brands"] == "Test Brand"


def test_get_external_product_not_found(client, monkeypatch):
    def mock_get_product(barcode):
        return None

    monkeypatch.setattr(
        "app.routes.get_product_by_barcode",
        mock_get_product
    )

    response = client.get(
        "/products/external/999999999"
    )

    assert response.status_code == 404
    assert response.json["error"] == (
        "Product not found or OpenFoodFacts unavailable"
    )


def test_import_external_product(client, monkeypatch):
    fake_product = {
        "code": "987654321",
        "product_name": "Imported Product",
        "brands": "Imported Brand",
        "categories": "Imported Category",
        "ingredients_text": "Imported ingredients"
    }

    def mock_get_product(barcode):
        return fake_product

    monkeypatch.setattr(
        "app.routes.get_product_by_barcode",
        mock_get_product
    )

    response = client.post(
        "/inventory/import/987654321"
    )

    assert response.status_code == 201
    assert response.json["barcode"] == "987654321"
    assert response.json["product_name"] == "Imported Product"
    assert response.json["brand"] == "Imported Brand"
    assert response.json["category"] == "Imported Category"
    assert response.json["stock"] == 0


def test_import_external_product_already_exists(client):
    response = client.post(
        "/inventory/import/3017624010701"
    )

    assert response.status_code == 409
    assert response.json["error"] == (
        "Product already exists in inventory"
    )


def test_import_external_product_not_found(client, monkeypatch):
    def mock_get_product(barcode):
        return None

    monkeypatch.setattr(
        "app.routes.get_product_by_barcode",
        mock_get_product
    )

    response = client.post(
        "/inventory/import/999999999"
    )

    assert response.status_code == 404
    assert response.json["error"] == (
        "Product not found or OpenFoodFacts unavailable"
    )
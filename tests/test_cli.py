from unittest.mock import Mock, patch

import requests

from cli import (
    add_inventory_item,
    delete_inventory_item,
    display_inventory,
    get_float,
    get_integer,
    import_openfoodfacts_product,
    main,
    search_openfoodfacts,
    update_inventory_item,
    view_inventory,
    view_inventory_item,
)


def test_display_inventory(capsys):
    items = [
        {
            "id": 1,
            "barcode": "123456789",
            "product_name": "Test Product",
            "brand": "Test Brand",
            "category": "Test Category",
            "ingredients_text": "Test ingredients",
            "price": 200,
            "stock": 10
        }
    ]

    display_inventory(items)

    output = capsys.readouterr().out

    assert "INVENTORY" in output
    assert "Test Product" in output
    assert "Test Brand" in output
    assert "200" in output
    assert "10" in output


def test_display_inventory_empty(capsys):
    display_inventory([])

    output = capsys.readouterr().out

    assert "Inventory is empty." in output


def test_get_integer():
    with patch(
        "builtins.input",
        side_effect=["abc", "10"]
    ):
        result = get_integer("Enter number: ")

    assert result == 10


def test_get_float():
    with patch(
        "builtins.input",
        side_effect=["abc", "25.50"]
    ):
        result = get_float("Enter price: ")

    assert result == 25.50


def test_view_inventory(capsys):
    fake_response = Mock()

    fake_response.json.return_value = [
        {
            "id": 1,
            "product_name": "Test Product",
            "brand": "Test Brand",
            "price": 200,
            "stock": 10
        }
    ]

    with patch("cli.requests.get") as mock_get:
        mock_get.return_value = fake_response

        view_inventory()

    mock_get.assert_called_once_with(
        "http://127.0.0.1:5000/inventory",
        timeout=10
    )

    output = capsys.readouterr().out

    assert "Test Product" in output


def test_view_inventory_request_error(capsys):
    with patch("cli.requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException(
            "Connection error"
        )

        view_inventory()

    output = capsys.readouterr().out

    assert "Unable to connect to the Flask API." in output


def test_view_inventory_item(capsys):
    fake_response = Mock()

    fake_response.status_code = 200

    fake_response.json.return_value = {
        "id": 1,
        "product_name": "Test Product",
        "brand": "Test Brand",
        "price": 200,
        "stock": 10
    }

    with patch("cli.requests.get") as mock_get:
        mock_get.return_value = fake_response

        with patch(
            "builtins.input",
            return_value="1"
        ):
            view_inventory_item()

    mock_get.assert_called_once_with(
        "http://127.0.0.1:5000/inventory/1",
        timeout=10
    )

    output = capsys.readouterr().out

    assert "Test Product" in output


def test_view_inventory_item_not_found(capsys):
    fake_response = Mock()

    fake_response.status_code = 404

    with patch("cli.requests.get") as mock_get:
        mock_get.return_value = fake_response

        with patch(
            "builtins.input",
            return_value="9999"
        ):
            view_inventory_item()

    output = capsys.readouterr().out

    assert "Inventory item not found." in output


def test_add_inventory_item(capsys):
    fake_response = Mock()

    fake_response.status_code = 201

    fake_response.json.return_value = {
        "id": 3,
        "barcode": "123456789",
        "product_name": "Test Product",
        "brand": "Test Brand",
        "category": "Test Category",
        "ingredients_text": "Test ingredients",
        "price": 200,
        "stock": 10
    }

    user_inputs = [
        "123456789",
        "Test Product",
        "Test Brand",
        "Test Category",
        "Test ingredients",
        "200",
        "10"
    ]

    with patch("cli.requests.post") as mock_post:
        mock_post.return_value = fake_response

        with patch(
            "builtins.input",
            side_effect=user_inputs
        ):
            add_inventory_item()

    mock_post.assert_called_once_with(
        "http://127.0.0.1:5000/inventory",
        json={
            "barcode": "123456789",
            "product_name": "Test Product",
            "brand": "Test Brand",
            "category": "Test Category",
            "ingredients_text": "Test ingredients",
            "price": 200.0,
            "stock": 10
        },
        timeout=10
    )

    output = capsys.readouterr().out

    assert "Inventory item added successfully." in output
    assert "Test Product" in output


def test_add_inventory_item_invalid_data(capsys):
    fake_response = Mock()

    fake_response.status_code = 400

    fake_response.json.return_value = {
        "error": "Missing required fields"
    }

    user_inputs = [
        "123456789",
        "Test Product",
        "Test Brand",
        "",
        "",
        "200",
        "10"
    ]

    with patch("cli.requests.post") as mock_post:
        mock_post.return_value = fake_response

        with patch(
            "builtins.input",
            side_effect=user_inputs
        ):
            add_inventory_item()

    output = capsys.readouterr().out

    assert "Invalid inventory data." in output


def test_update_inventory_item(capsys):
    fake_response = Mock()

    fake_response.status_code = 200

    fake_response.json.return_value = {
        "id": 1,
        "product_name": "Updated Product",
        "price": 750,
        "stock": 50
    }

    user_inputs = [
        "1",
        "",
        "Updated Product",
        "",
        "",
        "",
        "750",
        "50"
    ]

    with patch("cli.requests.patch") as mock_patch:
        mock_patch.return_value = fake_response

        with patch(
            "builtins.input",
            side_effect=user_inputs
        ):
            update_inventory_item()

    mock_patch.assert_called_once_with(
        "http://127.0.0.1:5000/inventory/1",
        json={
            "product_name": "Updated Product",
            "price": 750.0,
            "stock": 50
        },
        timeout=10
    )

    output = capsys.readouterr().out

    assert "Inventory item updated successfully." in output
    assert "Updated Product" in output


def test_update_inventory_item_not_found(capsys):
    fake_response = Mock()

    fake_response.status_code = 404

    user_inputs = [
        "9999",
        "",
        "Updated Product",
        "",
        "",
        "",
        "750",
        ""
    ]

    with patch("cli.requests.patch") as mock_patch:
        mock_patch.return_value = fake_response

        with patch(
            "builtins.input",
            side_effect=user_inputs
        ):
            update_inventory_item()

    output = capsys.readouterr().out

    assert "Inventory item not found." in output


def test_update_inventory_item_no_changes(capsys):
    user_inputs = [
        "1",
        "",
        "",
        "",
        "",
        "",
        "",
        ""
    ]

    with patch(
        "builtins.input",
        side_effect=user_inputs
    ):
        update_inventory_item()

    output = capsys.readouterr().out

    assert "No changes were provided." in output


def test_delete_inventory_item(capsys):
    fake_response = Mock()

    fake_response.status_code = 200

    fake_response.json.return_value = {
        "message": "Inventory item deleted successfully"
    }

    with patch("cli.requests.delete") as mock_delete:
        mock_delete.return_value = fake_response

        with patch(
            "builtins.input",
            side_effect=["1", "y"]
        ):
            delete_inventory_item()

    mock_delete.assert_called_once_with(
        "http://127.0.0.1:5000/inventory/1",
        timeout=10
    )

    output = capsys.readouterr().out

    assert "Inventory item deleted successfully" in output


def test_delete_inventory_item_cancelled(capsys):
    with patch(
        "builtins.input",
        side_effect=["1", "n"]
    ):
        with patch("cli.requests.delete") as mock_delete:
            delete_inventory_item()

    mock_delete.assert_not_called()

    output = capsys.readouterr().out

    assert "Delete cancelled." in output


def test_delete_inventory_item_not_found(capsys):
    fake_response = Mock()

    fake_response.status_code = 404

    with patch("cli.requests.delete") as mock_delete:
        mock_delete.return_value = fake_response

        with patch(
            "builtins.input",
            side_effect=["9999", "y"]
        ):
            delete_inventory_item()

    output = capsys.readouterr().out

    assert "Inventory item not found." in output


def test_search_openfoodfacts(capsys):
    fake_response = Mock()

    fake_response.status_code = 200

    fake_response.json.return_value = {
        "code": "3017624010701",
        "product_name": "Nutella",
        "brands": "Ferrero",
        "categories": "Spreads",
        "ingredients_text": "Sugar, hazelnuts, cocoa"
    }

    with patch("cli.requests.get") as mock_get:
        mock_get.return_value = fake_response

        with patch(
            "builtins.input",
            return_value="3017624010701"
        ):
            search_openfoodfacts()

    mock_get.assert_called_once_with(
        "http://127.0.0.1:5000/products/external/3017624010701",
        timeout=10
    )

    output = capsys.readouterr().out

    assert "Nutella" in output
    assert "Ferrero" in output


def test_search_openfoodfacts_not_found(capsys):
    fake_response = Mock()

    fake_response.status_code = 404

    with patch("cli.requests.get") as mock_get:
        mock_get.return_value = fake_response

        with patch(
            "builtins.input",
            return_value="999999999"
        ):
            search_openfoodfacts()

    output = capsys.readouterr().out

    assert "Product not found on OpenFoodFacts." in output


def test_search_openfoodfacts_empty_barcode(capsys):
    with patch(
        "builtins.input",
        return_value=""
    ):
        with patch("cli.requests.get") as mock_get:
            search_openfoodfacts()

    mock_get.assert_not_called()

    output = capsys.readouterr().out

    assert "Barcode cannot be empty." in output


def test_import_openfoodfacts_product(capsys):
    fake_response = Mock()

    fake_response.status_code = 201

    fake_response.json.return_value = {
        "id": 3,
        "barcode": "987654321",
        "product_name": "Imported Product",
        "brand": "Imported Brand",
        "category": "Imported Category",
        "ingredients_text": "Imported ingredients",
        "price": 0,
        "stock": 0
    }

    with patch("cli.requests.post") as mock_post:
        mock_post.return_value = fake_response

        with patch(
            "builtins.input",
            return_value="987654321"
        ):
            import_openfoodfacts_product()

    mock_post.assert_called_once_with(
        "http://127.0.0.1:5000/inventory/import/987654321",
        timeout=10
    )

    output = capsys.readouterr().out

    assert "Product imported successfully." in output
    assert "Imported Product" in output


def test_import_openfoodfacts_product_already_exists(capsys):
    fake_response = Mock()

    fake_response.status_code = 409

    with patch("cli.requests.post") as mock_post:
        mock_post.return_value = fake_response

        with patch(
            "builtins.input",
            return_value="3017624010701"
        ):
            import_openfoodfacts_product()

    output = capsys.readouterr().out

    assert "This product already exists in inventory." in output


def test_import_openfoodfacts_product_not_found(capsys):
    fake_response = Mock()

    fake_response.status_code = 404

    with patch("cli.requests.post") as mock_post:
        mock_post.return_value = fake_response

        with patch(
            "builtins.input",
            return_value="999999999"
        ):
            import_openfoodfacts_product()

    output = capsys.readouterr().out

    assert "Product not found on OpenFoodFacts." in output


def test_main_exit(capsys):
    with patch(
        "builtins.input",
        return_value="8"
    ):
        main()

    output = capsys.readouterr().out

    assert "Goodbye!" in output


def test_main_invalid_option(capsys):
    with patch(
        "builtins.input",
        side_effect=["99", "8"]
    ):
        main()

    output = capsys.readouterr().out

    assert "Invalid option. Please choose 1-8." in output
    assert "Goodbye!" in output
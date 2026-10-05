from unittest.mock import Mock, patch

import requests

from app.openfoodfacts import get_product_by_barcode


def test_get_product_by_barcode_success():
    fake_response = Mock()

    fake_response.json.return_value = {
        "product": {
            "code": "3017624010701",
            "product_name": "Nutella",
            "brands": "Ferrero"
        }
    }

    with patch("app.openfoodfacts.requests.get") as mock_get:
        mock_get.return_value = fake_response

        result = get_product_by_barcode("3017624010701")

    assert result["product_name"] == "Nutella"
    assert result["brands"] == "Ferrero"
    assert result["code"] == "3017624010701"

    mock_get.assert_called_once_with(
        "https://world.openfoodfacts.org/api/v3/product/3017624010701",
        headers={
            "User-Agent": "InventoryManagementSystem/1.0"
        },
        timeout=10
    )


def test_get_product_by_barcode_request_error():
    with patch("app.openfoodfacts.requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException(
            "Connection error"
        )

        result = get_product_by_barcode("3017624010701")

    assert result is None


def test_get_product_by_barcode_http_error():
    fake_response = Mock()

    fake_response.raise_for_status.side_effect = (
        requests.RequestException("404 Not Found")
    )

    with patch("app.openfoodfacts.requests.get") as mock_get:
        mock_get.return_value = fake_response

        result = get_product_by_barcode("999999999")

    assert result is None


def test_get_product_by_barcode_product_missing():
    fake_response = Mock()

    fake_response.json.return_value = {
        "code": "999999999",
        "status": 0
    }

    with patch("app.openfoodfacts.requests.get") as mock_get:
        mock_get.return_value = fake_response

        result = get_product_by_barcode("999999999")

    assert result is None
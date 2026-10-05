import requests

BASE_URL = "https://world.openfoodfacts.org/api/v3/product"


def get_product_by_barcode(barcode):
    url = f"{BASE_URL}/{barcode}"

    headers = {
        "User-Agent": "InventoryManagementSystem/1.0"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

    except requests.RequestException:
        return None

    data = response.json()

    if "product" not in data:
        return None

    return data["product"]

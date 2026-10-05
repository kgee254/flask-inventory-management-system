import requests

BASE_URL = "http://127.0.0.1:5000"

def display_menu():
    print("\n================================")
    print("   Inventory Management System")
    print("================================")
    print("1. View inventory")
    print("2. View inventory item")
    print("3. Add inventory item")
    print("4. Update inventory item")
    print("5. Delete inventory item")
    print("6. Search OpenFoodFacts")
    print("7. Import product from OpenFoodFacts")
    print("8. Exit")


def display_item(item):
    print("\n--------------------------------")
    print(f"ID:           {item.get('id')}")
    print(f"Barcode:      {item.get('barcode')}")
    print(f"Product:      {item.get('product_name')}")
    print(f"Brand:        {item.get('brand')}")
    print(f"Category:     {item.get('category')}")
    print(f"Ingredients:  {item.get('ingredients_text')}")
    print(f"Price:        {item.get('price')}")
    print(f"Stock:        {item.get('stock')}")
    print("--------------------------------")


def display_inventory(items):
    if not items:
        print("\nInventory is empty.")
        return
    
    print("\n========== INVENTORY ==========")
    for item in items:
        display_item(item)


def get_integer(prompt):
    while True:
        value = input(prompt)

        try:
            return int(value)
        except ValueError:
            print("Please enter a valid number.")


def get_float(prompt):
    while True:
        value = input(prompt)

        try:
            return float(value)
        except ValueError:
            print("Please enter a valid number.")


def view_inventory():
    try:
        response = requests.get(
            f"{BASE_URL}/inventory",
            timeout=10
        )

        response.raise_for_status()

        inventory = response.json()

        display_inventory(inventory)

    except requests.RequestException:
        print("\nUnable to connect to the Flask API.")
        print("Make sure the Flask server is running.")


def view_inventory_item():
    item_id = get_integer("Enter inventory item ID: ")

    try:
        response = requests.get(
            f"{BASE_URL}/inventory/{item_id}",
            timeout=10
        )

        if response.status_code == 404:
            print("\nInventory item not found.")
            return

        response.raise_for_status()

        item = response.json()

        display_item(item)

    except requests.RequestException:
        print("\nUnable to connect to the Flask API.")


def add_inventory_item():
    print("\n========== ADD INVENTORY ITEM ==========")

    barcode = input("Barcode: ")
    product_name = input("Product name: ")
    brand = input("Brand: ")
    category = input("Category: ")
    ingredients_text = input("Ingredients: ")
    price = get_float("Price: ")
    stock = get_integer("Stock: ")

    item = {
        "barcode": barcode,
        "product_name": product_name,
        "brand": brand,
        "category": category,
        "ingredients_text": ingredients_text,
        "price": price,
        "stock": stock
    }

    try:
        response = requests.post(
            f"{BASE_URL}/inventory",
            json=item,
            timeout=10
        )

        if response.status_code == 400:
            print("\nInvalid inventory data.")
            print(response.json())
            return

        response.raise_for_status()

        new_item = response.json()

        print("\nInventory item added successfully.")
        display_item(new_item)

    except requests.RequestException:
        print("\nUnable to connect to the Flask API.")


def update_inventory_item():
    print("\n========== UPDATE INVENTORY ITEM ==========")

    item_id = get_integer("Enter inventory item ID: ")

    print("\nLeave a field blank if you do not want to change it.")

    barcode = input("Barcode: ")
    product_name = input("Product name: ")
    brand = input("Brand: ")
    category = input("Category: ")
    ingredients_text = input("Ingredients: ")
    price = input("Price: ")
    stock = input("Stock: ")

    data = {}

    if barcode:
        data["barcode"] = barcode

    if product_name:
        data["product_name"] = product_name

    if brand:
        data["brand"] = brand

    if category:
        data["category"] = category

    if ingredients_text:
        data["ingredients_text"] = ingredients_text

    if price:
        try:
            data["price"] = float(price)
        except ValueError:
            print("Invalid price.")
            return

    if stock:
        try:
            data["stock"] = int(stock)
        except ValueError:
            print("Invalid stock.")
            return

    if not data:
        print("\nNo changes were provided.")
        return

    try:
        response = requests.patch(
            f"{BASE_URL}/inventory/{item_id}",
            json=data,
            timeout=10
        )

        if response.status_code == 404:
            print("\nInventory item not found.")
            return

        response.raise_for_status()

        updated_item = response.json()

        print("\nInventory item updated successfully.")
        display_item(updated_item)

    except requests.RequestException:
        print("\nUnable to connect to the Flask API.")


def delete_inventory_item():
    print("\n========== DELETE INVENTORY ITEM ==========")

    item_id = get_integer("Enter inventory item ID: ")

    confirmation = input(
        "Are you sure you want to delete this item? (y/n): "
    ).lower()

    if confirmation != "y":
        print("\nDelete cancelled.")
        return

    try:
        response = requests.delete(
            f"{BASE_URL}/inventory/{item_id}",
            timeout=10
        )

        if response.status_code == 404:
            print("\nInventory item not found.")
            return

        response.raise_for_status()

        result = response.json()

        print(f"\n{result.get('message')}")

    except requests.RequestException:
        print("\nUnable to connect to the Flask API.")


def search_openfoodfacts():
    print("\n========== SEARCH OPENFOODFACTS ==========")

    barcode = input("Enter product barcode: ")

    if not barcode:
        print("Barcode cannot be empty.")
        return

    try:
        response = requests.get(
            f"{BASE_URL}/products/external/{barcode}",
            timeout=10
        )

        if response.status_code == 404:
            print("\nProduct not found on OpenFoodFacts.")
            return

        response.raise_for_status()

        product = response.json()

        print("\n========== EXTERNAL PRODUCT ==========")
        print(f"Barcode:      {product.get('code', barcode)}")
        print(f"Product:      {product.get('product_name', 'Unknown')}")
        print(f"Brand:        {product.get('brands', 'Unknown')}")
        print(f"Category:     {product.get('categories', 'Unknown')}")
        print(
            f"Ingredients:  "
            f"{product.get('ingredients_text', 'Not available')}"
        )

    except requests.RequestException:
        print("\nUnable to connect to the Flask API.")


def import_openfoodfacts_product():
    print("\n========== IMPORT FROM OPENFOODFACTS ==========")

    barcode = input("Enter product barcode: ")

    if not barcode:
        print("Barcode cannot be empty.")
        return

    try:
        response = requests.post(
            f"{BASE_URL}/inventory/import/{barcode}",
            timeout=10
        )

        if response.status_code == 404:
            print("\nProduct not found on OpenFoodFacts.")
            return

        if response.status_code == 409:
            print("\nThis product already exists in inventory.")
            return

        response.raise_for_status()

        item = response.json()

        print("\nProduct imported successfully.")
        display_item(item)

    except requests.RequestException:
        print("\nUnable to connect to the Flask API.")


def main():
    while True:
        display_menu()

        choice = input("Choose an option: ")

        if choice == "1":
            view_inventory()

        elif choice == "2":
            view_inventory_item()

        elif choice == "3":
            add_inventory_item()

        elif choice == "4":
            update_inventory_item()

        elif choice == "5":
            delete_inventory_item()

        elif choice == "6":
            search_openfoodfacts()

        elif choice == "7":
            import_openfoodfacts_product()

        elif choice == "8":
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid option. Please choose 1-8.")


if __name__ == "__main__":
    main()
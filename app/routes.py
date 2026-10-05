from flask import Blueprint, request

from app.data import inventory


inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.route("/inventory", methods=["GET"])
def get_inventory():
    return inventory


@inventory_bp.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return item

    return {"error": "Inventory item not found"}, 404


@inventory_bp.route("/inventory", methods=["POST"])
def create_inventory_item():
    data = request.json

    required_fields = [
        "barcode",
        "product_name",
        "brand",
        "category",
        "ingredients_text",
        "price",
        "stock"
    ]

    missing_fields = [
        field for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return {
            "error": "Missing required fields",
            "fields": missing_fields
        }, 400

    new_item = {
        "id": max((item["id"] for item in inventory), default=0) + 1,
        "barcode": data["barcode"],
        "product_name": data["product_name"],
        "brand": data["brand"],
        "category": data["category"],
        "ingredients_text": data["ingredients_text"],
        "price": data["price"],
        "stock": data["stock"]
    }

    inventory.append(new_item)

    return new_item, 201


@inventory_bp.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_inventory_item(item_id):
    data = request.json

    allowed_fields = [
        "barcode",
        "product_name",
        "brand",
        "category",
        "ingredients_text",
        "price",
        "stock"
    ]

    for item in inventory:
        if item["id"] == item_id:

            for field in allowed_fields:
                if field in data:
                    item[field] = data[field]

            return item

    return {"error": "Inventory item not found"}, 404


@inventory_bp.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            inventory.remove(item)

            return {
                "message": "Inventory item deleted successfully"
            }

    return {"error": "Inventory item not found"}, 404
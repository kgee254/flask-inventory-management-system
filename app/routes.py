from flask import Blueprint


inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.route("/inventory", methods=["GET"])
def get_inventory():
    return {
        "message": "Get all inventory items"
    }


@inventory_bp.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    return {
        "message": "Get one inventory item",
        "id": item_id
    }


@inventory_bp.route("/inventory", methods=["POST"])
def create_inventory_item():
    return {
        "message": "Create inventory item"
    }


@inventory_bp.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_inventory_item(item_id):
    return {
        "message": "Update inventory item",
        "id": item_id
    }


@inventory_bp.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    return {
        "message": "Delete inventory item",
        "id": item_id
    }
from flask import Flask

from app.routes import inventory_bp


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def home():
        return {
            "message": "Inventory Management API is running"
        }

    app.register_blueprint(inventory_bp)

    return app
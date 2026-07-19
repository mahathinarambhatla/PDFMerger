"""Flask application factory.

Creates and configures the Flask app instance.

Exports:
    create_app() -> flask.Flask
"""

from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    app.config.from_object("app.config.Config")

    CORS(app)

    from app.routes import main
    app.register_blueprint(main)

    return app
"""
__init__.py

Package initializer for the Flask application.
Defines the application factory function `create_app`
which configures and returns the Flask app instance.
"""

from flask import Flask

from myPage import pages

def create_app():
    app = Flask(__name__)

    app.register_blueprint(pages.bp)
    return app

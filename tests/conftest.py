from flask import Flask
import pytest


@pytest.fixture
def flask_app(request):
    app = Flask("testapp")

    @app.route("/")
    def howdy():
        return "howdy!"

    return app

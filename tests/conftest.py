from fastapi import FastAPI
from flask import Flask
import pytest


@pytest.fixture
def flask_app(request):
    app = Flask("testapp")

    @app.route("/")
    def howdy():
        return "howdy!"

    return app


@pytest.fixture
def fastapi_app():
    app = FastAPI()

    @app.get("/")
    def root():
        return {"message": "Howdy!"}

    return app

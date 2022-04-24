import pytest
import requests

from server_thread import ServerThread


def test_basic_flask_app(flask_app):
    server = ServerThread(flask_app, debug=True)
    requests.get(f"http://{server.host}:{server.port}/").raise_for_status()


def test_bad_port(flask_app):
    with pytest.raises(ValueError):
        ServerThread(flask_app, port="foo")


def test_server_shutdown(flask_app):
    server = ServerThread(flask_app, debug=True)
    url = f"http://{server.host}:{server.port}/"
    requests.get(url).raise_for_status()
    server.shutdown()
    del server
    with pytest.raises(requests.ConnectionError):
        requests.get(url).raise_for_status()

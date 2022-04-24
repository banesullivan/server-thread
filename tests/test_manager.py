import pytest
import requests

from server_thread import ServerDownError, ServerManager, launch_server


def test_launch_server(flask_app):
    key = launch_server(flask_app, debug=True)
    server = ServerManager.get_server(key)
    requests.get(f"http://{server.host}:{server.port}/").raise_for_status()
    key2 = launch_server(flask_app, debug=True)
    assert key == key2


def test_manager_shutdown(flask_app):
    # Default
    key = launch_server(flask_app, debug=True)
    server = ServerManager.get_server(key)
    url = f"http://{server.host}:{server.port}/"
    requests.get(url).raise_for_status()
    ServerManager.shutdown_server(key)
    requests.get(url).raise_for_status()
    ServerManager.shutdown_server(key, force=True)
    with pytest.raises(requests.ConnectionError):
        requests.get(url).raise_for_status()
    ServerManager.shutdown_server(key, force=True)
    with pytest.raises(ServerDownError):
        ServerManager.get_server(key)

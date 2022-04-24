import pytest
import requests
from werkzeug import Request, Response

from server_thread import ServerManager, launch_server


@Request.application
def app(request):
    return Response("howdy", 200)


class TestClient:
    def __init__(self, port="default", host="127.0.0.1", debug=False):
        self.key = launch_server(app, port=port, debug=debug, host=host)
        self.server = ServerManager.get_server(self.key)
        self.port = self.server.port
        self.host = self.server.host

    def raise_for_status(self):
        return requests.get(f"http://{self.host}:{self.port}/").raise_for_status()


def test_client_force_shutdown():
    client = TestClient(debug=True)
    client.raise_for_status()
    assert ServerManager.server_count() == 1
    ServerManager.shutdown_server(client.key, force=True)
    assert ServerManager.server_count() == 0
    with pytest.raises(requests.ConnectionError):
        client.raise_for_status()


def test_launch_non_default_server():
    default = TestClient()
    diff = TestClient(port=0)
    assert default.server != diff.server
    assert default.server.port != diff.server.port

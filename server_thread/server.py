import logging
import os
import threading
from typing import Union

from werkzeug.serving import make_server

logger = logging.getLogger(__name__)


class ServerDownError(Exception):
    """Raised when a ServerThread is down."""

    pass


class ServerManager:
    _LIVE_SERVERS = {}

    def __init__(self):
        raise NotImplementedError(
            "The ServerManager class cannot be instantiated."
        )  # pragma: no cover

    @staticmethod
    def server_count():
        return len(ServerManager._LIVE_SERVERS)

    @staticmethod
    def is_server_live(key: Union[int, str]):
        return key in ServerManager._LIVE_SERVERS and ServerManager._LIVE_SERVERS[key].is_alive()

    @staticmethod
    def add_server(key, val):
        ServerManager._LIVE_SERVERS[key] = val

    @staticmethod
    def pop_server(key):
        try:
            return ServerManager._LIVE_SERVERS.pop(key)
        except KeyError:
            raise ServerDownError("Server for this key has been shutdown.")

    @staticmethod
    def get_server(key):
        try:
            return ServerManager._LIVE_SERVERS[key]
        except KeyError:
            raise ServerDownError("Server for this key has been shutdown.")

    @staticmethod
    def shutdown_server(key: int, force: bool = False):
        if not force and key == "default":
            # We do not shut down the default server unless forced
            return
        try:
            server = ServerManager.pop_server(key)
            server.shutdown()
            del server
        except ServerDownError:
            logger.error(f"Server for key ({key}) not found.")


class ServerThread(threading.Thread):
    """Launch a server as a background thread."""

    def __init__(
        self,
        app,  # WSGIApplication
        port: int = 0,
        debug: bool = False,
        start: bool = True,
        host: str = "127.0.0.1",
    ):
        self._lts_initialized = False
        if not isinstance(port, int):
            raise ValueError(f"Port must be an int, not {type(port)}")

        if not debug:
            logging.getLogger("werkzeug").setLevel(logging.ERROR)
        else:
            if hasattr(app, "config") and isinstance(app.config, dict):
                app.config["DEBUG"] = True
            logging.getLogger("werkzeug").setLevel(logging.DEBUG)
            # make_server -> passthrough_errors ?

        if os.name == "nt" and host == "127.0.0.1":
            host = "localhost"
        self.srv = make_server(host, port, app, threaded=True)

        if hasattr(app, "app_context"):
            self.ctx = app.app_context()
            self.ctx.push()
        else:
            self.ctx = None

        # daemon = True  # CRITICAL for safe exit
        threading.Thread.__init__(self, daemon=True, target=self.srv.serve_forever)
        self._lts_initialized = True

        if start:
            self.start()

    def shutdown(self):
        if self._lts_initialized and self.is_alive():
            self.srv.shutdown()
            self.srv.server_close()
            self.join()

    def __del__(self):
        self.shutdown()

    @property
    def port(self):
        return self.srv.port

    @property
    def host(self):
        return self.srv.host


def launch_server(
    app,  # WSGIApplication
    port: Union[int, str] = "default",
    debug: bool = False,
    host: str = "127.0.0.1",
):
    if ServerManager.is_server_live(port):
        return port
    if port == "default":
        server = ServerThread(app, port=0, debug=debug, host=host)
    else:
        server = ServerThread(app, port=port, debug=debug, host=host)
        if port == 0:
            # Get reallocated port
            port = server.port
    ServerManager.add_server(port, server)
    return port

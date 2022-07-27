import logging
import os
import threading
import time
from typing import Union

import uvicorn
from werkzeug.serving import make_server

logger = logging.getLogger(__name__)


def is_fastapi(app):
    try:
        from fastapi import FastAPI

        return isinstance(app, FastAPI)
    except ImportError:  # pragma: no cover
        pass


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


class ServerBase:
    def __init__(self, app, host, port, debug: bool = False):
        raise NotImplementedError  # pragma: no cover

    def shutdown(self):
        raise NotImplementedError  # pragma: no cover

    def __del__(self):
        self.shutdown()

    @property
    def port(self):
        raise NotImplementedError  # pragma: no cover

    @property
    def host(self):
        raise NotImplementedError  # pragma: no cover

    @property
    def serve_forever(self):
        raise NotImplementedError  # pragma: no cover


class WSGIServer(ServerBase):
    """Manager for WSGI applications."""

    def __init__(self, app, host, port, debug: bool = False):
        self.server = make_server(host, port, app, threaded=True, passthrough_errors=debug)

    def shutdown(self):
        self.server.shutdown()
        self.server.server_close()

    @property
    def port(self):
        return self.server.port

    @property
    def host(self):
        return self.server.host

    @property
    def serve_forever(self):
        return self.server.serve_forever


class ASGIServer(ServerBase):
    """Manager for ASGI applications."""

    def __init__(self, app, host, port, debug: bool = False):
        config = uvicorn.Config(
            app, host=host, port=port, log_level="debug" if debug else "critical"
        )
        self.server = uvicorn.Server(config)

    @property
    def sock(self):
        if self.server.started:
            if (
                hasattr(self.server, "servers")
                and len(self.server.servers)  # noqa: W503
                and len(self.server.servers[0].sockets)  # noqa: W503
            ):
                return self.server.servers[0].sockets[0]
            else:
                raise ServerDownError("Server started, but no servers present")
        else:
            timeout = time.time() + 10
            while not self.server.started:
                if time.time() > timeout:
                    raise ServerDownError("Server not started")
        return self.sock

    def shutdown(self):
        self.server.should_exit = True
        self.server.handle_exit(0, None)
        # await self.server.shutdown()

    @property
    def port(self):
        return self.sock.getsockname()[1]

    @property
    def host(self):
        return self.sock.getsockname()[0]

    @property
    def serve_forever(self):
        return self.server.run


class ServerThread(threading.Thread):
    """Launch a server as a background thread."""

    def __init__(
        self,
        app,  # WSGI or ASGI Application
        port: int = 0,
        debug: bool = False,
        start: bool = True,
        host: str = "127.0.0.1",
        wsgi: bool = None,
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

        if (wsgi is not None and not wsgi) or (wsgi is None and is_fastapi(app)):
            self.srv = ASGIServer(app, host, port, debug=debug)
        else:  # Fallback to WSGI
            self.srv = WSGIServer(app, host, port, debug=debug)

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

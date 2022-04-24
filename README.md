# ⚙️ Server Thread

[![Tests](https://github.com/banesullivan/server-thread/actions/workflows/test.yml/badge.svg)](https://github.com/banesullivan/server-thread/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/banesullivan/server-thread/branch/main/graph/badge.svg?token=S0HQ64FW8G)](https://codecov.io/gh/banesullivan/server-thread)
[![PyPI](https://img.shields.io/pypi/v/server-thread.svg?logo=python&logoColor=white)](https://pypi.org/project/server-thread/)
[![conda](https://img.shields.io/conda/vn/conda-forge/server-thread.svg?logo=conda-forge&logoColor=white)](https://anaconda.org/conda-forge/server-thread)

Launch a WSGIApplication in a background thread with werkzeug.

This application was created for [`localtileserver`](https://github.com/banesullivan/localtileserver)
and provides the basis for how it can launch an image tile server as a
background thread for visualizing data in Jupyter notebooks.

While this may not be a widely applicable library, it is useful for a few
Python packages I have created that require a background service.


## 🚀 Usage

Use the `ServerThread` with any WSGIApplication.

Start by creating a WSGIApplication (this can be a flask app or a simple app
like below):


```py
# Create some WSGI Application
from werkzeug import Request, Response

@Request.application
def app(request):
    return Response("howdy", 200)
```

Then launch the app with the `ServerThread` class:


```py
import requests
from server_thread import ServerThread

# Launch app in a background thread
server = ServerThread(app)

# Perform requests against the server without blocking
requests.get(f"http://{server.host}:{server.port}/").raise_for_status()
```


## ⬇️ Installation

Get started with `server-thread` to create applications that require a
WSGIApplication in the background.

### 🐍 Installing with `conda`

Conda makes managing `server-thread`'s dependencies across platforms quite
easy and this is the recommended method to install:

```bash
conda install -c conda-forge server-thread
```

### 🎡 Installing with `pip`

If you prefer pip, then you can install from PyPI: https://pypi.org/project/server-thread/

```
pip install server-thread
```

## 💭 Feedback

Please share your thoughts and questions on the [Discussions](https://github.com/banesullivan/server-thread/discussions) board.
If you would like to report any bugs or make feature requests, please open an issue.

If filing a bug report, please share a scooby `Report`:

```py
import server_thread
print(server_thread.Report())
```

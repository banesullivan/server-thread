from io import open as io_open
import os

from setuptools import find_packages, setup

dirname = os.path.dirname(__file__)
readme_file = os.path.join(dirname, "README.md")
if os.path.exists(readme_file):
    with io_open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    # When this is first installed in development Docker, README.md is not available
    long_description = ""

# major, minor, patch
version_info = 0, 2, 0
# Nice string for the version
__version__ = ".".join(map(str, version_info))

setup(
    name="server-thread",
    version=__version__,
    description="Launch a WSGI or ASGI Application in a background thread with werkzeug or uvicorn.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Bane Sullivan",
    author_email="hello@banesullivan.com",
    url="https://github.com/banesullivan/server-thread",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python",
    ],
    python_requires=">=3.7",
    install_requires=[
        "scooby",
        "uvicorn",
        "werkzeug",
    ],
)

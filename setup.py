from os import path

from setuptools import find_packages, setup

from logiclayer import __version__

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md")) as f:
    README = f.read()

setup(
    name="logiclayer",
    version=__version__,
    description="The missing piece for all your data processing needs.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Francisco Abarzua",
    author_email="francisco@datawheel.us",
    url="https://github.com/Datawheel/logiclayer/",
    install_requires=["requests", "flask"],
    extras_require={
        ':python_version>="3.0"': ["requests >= 2.0.0"],
    },
    packages=find_packages(include=["logiclayer", "logiclayer.*"]),
    include_package_data=True,
    keywords="datawheel logiclayer data tesseract-olap",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: No Input/Output (Daemon)",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)

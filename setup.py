from os import path
from setuptools import find_packages
from setuptools import setup


# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

version = "0.1"

install_requires = ["pytz", "unidecode"]
tests_require = [
    "pytest",
]

setup(
    name="stellaspark_utils",
    packages=find_packages(include=["stellaspark_utils"]),
    version=version,
    license="MIT",
    description="A collection of python utilities for StellaSpark Nexus Digital Twin",
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="StellaSpark",
    author_email="support@stellaspark.com",
    maintainer="StellaSpark",
    maintainer_email="support@stellaspark.com",
    url="https://github.com/StellaSpark/stellaspark_utils",
    download_url=f"https://github.com/StellaSpark/stellaspark_utils/archive/v{version}.tar.gz",
    keywords=["stellaspark", "nexus", "utils", "calculation", "python"],
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={"test": tests_require},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Build Tools",
    ],
)

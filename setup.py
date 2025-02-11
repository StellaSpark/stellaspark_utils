from pathlib import Path
from setuptools import find_packages
from setuptools import setup


# Read the contents of your README file
readme_md_path = Path(".").resolve() / "README.md"


with open(readme_md_path.as_posix(), encoding="utf-8") as f:
    long_description = f.read()

version = "2.3"

# Use sqlalchemy <2.0 to avoid mandatory use of a text(<sql>). Only the last sqlalchymy version
# before 2.0 (version 1.4.49) can work with python 3.12 (so python 3.12 is included below).
install_requires = ["pytz", "unidecode", "sqlalchemy<2.0", "psycopg2-binary"]
tests_requires = [
    "pytest",
    "pytest-cov",
    "python-dotenv",
    "requests",
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
    python_requires=">=3.7, <=3.12",
    install_requires=install_requires,
    tests_require=tests_requires,
    extras_require={"test": tests_requires},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Build Tools",
    ],
)

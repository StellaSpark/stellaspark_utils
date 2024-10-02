from datetime import datetime
from distutils.command.sdist import sdist
from distutils.dist import Distribution
from pathlib import Path

import logging
import os
import subprocess
import sys
import time


logger = logging.getLogger(__name__)


CHANGES_PATH = Path(".") / "CHANGES.md"
ENV_STELLASPARK_UTILS_VERSION = "ENV_STELLASPARK_UTILS_VERSION"
DOTENV_PATH = Path(".") / ".env"


def load_dotenv():
    """Loads environment variables from a .env file into the environment.

    Why not use the 'from dotenv import load_dotenv'? That does not work in combination with build_distribution() below.
    """
    assert DOTENV_PATH.is_file(), f"{DOTENV_PATH} must exist"
    with open(DOTENV_PATH.as_posix()) as f:
        for line in f:
            # Strip whitespace and skip comments or empty lines
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Split the line into key, value pairs
            if "=" in line:
                key, value = line.split("=", 1)

                # Strip whitespace from key and value
                key = key.strip()
                value = value.strip().strip('"').strip("'")  # Strip quotes around values if any

                # Set the environment variable
                os.environ[key] = value


def setup_logging() -> None:
    """Adds a configured handlers to the root logger: stream."""
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    stream_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt="%H:%M:%S"))

    root_logger = logging.getLogger()
    root_logger.addHandler(stream_handler)
    root_logger.setLevel(min([handler.level for handler in root_logger.handlers]))
    root_logger.debug("setup logging done")


def get_pypi_token() -> str:
    _pypi_token = os.getenv("PYPI_TOKEN")
    assert _pypi_token, "'PYPI_TOKEN=<your_pypi_token>' not found in the stellaspark_utils/.env file"
    assert _pypi_token.startswith("pypi-"), f"The pypi token should start with 'pypi-', but it is '{_pypi_token}'"
    return _pypi_token


def get_version() -> str:
    """Read and validate the version from version.txt."""
    version_path = Path(".") / "version.txt"
    assert version_path.is_file(), f"Version file '{version_path}' must exist"
    with open(version_path.as_posix(), "r") as f:
        _version = f.readline().strip()

    # Validate format
    error_msg = f"Version '{_version}' in '{version_path}' is not valid. Expected format is x.y"
    assert len(_version) == 3, error_msg
    for version_number in [_version[0], _version[2]]:
        try:
            int(version_number)
        except ValueError:
            raise ValueError(error_msg)
    assert _version[1] == ".", error_msg

    logger.info(f"Successfully detected version '{_version}'")
    time.sleep(1)

    return _version


def validate_version_is_in_changes(_version: str) -> None:
    assert CHANGES_PATH.is_file(), f"CHANGES file '{CHANGES_PATH}' must exist"
    today = datetime.today()
    expected_line = f"### {_version} <small> {today.strftime('%Y-%m-%d')} </small>"
    with open(CHANGES_PATH.as_posix(), "r") as f:
        expected_line_in_changes = expected_line in f.read()
    assert expected_line_in_changes, f"Line '{expected_line}' must be in '{CHANGES_PATH}'"


def build_distribution(_distribution_path: Path, _version: str, remove_if_exists: bool = True) -> None:
    logger.info(f"Building distribution {_version} to Pypi")

    if _distribution_path.is_file():
        msg = f"Distribution {_distribution_path} already exists."
        if remove_if_exists:
            logger.warning(f"{msg} Deleting it now...")
            os.remove(_distribution_path.as_posix())
        else:
            raise AssertionError(msg)

    # Set the version as an environment variable
    os.environ[ENV_STELLASPARK_UTILS_VERSION] = _version

    # Create a Distribution object
    dist = Distribution(attrs={"version": _version})

    # Set the distribution command to 'sdist'
    dist.script_name = "setup.py"
    dist.script_args = ["sdist"]

    # Run the 'sdist' command
    try:
        cmd = sdist(dist)
        cmd.ensure_finalized()
        cmd.run()
        logger.info(f"Successfully build {_distribution_path.as_posix()}")
    except Exception as err:
        logger.error(f"Failed to build {_distribution_path.as_posix()}, err={err}")
        sys.exit(1)

    # Run the twine command to upload to PyPI
    command = ["python", "setup.py", "sdist"]
    try:
        subprocess.run(command, check=True)
        logger.info(f"Successfully build {_distribution_path.as_posix()}")
    except subprocess.CalledProcessError as err:
        logger.error(f"Failed to build {_distribution_path.as_posix()}, err={err.output}")
        sys.exit(1)

    assert _distribution_path.is_file(), f"Distribution was build, but there is no file '{_distribution_path}'"


def release_to_pypi(_distribution_path: Path, _version: str) -> None:
    logger.info(f"Releasing stellaspark_utils {_version} to Pypi")
    # Run the twine command to upload to PyPI
    command = ["twine", "upload", _distribution_path.as_posix(), "--username", "__token__", "--password", pypi_token]
    try:
        subprocess.run(command, check=True)
        logger.info(f"Successfully uploaded {_distribution_path.as_posix()} to PyPI.")
    except subprocess.CalledProcessError as err:
        logger.info(f"Error: Failed to upload {_distribution_path.as_posix()}, err={err}")
        sys.exit(1)


if __name__ == "__main__":
    setup_logging()
    load_dotenv()
    pypi_token = get_pypi_token()
    version_found = get_version()
    validate_version_is_in_changes(version_found)

    distribution_path = Path(".") / "dist" / f"stellaspark_utils-{version_found}.tar.gz"

    build_distribution(distribution_path, version_found)
    release_to_pypi(distribution_path, version_found)

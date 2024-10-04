from constants import CHANGES_PATH
from constants import DIST_DIR
from constants import DOTENV_PATH
from constants import EGG_INFO_DIR
from constants import ENV_PACKAGE_VERSION
from constants import ENV_PYPI_TOKEN
from constants import MANIFEST_PATH
from constants import MODULE_NAMES
from constants import PACKAGE_NAME
from constants import PROJECT_ROOT_DIR
from constants import URL_PYPI
from constants import URL_PYPI_RELEASES
from constants import URL_PYPI_TOKEN
from constants import VERSION_PATH
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from pprint import pprint

import logging
import os
import shutil
import subprocess
import sys
import time


load_dotenv()

logger = logging.getLogger(__name__)


def get_distribution_path(_version: str) -> Path:
    return DIST_DIR / f"{PACKAGE_NAME}-{_version}.tar.gz"


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
    logger.debug("Run get_pypi_token()")
    assert DOTENV_PATH.is_file(), f"{DOTENV_PATH} must exist"
    _pypi_token = os.getenv(ENV_PYPI_TOKEN)
    msg_token = f"To create a Pypi token see '{URL_PYPI_TOKEN}'"
    assert _pypi_token, f"'{ENV_PYPI_TOKEN}=<your_pypi_token>' not found in '{DOTENV_PATH}'. {msg_token}"
    assert _pypi_token.startswith("pypi-"), f"The pypi token '{_pypi_token} must start with 'pypi-'. . {msg_token}"
    return _pypi_token


def read_release_version() -> str:
    """Read and validate the version from version.txt."""
    logger.debug("Run get_version()")

    assert VERSION_PATH.is_file(), f"Version file '{VERSION_PATH}' must exist"
    with open(VERSION_PATH.as_posix(), "r") as f:
        _version = f.readline().strip()

    # Validate format
    error_msg = f"Version '{_version}' in '{VERSION_PATH}' is not valid. Expected format is x.y"
    assert len(_version) == 3, error_msg
    for version_number in [_version[0], _version[2]]:
        try:
            int(version_number)
        except ValueError:
            raise ValueError(error_msg)
    assert _version[1] == ".", error_msg

    logger.info(f"Detected version '{_version}' from '{VERSION_PATH}'")
    time.sleep(1)

    return _version


def validate_version_is_in_changes(version: str) -> None:
    logger.debug("Run validate_version_is_in_changes()")
    assert CHANGES_PATH.is_file(), f"CHANGES file '{CHANGES_PATH}' must exist"
    today = datetime.today()
    expected_line = f"### {version} <small> {today.strftime('%Y-%m-%d')} </small>"
    with open(CHANGES_PATH.as_posix(), "r") as f:
        expected_line_in_changes = expected_line in f.read()
    if not expected_line_in_changes:
        msg = f"Releasing version '{version}' today, so line '{expected_line}' must be in '{CHANGES_PATH}'"
        raise AssertionError(msg)


def validate_modules() -> None:
    logger.debug("Run validate_modules()")
    modules_found = []
    for _path in PROJECT_ROOT_DIR.iterdir():
        try:
            if _path.is_dir():
                if "__init__.py" in [x.name for x in _path.iterdir()]:
                    modules_found.append(_path.name)
        except Exception as err:
            if isinstance(err, OSError):
                # This is caused by the 'nul' file that is created during the run. We cannot delete it automatically..
                continue
            logger.warning(err)
    expected_modules_not_found = [x for x in MODULE_NAMES if x not in modules_found]
    if expected_modules_not_found:
        msg = f"Some setup.py packages do not exists {expected_modules_not_found}. Is constants.MODULE_NAMES correct?"
        raise AssertionError(msg)


def build_distribution(version: str, if_exists: str) -> None:
    logger.debug("Run build_distribution()")
    logger.info(f"Building distribution version '{version}'")

    assert if_exists in ["remove", "exit", "raise"]
    distribution_path = get_distribution_path(version)
    if distribution_path.exists():
        msg = f"Distribution {distribution_path} already exists"
        if if_exists == "raise":
            raise AssertionError(f"{msg}. Please delete manually and try again")
        elif if_exists == "remove":
            logger.warning(f"{msg}. We will delete it now, and then continue")
            time.sleep(2)
            os.remove(distribution_path.as_posix())
        elif if_exists == "exit":
            clean_files_and_dirs(delete_dist_files=False)
            logger.warning(f"{msg}. Exiting now")
            sys.exit(1)
        else:
            msg = f"Argument 'if_exists' '{if_exists}' in build_distribution() must be in ['remove', 'exit', 'raise']"
            raise NotImplementedError(msg)

    # Set the version as an environment variable
    os.environ[ENV_PACKAGE_VERSION] = version

    # Run the twine command to upload to PyPI
    command = ["python", "setup.py", "sdist"]
    try:
        subprocess.run(command, check=True)
        logger.info(f"Successfully build {distribution_path.as_posix()}")
    except subprocess.CalledProcessError as err:
        clean_files_and_dirs(delete_dist_files=False)
        logger.error(f"Exiting now as we failed to build {distribution_path.as_posix()}, err={err.output}")
        sys.exit(1)

    # Ensure that the distribution (the tar.gz file) was created
    if distribution_path.is_file():
        return
    dists_found = [x.as_posix() for x in DIST_DIR.iterdir()]
    msg = f"Distribution was build, but there is no file '{distribution_path}'. Distribution files found {dists_found}"
    raise AssertionError(msg)


def release_to_pypi(version: str, pypi_token: str) -> None:
    logger.debug("Run release_to_pypi()")
    logger.info(f"Releasing {PACKAGE_NAME} {version} to Pypi '{URL_PYPI}'")

    distribution_path = get_distribution_path(version)

    # Run the twine command to upload to PyPI
    file_path = distribution_path.as_posix()
    command = ["twine", "upload", file_path, "--username", "__token__", "--password", pypi_token, "--verbose"]
    try:
        subprocess.run(command, check=True, capture_output=True)
        logger.info(f"Successfully uploaded {distribution_path.as_posix()} to PyPI '{URL_PYPI}'")
    except subprocess.CalledProcessError as err:
        clean_files_and_dirs(delete_dist_files=False)
        pypi_response = str(err.output).lower()
        print("\n")
        print("-------------------------------------- Start pypi response -----------------------------------------")
        pprint(pypi_response)
        print("--------------------------------------- End pypi response ------------------------------------------")
        print("\n")
        if "file already exists" in pypi_response:
            msg = f"release to pypi failed as version '{version}' already exists on pypi '{URL_PYPI_RELEASES}'"
        else:
            msg = f"release to pypi failed, err={err}"
        logger.error(f"Exiting now as {msg}")
        sys.exit(1)


def clean_files_and_dirs(delete_dist_files: bool) -> None:
    logger.debug("Run clean_files_and_dirs()")

    dirs_to_remove = [EGG_INFO_DIR]
    files_to_remove = [MANIFEST_PATH]
    if delete_dist_files and DIST_DIR.is_dir():
        files_to_remove.extend([x for x in DIST_DIR.iterdir()])

    # Delete directories
    for dir_path in dirs_to_remove:
        try:
            if dir_path.is_dir():
                logger.debug(f"Deleting dir {dir_path}")
                shutil.rmtree(dir_path.as_posix())
        except Exception as err:
            logger.warning(f"Could not delete dir {dir_path}, err={err}")

    # Delete files
    for file_path in files_to_remove:
        try:
            if file_path.is_file():
                logger.debug(f"Deleting file {file_path}")
                os.remove(file_path.as_posix())
        except Exception as err:
            logger.warning(f"Could not delete file {file_path}, err={err}")


if __name__ == "__main__":
    setup_logging()
    clean_files_and_dirs(delete_dist_files=True)
    load_dotenv()
    pypi_token_found = get_pypi_token()
    validate_modules()
    version_found = read_release_version()
    validate_version_is_in_changes(version_found)
    build_distribution(version_found, if_exists="exit")
    release_to_pypi(version_found, pypi_token_found)
    clean_files_and_dirs(delete_dist_files=False)

    logger.info("Shutting down")

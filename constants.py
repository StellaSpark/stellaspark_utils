from pathlib import Path


# The PACKAGE_NAME will be normalized ('_' to '-'), see https://peps.python.org/pep-0503/#normalized-names
# Results in (see https://stackoverflow.com/a/54599368):
#   - distribution name for example: 'stellaspark-utils-0.2.tar.gz'         <- with dash
#   - pypi url: https://pypi.org/project/stellaspark-utils/                 <- with dash
#   - pip install command: 'pip install stellaspark-utils'                  <- with dash
PACKAGE_NAME = "stellaspark-utils"

# The MODULE_NAMES are underscore '_' because of python conventions
# Results in:
#   - '>>> import stellaspark_utils'                                        <- with underscore
#   - '>>> from stellaspark_utils import db'                                <- with underscore
MODULE_NAMES = ["stellaspark_utils"]
REPO_NAME = "stellaspark_utils"
ENV_PACKAGE_VERSION = "ENV_PACKAGE_VERSION"
ENV_PYPI_TOKEN = "PYPI_TOKEN"
URL_PYPI = f"https://pypi.org/project/{PACKAGE_NAME}/"
URL_PYPI_RELEASES = f"{URL_PYPI}#files"
URL_PYPI_TOKEN = "https://pypi.org/help/#apitoken"
PROJECT_ROOT_DIR = Path(".").resolve().absolute()
CHANGES_PATH = PROJECT_ROOT_DIR / "CHANGES.rst"
VERSION_PATH = PROJECT_ROOT_DIR / "version.txt"
DOTENV_PATH = PROJECT_ROOT_DIR / ".env"
MANIFEST_PATH = PROJECT_ROOT_DIR / "MANIFEST"
EGG_INFO_DIR = PROJECT_ROOT_DIR / f"{REPO_NAME}.egg-info"
DIST_DIR = PROJECT_ROOT_DIR / "dist"

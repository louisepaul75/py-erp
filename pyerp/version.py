"""Version information for pyERP."""

__version__ = "0.6.0"


def get_version():
    """Return the current version."""
    return __version__


def bump_version(version_type="patch"):
    """
    Bump the version number.

    Args:
        version_type (str): Type of version bump ('major', 'minor', or 'patch')
    """
    global __version__
    major, minor, patch = map(int, __version__.split("."))

    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1

    __version__ = f"{major}.{minor}.{patch}"
    return __version__

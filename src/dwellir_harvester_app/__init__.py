from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("dwellir-harvester")
except PackageNotFoundError:  # fallback for editable installs
    from .__version__ import __version__  # type: ignore

__all__ = ["cli", "daemon"]

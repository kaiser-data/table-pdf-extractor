import importlib

from .base import TableBackend
from .docling_backend import DoclingBackend
from .ollama_backend import OllamaBackend
from .img2table_backend import Img2TableBackend

BACKENDS: dict[str, type[TableBackend]] = {
    "docling": DoclingBackend,
    "ollama": OllamaBackend,
    "img2table": Img2TableBackend,
}

# Map backend names to the pip extra needed
_BACKEND_DEPS = {
    "docling": "docling",
    "ollama": None,  # only needs requests (core dep)
    "img2table": "img2table",
}


def backend_available(name: str) -> bool:
    """Check if a backend's dependencies are installed."""
    dep = _BACKEND_DEPS.get(name)
    if dep is None:
        return True
    try:
        importlib.import_module(dep)
        return True
    except ImportError:
        return False


__all__ = ["TableBackend", "BACKENDS", "backend_available"]

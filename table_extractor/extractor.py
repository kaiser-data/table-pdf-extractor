"""Main orchestrator for table extraction."""

from pathlib import Path

from .backends import BACKENDS, TableBackend


def get_backend(name: str, **kwargs) -> TableBackend:
    """Get a backend instance by name.

    Args:
        name: Backend name (docling, ollama, img2table).
        **kwargs: Backend-specific options (e.g. model for ollama).

    Returns:
        Configured TableBackend instance.
    """
    if name not in BACKENDS:
        available = ", ".join(sorted(BACKENDS))
        raise ValueError(f"Unknown backend '{name}'. Available: {available}")

    cls = BACKENDS[name]
    if name == "ollama":
        return cls(model=kwargs.get("model", "gemma3"))
    return cls()


def extract_tables(
    path: str | Path,
    backend: str = "docling",
    pages: list[int] | None = None,
    **kwargs,
) -> list[list[list[str]]]:
    """Extract tables from a file.

    Args:
        path: Path to PDF or image file.
        backend: Backend name.
        pages: Optional 0-indexed page numbers (PDF only).
        **kwargs: Passed to get_backend.

    Returns:
        List of tables (each is list of rows of cell strings).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    be = get_backend(backend, **kwargs)
    return be.extract(path, pages=pages)

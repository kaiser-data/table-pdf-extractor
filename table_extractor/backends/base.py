"""Abstract base class for table extraction backends."""

from abc import ABC, abstractmethod
from pathlib import Path


class TableBackend(ABC):
    """Base class all extraction backends must implement.

    extract() returns a list of tables. Each table is a list of rows,
    and each row is a list of cell strings.
    """

    @abstractmethod
    def extract(self, path: Path, pages: list[int] | None = None) -> list[list[list[str]]]:
        """Extract tables from a PDF or image file.

        Args:
            path: Path to a PDF or image file.
            pages: Optional list of 0-indexed page numbers (PDF only).

        Returns:
            List of tables, where each table is a list of rows,
            and each row is a list of cell value strings.
        """
        ...

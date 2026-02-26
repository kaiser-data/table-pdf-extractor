"""Utility functions for PDF conversion and CSV formatting."""

import csv
import io
from pathlib import Path

from PIL import Image

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}
PDF_EXTENSIONS = {".pdf"}


def is_image(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTENSIONS


def is_pdf(path: Path) -> bool:
    return path.suffix.lower() in PDF_EXTENSIONS


def pdf_to_images(path: Path, pages: list[int] | None = None) -> list[Image.Image]:
    """Convert PDF pages to PIL Images using pdf2image (poppler).

    Args:
        path: Path to a PDF file.
        pages: Optional list of 0-indexed page numbers. If None, convert all.

    Returns:
        List of PIL Images, one per page.
    """
    from pdf2image import convert_from_path

    kwargs: dict = {"dpi": 300}
    if pages is not None:
        # pdf2image uses 1-indexed pages
        kwargs["first_page"] = min(pages) + 1
        kwargs["last_page"] = max(pages) + 1

    images = convert_from_path(str(path), **kwargs)

    if pages is not None and len(pages) == 1:
        return images

    if pages is not None:
        # Filter to only requested pages within the converted range
        base = min(pages)
        selected = []
        for p in pages:
            idx = p - base
            if 0 <= idx < len(images):
                selected.append(images[idx])
        return selected

    return images


def tables_to_csv(tables: list[list[list[str]]], output: io.TextIOBase | None = None, all_tables: bool = False) -> str | None:
    """Write extracted tables to CSV format.

    Args:
        tables: List of tables (each table is list of rows of cell strings).
        output: If provided, write to this file-like object and return None.
                If None, return the CSV as a string.
        all_tables: If True, include all tables (separated by blank line).
                   If False, only include the first table.

    Returns:
        CSV string if output is None, otherwise None.
    """
    if not tables:
        return "" if output is None else None

    selected = tables if all_tables else [tables[0]]

    buf = io.StringIO() if output is None else output
    writer = csv.writer(buf)

    for i, table in enumerate(selected):
        if i > 0:
            writer.writerow([])  # blank separator between tables
        for row in table:
            writer.writerow(row)

    if output is None:
        return buf.getvalue()
    return None

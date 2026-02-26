"""img2table backend - lightweight OpenCV-based table extraction."""

from pathlib import Path

from .base import TableBackend
from ..utils import is_pdf


class Img2TableBackend(TableBackend):
    """Extract tables using img2table with Tesseract OCR.

    Lightweight, near-zero GPU usage. Best for bordered/simple tables.
    """

    def extract(self, path: Path, pages: list[int] | None = None) -> list[list[list[str]]]:
        try:
            from img2table.document import Image as Img2TableImage, PDF as Img2TablePDF
            from img2table.ocr import TesseractOCR
        except ImportError:
            raise ImportError(
                "img2table is not installed. Install with: pip install table-pdf-extractor[img2table]"
            )

        ocr = TesseractOCR(lang="eng")

        if is_pdf(path):
            doc = Img2TablePDF(str(path), pages=pages)
        else:
            doc = Img2TableImage(str(path))

        extracted = doc.extract_tables(ocr=ocr, borderless_tables=False)

        tables = []
        if isinstance(extracted, dict):
            # PDF returns {page_idx: [tables]}
            for page_idx in sorted(extracted.keys()):
                for tbl in extracted[page_idx]:
                    rows = _extracted_table_to_rows(tbl)
                    if rows:
                        tables.append(rows)
        elif isinstance(extracted, list):
            # Image returns [tables]
            for tbl in extracted:
                rows = _extracted_table_to_rows(tbl)
                if rows:
                    tables.append(rows)

        return tables


def _extracted_table_to_rows(tbl) -> list[list[str]]:
    """Convert an img2table ExtractedTable to a list of row lists."""
    df = tbl.df
    if df is None or df.empty:
        return []
    header = [str(c) for c in df.columns.tolist()]
    rows = [header]
    for _, row in df.iterrows():
        rows.append([str(v) for v in row.tolist()])
    return rows

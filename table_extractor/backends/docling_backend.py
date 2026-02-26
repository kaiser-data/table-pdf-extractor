"""Docling backend - IBM's document understanding library with TableFormer."""

from pathlib import Path

from .base import TableBackend


class DoclingBackend(TableBackend):
    """Extract tables using IBM Docling with TableFormer model.

    Best table structure preservation. CUDA-accelerated, ARM64 compatible.
    """

    def extract(self, path: Path, pages: list[int] | None = None) -> list[list[list[str]]]:
        try:
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import (
                PdfPipelineOptions,
                TableFormerMode,
            )
            from docling.document_converter import DocumentConverter, PdfFormatOption
        except ImportError:
            raise ImportError(
                "Docling is not installed. Install with: pip install table-pdf-extractor[docling]"
            )

        pipeline_opts = PdfPipelineOptions(do_table_structure=True)
        pipeline_opts.table_structure_options.mode = TableFormerMode.FAST

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_opts),
            }
        )

        result = converter.convert(str(path))

        tables = []
        for table in result.document.tables:
            # Filter by page if requested
            if pages is not None and hasattr(table, "prov") and table.prov:
                page_no = table.prov[0].page_no  # 1-indexed
                if (page_no - 1) not in pages:
                    continue

            grid = table.export_to_dataframe()
            header = [str(c) for c in grid.columns.tolist()]
            rows = [header]
            for _, row in grid.iterrows():
                rows.append([str(v) for v in row.tolist()])
            tables.append(rows)

        return tables

"""CLI entrypoint for table-extract."""

import argparse
import sys
import time
from pathlib import Path

from . import __version__
from .extractor import extract_tables
from .utils import tables_to_csv


def parse_pages(spec: str) -> list[int]:
    """Parse a page range spec like '1-3,5' into 0-indexed page numbers."""
    pages = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            pages.extend(range(int(start) - 1, int(end)))
        else:
            pages.append(int(part) - 1)
    return sorted(set(pages))


def list_backends():
    """Print available backends and their install status."""
    from .backends import BACKENDS, backend_available

    print("Available backends:\n")
    for name in sorted(BACKENDS):
        installed = backend_available(name)
        status = "installed" if installed else "not installed"
        marker = "+" if installed else "-"
        hint = ""
        if not installed:
            hint = f"  (pip install table-pdf-extractor[{name}])"
        print(f"  [{marker}] {name:12s} {status}{hint}")


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        prog="table-extract",
        description="Extract tables from PDFs and images into CSV.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--list-backends", action="store_true",
        help="Show which backends are installed and exit",
    )
    parser.add_argument("input", nargs="?", type=Path, help="Path to a PDF or image file")
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output CSV file path (default: stdout)",
    )
    parser.add_argument(
        "--backend",
        choices=["docling", "ollama", "img2table"],
        default="docling",
        help="Extraction backend (default: docling)",
    )
    parser.add_argument(
        "--model",
        default="gemma3",
        help="Model name for ollama backend (default: gemma3)",
    )
    parser.add_argument(
        "--pages",
        default=None,
        help="Page range for PDFs, e.g. '1-3,5' (1-indexed)",
    )
    parser.add_argument(
        "--all-tables",
        action="store_true",
        help="Extract all tables, not just the first",
    )

    args = parser.parse_args(argv)

    if args.list_backends:
        list_backends()
        sys.exit(0)

    if args.input is None:
        parser.error("the following arguments are required: input")

    if not args.input.exists():
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    pages = parse_pages(args.pages) if args.pages else None

    print(f"Extracting tables from {args.input}...", file=sys.stderr)
    t0 = time.monotonic()

    try:
        tables = extract_tables(
            args.input,
            backend=args.backend,
            pages=pages,
            model=args.model,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    elapsed = time.monotonic() - t0

    if not tables:
        print(f"No tables found ({elapsed:.1f}s).", file=sys.stderr)
        sys.exit(0)

    print(
        f"Found {len(tables)} table(s) in {elapsed:.1f}s.",
        file=sys.stderr,
    )

    if args.output:
        with open(args.output, "w", newline="") as f:
            tables_to_csv(tables, output=f, all_tables=args.all_tables)
        count = len(tables) if args.all_tables else 1
        print(f"Wrote {count} table(s) to {args.output}", file=sys.stderr)
    else:
        csv_str = tables_to_csv(tables, all_tables=args.all_tables)
        sys.stdout.write(csv_str)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate a sample table image for testing table-extract.

Usage:
    python examples/create_sample.py
    # Creates examples/sample_table.png
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def create_sample_table(output_path: Path):
    """Create a PNG image of a simple table."""
    # Table data
    headers = ["Name", "Department", "Salary"]
    rows = [
        ["Alice Johnson", "Engineering", "$105,000"],
        ["Bob Smith", "Marketing", "$82,000"],
        ["Carol Williams", "Engineering", "$112,000"],
        ["David Brown", "Sales", "$78,500"],
        ["Eve Davis", "Marketing", "$91,000"],
    ]

    # Layout constants
    col_widths = [200, 180, 140]
    row_height = 40
    padding = 12
    margin = 30

    table_width = sum(col_widths)
    table_height = row_height * (len(rows) + 1)  # +1 for header
    img_width = table_width + 2 * margin
    img_height = table_height + 2 * margin

    # Create image
    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    # Try to use a monospace font, fall back to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
        font_bold = font

    x0, y0 = margin, margin

    # Draw header row (gray background)
    draw.rectangle([x0, y0, x0 + table_width, y0 + row_height], fill="#d0d0d0")
    x = x0
    for col_idx, header in enumerate(headers):
        draw.text((x + padding, y0 + padding), header, fill="black", font=font_bold)
        x += col_widths[col_idx]

    # Draw data rows
    for row_idx, row in enumerate(rows):
        y = y0 + row_height * (row_idx + 1)
        bg = "#f5f5f5" if row_idx % 2 == 0 else "white"
        draw.rectangle([x0, y, x0 + table_width, y + row_height], fill=bg)
        x = x0
        for col_idx, cell in enumerate(row):
            draw.text((x + padding, y + padding), cell, fill="black", font=font)
            x += col_widths[col_idx]

    # Draw grid lines
    # Horizontal lines
    for i in range(len(rows) + 2):
        y = y0 + row_height * i
        draw.line([(x0, y), (x0 + table_width, y)], fill="black", width=1)

    # Vertical lines
    x = x0
    for w in col_widths:
        draw.line([(x, y0), (x, y0 + table_height)], fill="black", width=1)
        x += w
    draw.line([(x, y0), (x, y0 + table_height)], fill="black", width=1)

    img.save(output_path)
    print(f"Created {output_path}")


if __name__ == "__main__":
    out = Path(__file__).parent / "sample_table.png"
    create_sample_table(out)

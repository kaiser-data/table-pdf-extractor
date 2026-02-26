# table-pdf-extractor

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20aarch64-lightgrey)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

**Extract tables from PDFs and images into CSV** — a practical CLI tool designed to run locally on edge hardware like the NVIDIA Jetson Orin Nano.

No cloud APIs. No data leaves your machine.

## Architecture

```
┌──────────────────────────────────────────────────┐
│                  table-extract CLI                │
│                                                  │
│   input.pdf / input.png ──► CSV to stdout/file   │
└──────────────┬───────────────────────────────────┘
               │
       ┌───────┼───────────┐
       ▼       ▼           ▼
   ┌────────┐ ┌──────┐ ┌──────────┐
   │docling │ │ollama│ │img2table │
   │        │ │(VLM) │ │(OpenCV)  │
   └────────┘ └──────┘ └──────────┘
   TableFormer  Gemma3   Tesseract
   (GPU)       Qwen2-VL    OCR
               (GPU)
```

## Backend Comparison

| Backend    | Method           | GPU  | Best For                      | Install Extra       |
|------------|------------------|------|-------------------------------|---------------------|
| `docling`  | TableFormer DL   | Yes  | Complex/nested tables         | `[docling]`         |
| `ollama`   | Vision LLM       | Yes  | Messy layouts, handwriting    | Ollama running       |
| `img2table`| OpenCV + OCR     | No   | Simple bordered tables        | `[img2table]`       |

## Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) (for the `ollama` backend)
- [Poppler](https://poppler.freedesktop.org/) (`apt install poppler-utils`) for PDF support

### Install

```bash
git clone https://github.com/kaiser-data/table-pdf-extractor.git
cd table-pdf-extractor

python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

To install optional backends:

```bash
pip install -e ".[docling]"       # IBM Docling + TableFormer
pip install -e ".[img2table]"     # img2table + Tesseract
pip install -e ".[all]"           # Everything
```

### Usage

```bash
# Extract table from an image using Ollama (default model: gemma3)
table-extract photo.png --backend ollama -o output.csv

# Extract from PDF using docling
table-extract report.pdf --backend docling --pages 1-3

# Pipe CSV to stdout
table-extract scan.png --backend ollama

# Extract all tables (not just the first)
table-extract multi-table.pdf --backend ollama --all-tables

# List installed backends
table-extract --list-backends
```

### Try It Without a PDF

```bash
python examples/create_sample.py           # generates examples/sample_table.png
table-extract examples/sample_table.png --backend ollama -o test.csv
cat test.csv
```

## Hardware

Developed and tested on:

| Component | Spec                              |
|-----------|-----------------------------------|
| Board     | NVIDIA Jetson Orin Nano (8 GB)    |
| CPU       | 6-core Arm Cortex-A78AE           |
| GPU       | 1024-core Ampere (CUDA 8.7)       |
| OS        | JetPack 6 / Ubuntu 22.04 aarch64  |

The `ollama` backend with Gemma 3 4B runs comfortably within the 8 GB unified memory budget, making this setup ideal for air-gapped or on-premise table extraction.

## License

MIT

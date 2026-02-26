"""Ollama VLM backend - uses vision language models via Ollama API."""

import base64
import csv
import io
import json
from pathlib import Path

import requests
from PIL import Image

from .base import TableBackend
from ..utils import is_pdf, pdf_to_images

OLLAMA_URL = "http://localhost:11434"

EXTRACT_PROMPT = """Extract ALL tables from this image into CSV format.
Rules:
- Output ONLY the CSV data, no explanations or markdown fences.
- Use commas as delimiters.
- Include the header row.
- If there are multiple tables, separate them with a single blank line.
- Preserve the exact text from each cell.
"""


class OllamaBackend(TableBackend):
    """Extract tables using a vision language model via Ollama.

    Supports Qwen2.5-VL, Gemma 3, and other vision models.
    """

    def __init__(self, model: str = "gemma3"):
        self.model = model

    def _image_to_base64(self, img: Image.Image) -> str:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def _check_connectivity(self):
        """Verify Ollama is reachable before making extraction requests."""
        try:
            resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            resp.raise_for_status()
        except requests.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {OLLAMA_URL}. "
                "Is Ollama running? Start it with: ollama serve"
            )
        except requests.Timeout:
            raise ConnectionError(
                f"Ollama at {OLLAMA_URL} is not responding. "
                "Is Ollama running? Start it with: ollama serve"
            )

    def _query_ollama(self, image_b64: str) -> str:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": self.model,
                "prompt": EXTRACT_PROMPT,
                "images": [image_b64],
                "stream": False,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["response"]

    def _parse_csv_response(self, text: str) -> list[list[list[str]]]:
        """Parse the VLM response into tables (split on blank lines)."""
        # Strip markdown code fences if present
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = lines[1:]  # drop opening fence
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        tables = []
        current_chunk: list[str] = []

        for line in text.split("\n"):
            if line.strip() == "":
                if current_chunk:
                    tables.append(current_chunk)
                    current_chunk = []
            else:
                current_chunk.append(line)

        if current_chunk:
            tables.append(current_chunk)

        result = []
        for chunk in tables:
            reader = csv.reader(io.StringIO("\n".join(chunk)))
            rows = [row for row in reader if row]
            if rows:
                result.append(rows)

        return result

    def extract(self, path: Path, pages: list[int] | None = None) -> list[list[list[str]]]:
        self._check_connectivity()

        if is_pdf(path):
            images = pdf_to_images(path, pages)
        else:
            images = [Image.open(path)]

        all_tables = []
        for img in images:
            b64 = self._image_to_base64(img)
            response = self._query_ollama(b64)
            tables = self._parse_csv_response(response)
            all_tables.extend(tables)

        return all_tables

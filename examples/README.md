# Examples

## Generate a Sample Table

```bash
python examples/create_sample.py
```

This creates `examples/sample_table.png` — a simple employee table you can use to verify the tool works without needing to find a real PDF.

## Extract It

```bash
# Using Ollama (make sure it's running: ollama serve)
table-extract examples/sample_table.png --backend ollama -o output.csv

# Print to stdout
table-extract examples/sample_table.png --backend ollama
```

## Expected Output

```csv
Name,Department,Salary
Alice Johnson,Engineering,"$105,000"
Bob Smith,Marketing,"$82,000"
Carol Williams,Engineering,"$112,000"
David Brown,Sales,"$78,500"
Eve Davis,Marketing,"$91,000"
```

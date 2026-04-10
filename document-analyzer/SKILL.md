---
name: document-analyzer
description: "Use this skill when you need to read, inspect, or extract content from documents — PDF, DOCX, XLSX, PPTX, CSV. Covers content inventory, text extraction, table extraction, page rasterization for visual inspection, embedded image/attachment/form-field extraction, OCR for scanned documents, and choosing the right reading strategy for different document and file types. Do NOT use this skill for document creation, editing, form filling, merging, splitting, watermarking, or encryption."
license: MIT
---

# Document Analyzer

## Overview

This skill covers reading and analysis of documents across multiple
formats: PDF, DOCX, XLSX, PPTX, and CSV. It provides strategies for
text extraction, table extraction, visual inspection, OCR, and
format-specific best practices.

---

## General Protocol

1. **Look at the extension.** That is your dispatch key.
2. **Stat before you read.** Large files need sampling, not slurping.
   ```bash
   stat -c '%s bytes, %y' document.pdf
   file document.pdf
   ```
3. **Read just enough to answer the question.** If the user asked
   "how many rows are in this CSV", don't load the whole thing into
   pandas -- `wc -l` gives a fast approximation.
4. **Use the right tool for the format.** The dispatch table and
   format-specific sections below tell you which tool to reach for.

## Dispatch Table

| Extension                         | First move                                           |
| --------------------------------- | ---------------------------------------------------- |
| `.pdf`                            | Content inventory (see PDF section)                  |
| `.docx`                           | `pandoc` to markdown or `python-docx`                |
| `.doc` (legacy)                   | Convert to `.docx` first -- pandoc cannot read it    |
| `.xlsx`, `.xlsm`                  | `openpyxl` sheet names + head                        |
| `.xls` (legacy)                   | `pd.read_excel(engine="xlrd")`                       |
| `.ods`                            | `pd.read_excel(engine="odf")`                        |
| `.pptx`                           | `python-pptx` slide count                            |
| `.csv`, `.tsv`                    | `pandas` with `nrows`                                |

---

## PDF

### Content inventory

Run a quick diagnostic first. For simple tasks ("summarize this
document"), `pdfinfo` + a text sample may suffice. For anything
involving figures, attachments, or extraction issues, run the full set:

```bash
# Always: page count, file size, PDF version, metadata
pdfinfo document.pdf

# Always: quick text extraction check -- is this a text PDF or a scan?
pdftotext -f 1 -l 1 document.pdf - | head -20

# If figures/charts may matter:
pdfimages -list document.pdf

# If the PDF might contain embedded files (reports, portfolios):
pdfdetach -list document.pdf

# If text extraction looks garbled:
pdffonts document.pdf
```

This tells you:
- **Page count and size** -- how big is the job?
- **Text extractability** -- does `pdftotext` return real text, or is
  it empty (scanned) or garbled (broken font encoding)?
- **Embedded raster images** -- are there photos or raster figures?
  (Note: vector-drawn charts from matplotlib/Excel won't appear -- see
  "Extracting embedded images" below)
- **Attachments** -- are there embedded spreadsheets, data files, etc.?
- **Font status** -- are fonts embedded? If not, text extraction may
  produce wrong characters.

### Text extraction

**pypdf** for basic text:
```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text
text = ""
for page in reader.pages:
    text += page.extract_text()
```

**pdftotext** preserving layout (better for multi-column docs):
```bash
# Layout mode preserves spatial positioning
pdftotext -layout document.pdf output.txt

# Specific page range
pdftotext -f 1 -l 5 document.pdf output.txt
```

**pdfplumber** for layout-aware extraction with positioning data:
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

### Visual inspection (rasterize pages)

Text extraction is **blind** to charts, diagrams, figures, equations,
multi-column layout, and form structures. When any of these matter,
rasterize the relevant page and Read the image:

```bash
# Rasterize a single page (page 3 here) at 150 DPI
pdftoppm -jpeg -r 150 -f 3 -l 3 document.pdf /tmp/page

# pdftoppm zero-pads the output filename based on TOTAL page count
# (e.g., page-03.jpg for a 50-page PDF, page-003.jpg for 200+ pages)
# Don't guess the filename -- find it:
ls /tmp/page-*.jpg
```

Then Read the resulting image file. This gives you full visual
understanding of that page -- layout, charts, equations, everything.

**When to rasterize vs. text-extract:**
- **Content/data questions -> text extraction** (cheaper, searchable)
- **Figures, charts, visual layout -> rasterize the page**
- **Tables -> try text extraction first, rasterize if garbled**
- **Precision matters -> do both** (extract text AND rasterize; use text
  for data, image for context)

**Token cost awareness:**
- Text extraction: ~200-400 tokens per page
- Rasterized image: ~1,600 tokens per page (at 150 DPI)
- Both together: ~2,000-2,400 tokens per page

For a 100-page PDF, rasterizing everything would consume ~160K tokens.
Only rasterize pages that matter for the question at hand.

### Choosing your reading strategy

**Text-heavy documents** (reports, articles, books):
-> Text extraction is primary. Rasterize only for specific figures or
  pages where layout matters.

**Scanned documents** (no extractable text):
-> Rasterize pages at 150 DPI and Read them visually. For bulk text
  extraction, use OCR (pytesseract after converting pages to images).

**Slide-deck PDFs** (exported presentations):
-> Every page is primarily visual. Rasterize individual pages on demand.
  Text extraction gives you bullet-point text but loses all layout.

**Form-heavy documents**:
-> Extract form field values programmatically first (see below). Rasterize
  the form page for visual context if needed.

**Data-heavy documents** (tables, charts, figures):
-> Use pdfplumber for tables. Rasterize pages with charts/figures.
  Extract text for surrounding narrative. Consider both text AND image
  for the same page when precision matters.

### Table extraction

**pdfplumber** (recommended for most tables):
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables()
    for table in tables:
        for row in table:
            print(row)
```

**Advanced table settings** for complex layouts:
```python
import pdfplumber
import pandas as pd

with pdfplumber.open("complex_table.pdf") as pdf:
    page = pdf.pages[0]

    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
        "intersection_tolerance": 15
    }
    tables = page.extract_tables(table_settings)

    # Convert to DataFrame for analysis
    if tables:
        df = pd.DataFrame(tables[0][1:], columns=tables[0][0])
        print(df)
```

**camelot** (for tables with clear line boundaries):
```python
import camelot

tables = camelot.read_pdf("document.pdf", pages="1-3")
print(f"Found {len(tables)} tables")
for table in tables:
    print(table.df)
```

### Extracting embedded images

```bash
# List all embedded images with metadata (size, color, compression)
pdfimages -list document.pdf

# Extract all images as PNG
pdfimages -png document.pdf /tmp/img

# Extract from specific pages only (pages 3-5)
pdfimages -png -f 3 -l 5 document.pdf /tmp/img

# Extract in original format (JPEG stays JPEG, etc.)
pdfimages -all document.pdf /tmp/img
```

**Gotcha -- vector graphics:** `pdfimages` extracts only raster image
data. Charts and diagrams drawn as vector graphics (common in
matplotlib, Excel, and R exports) will NOT appear -- they are page
content operators, not image objects. For these, rasterize the whole
page with `pdftoppm` instead.

**Gotcha -- empty images:** `pdfimages` sometimes produces many tiny or
empty image files -- these are typically background masks, transparency
layers, or decorative elements. Filter by file size to find the real
content images.

### Extracting file attachments

PDFs can contain embedded files -- spreadsheets, data files, other
documents. Common in business reports, PDF portfolios, and PDF/A-3
compliance documents.

```bash
# List all attachments
pdfdetach -list document.pdf

# Extract all attachments to a directory
mkdir -p /tmp/attachments
pdfdetach -saveall -o /tmp/attachments/ document.pdf

# Extract a specific attachment by number (1-based index from -list output)
pdfdetach -save 1 -o /tmp/attachment.pdf document.pdf
```

In Python:
```python
import os
from pypdf import PdfReader

reader = PdfReader("document.pdf")
for name, content_list in reader.attachments.items():
    safe_name = os.path.basename(name)  # sanitize -- name comes from the PDF
    for content in content_list:
        with open(f"/tmp/{safe_name}", "wb") as f:
            f.write(content)
```

**Two attachment mechanisms exist in PDFs:** page-level file annotation
attachments (shown as paperclip icons in viewers) and document-level
embedded files (in the EmbeddedFiles name tree). Both `pdfdetach` and
pypdf handle the common cases.

### Extracting form field data

PDFs with interactive forms (government forms, applications, contracts)
have fillable fields whose values can be read programmatically:

```python
from pypdf import PdfReader

reader = PdfReader("form.pdf")

# Text input fields only:
fields = reader.get_form_text_fields()
for name, value in fields.items():
    print(f"{name}: {value}")

# All field types (checkboxes, radio buttons, dropdowns too):
all_fields = reader.get_fields() or {}
for name, field in all_fields.items():
    print(f"{name}: {field.get('/V', '')} (type: {field.get('/FT', '')})")
```

`get_form_text_fields()` returns only text input fields. For
government forms and contracts that use checkboxes, radio buttons,
and dropdowns, use `get_fields()` instead to see all field types.

For comprehensive field info (types, options, defaults):
```bash
pdftk form.pdf dump_data_fields
```

### PDF forms -- checking and extracting structure

**Check if a PDF has fillable fields:**
```bash
python scripts/check_fillable_fields.py <file.pdf>
```

**Extract form field info** (for fillable PDFs):
```bash
python scripts/extract_form_field_info.py <input.pdf> <field_info.json>
```

**Extract form structure** (for non-fillable PDFs -- text labels, lines, checkboxes):
```bash
python scripts/extract_form_structure.py <input.pdf> <form_structure.json>
```

**Convert PDF to images** for visual analysis:
```bash
python scripts/convert_pdf_to_images.py <input.pdf> <output_directory>
```

### OCR for scanned PDFs

When text extraction returns empty or garbage, the PDF is likely scanned.
Use OCR:

```python
import pytesseract
from pdf2image import convert_from_path

def extract_text_with_ocr(pdf_path, lang="eng"):
    images = convert_from_path(pdf_path, dpi=200)
    text = ""
    for i, image in enumerate(images):
        page_text = pytesseract.image_to_string(image, lang=lang)
        text += f"\n--- Page {i+1} ---\n{page_text}"
    return text
```

For Russian documents, use `lang="rus"` or `lang="rus+eng"` for mixed.

### Font diagnostics

If text extraction produces garbled output (wrong characters, missing
text, mojibake), check the font situation:

```bash
pdffonts document.pdf
```

Look at the "emb" column -- if fonts show "no" (not embedded) with
custom encodings, the PDF's character mapping may be broken for text
extraction. In that case, rasterize the page and use vision instead.

### Encrypted PDFs

```python
from pypdf import PdfReader

reader = PdfReader("encrypted.pdf")
if reader.is_encrypted:
    reader.decrypt("password")
    text = reader.pages[0].extract_text()
```

---

## DOCX

### Quick reading with pandoc

```bash
# Convert to markdown for quick reading
pandoc document.docx -t markdown

# First 200 lines for a preview
pandoc document.docx -t markdown | head -200

# Convert to plain text
pandoc document.docx -t plain
```

### Reading with python-docx

```python
from docx import Document

doc = Document("document.docx")

# Extract all text
for para in doc.paragraphs:
    print(para.text)

# Extract with style info
for para in doc.paragraphs:
    print(f"[{para.style.name}] {para.text}")
```

### Tables from DOCX

```python
from docx import Document

doc = Document("document.docx")
for i, table in enumerate(doc.tables):
    print(f"\nTable {i+1}:")
    for row in table.rows:
        cells = [cell.text for cell in row.cells]
        print(" | ".join(cells))
```

### Headers and footers

```python
from docx import Document

doc = Document("document.docx")
for section in doc.sections:
    header = section.header
    if header and header.paragraphs:
        print("Header:", " ".join(p.text for p in header.paragraphs))
    footer = section.footer
    if footer and footer.paragraphs:
        print("Footer:", " ".join(p.text for p in footer.paragraphs))
```

**Legacy `.doc`** -- pandoc and python-docx cannot read the old binary
format. Convert to `.docx` first using LibreOffice:
```bash
libreoffice --headless --convert-to docx document.doc
```

---

## XLSX / XLS / Spreadsheets

### Quick look with openpyxl

```python
from openpyxl import load_workbook

wb = load_workbook("data.xlsx", read_only=True)
print("Sheets:", wb.sheetnames)
ws = wb.active
for row in ws.iter_rows(max_row=5, values_only=True):
    print(row)
```

`read_only=True` matters -- without it, openpyxl loads the entire
workbook into memory, which breaks on large files. Do not trust
`ws.max_row` in read-only mode: many non-Excel writers omit the
dimension record, so it comes back `None` or wrong. If you need a row
count, iterate or use pandas.

### Reading with pandas

```python
import pandas as pd

# Read first sheet
df = pd.read_excel("data.xlsx", nrows=10)
print(df)
print(df.dtypes)

# Read specific sheet
df = pd.read_excel("data.xlsx", sheet_name="Sales")

# Read all sheets
dfs = pd.read_excel("data.xlsx", sheet_name=None)
for name, df in dfs.items():
    print(f"\n--- {name} ({len(df)} rows) ---")
    print(df.head())
```

### Legacy .xls

openpyxl raises `InvalidFileException`. Use:
```python
import pandas as pd
df = pd.read_excel("old.xls", engine="xlrd", nrows=5)
```

### OpenDocument .ods

openpyxl also rejects this. Use:
```python
import pandas as pd
df = pd.read_excel("data.ods", engine="odf", nrows=5)
```

---

## PPTX

```python
from itertools import islice
from pptx import Presentation

p = Presentation("deck.pptx")
print(f"{len(p.slides)} slides")
for i, slide in enumerate(islice(p.slides, 3), 1):
    texts = [s.text for s in slide.shapes if s.has_text_frame]
    print(f"Slide {i}:", " | ".join(t for t in texts if t))
```

`p.slides` is not subscriptable -- `p.slides[:3]` raises
`AttributeError`. Use `islice` or `list(p.slides)[:3]`.

**Legacy `.ppt`** -- python-pptx only reads OOXML. Convert to `.pptx`
first via LibreOffice:
```bash
libreoffice --headless --convert-to pptx presentation.ppt
```

---

## CSV / TSV

**Do not** `cat` or `head` these blindly. A CSV with a 50KB quoted cell
in row 1 will wreck your `head -5`. Use pandas with `nrows`:

```python
import pandas as pd

df = pd.read_csv("data.csv", nrows=5)
print(df)
print()
print(df.dtypes)
```

Approximate row count without loading (over-counts if the file has
RFC-4180 quoted newlines):
```bash
wc -l data.csv
```

Full analysis only after you know the shape:
```python
df = pd.read_csv("data.csv")
print(f"Shape: {df.shape}")
print(df.describe())
```

TSV: same, with `sep="\t"`.

### Large CSV files

For files that don't fit in memory, use chunked reading:
```python
import pandas as pd

chunks = pd.read_csv("large.csv", chunksize=10000)
for chunk in chunks:
    # Process each chunk
    print(chunk.shape)
```

### Encoding issues

If you get `UnicodeDecodeError`, try common encodings:
```python
import pandas as pd

# Try common encodings
for enc in ["utf-8", "latin-1", "cp1251", "cp1252"]:
    try:
        df = pd.read_csv("data.csv", encoding=enc, nrows=5)
        print(f"Success with {enc}")
        break
    except UnicodeDecodeError:
        continue
```

---

## Quick Reference

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Inspect PDF | poppler-utils | `pdfinfo`, `pdfimages -list`, `pdfdetach -list`, `pdffonts` |
| Extract text from PDF | pdfplumber | `page.extract_text()` |
| Extract text from PDF (CLI) | pdftotext | `pdftotext -layout input.pdf output.txt` |
| Extract tables from PDF | pdfplumber | `page.extract_tables()` |
| Extract tables from PDF (alt) | camelot | `camelot.read_pdf("input.pdf")` |
| See PDF page visually | pdftoppm | `pdftoppm -jpeg -r 150 -f N -l N` |
| Extract images from PDF | pdfimages | `pdfimages -png input.pdf prefix` |
| Extract PDF attachments | pdfdetach | `pdfdetach -saveall -o /tmp/` |
| Read PDF form fields | pypdf | `reader.get_fields()` |
| OCR scanned PDFs | pytesseract | Convert to image first, then `image_to_string()` |
| Read DOCX (quick) | pandoc | `pandoc doc.docx -t markdown` |
| Read DOCX (programmatic) | python-docx | `Document("doc.docx")` |
| Read XLSX | openpyxl | `load_workbook("data.xlsx", read_only=True)` |
| Read XLSX (pandas) | pandas | `pd.read_excel("data.xlsx")` |
| Read PPTX | python-pptx | `Presentation("deck.pptx")` |
| Read CSV | pandas | `pd.read_csv("data.csv", nrows=5)` |
| Read CSV row count | wc | `wc -l data.csv` |

## Helper Scripts

All scripts are in the `scripts/` directory and accept file paths as CLI arguments.

| Script | Purpose | Usage |
|--------|---------|-------|
| `check_fillable_fields.py` | Check if PDF has fillable form fields | `python scripts/check_fillable_fields.py <file.pdf>` |
| `extract_form_field_info.py` | Extract fillable form field metadata to JSON | `python scripts/extract_form_field_info.py <input.pdf> <output.json>` |
| `extract_form_structure.py` | Extract non-fillable form structure (labels, lines, checkboxes) | `python scripts/extract_form_structure.py <input.pdf> <output.json>` |
| `convert_pdf_to_images.py` | Convert PDF pages to PNG images | `python scripts/convert_pdf_to_images.py <input.pdf> <output_dir>` |
| `check_bounding_boxes.py` | Validate bounding boxes in fields.json | `python scripts/check_bounding_boxes.py <fields.json>` |
| `create_validation_image.py` | Draw bounding boxes on page image for verification | `python scripts/create_validation_image.py <page_num> <fields.json> <input_img> <output_img>` |
| `fill_fillable_fields.py` | Fill fillable PDF form fields | `python scripts/fill_fillable_fields.py <input.pdf> <values.json> <output.pdf>` |
| `fill_pdf_form_with_annotations.py` | Fill non-fillable PDF via text annotations | `python scripts/fill_pdf_form_with_annotations.py <input.pdf> <fields.json> <output.pdf>` |

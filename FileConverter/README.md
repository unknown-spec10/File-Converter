# FileConverter

Simple modular file-conversion CLI in Python with **intelligent PDF→DOCX conversion**.

## 🎯 Key Features

### Intelligent PDF→DOCX Conversion
The converter automatically detects PDF type and uses the best method:

| PDF Type | Detection | Conversion Method | Result |
|----------|-----------|-------------------|--------|
| **Text-based** | Extractable text exists | Direct conversion (pdf2docx) | Fast, preserves layout |
| **Image-based** (scanned) | No text layer | OCR extraction (pytesseract) | Searchable, editable text |
| **Hybrid** (mixed) | Mixed pages | Per-page detection | Best method per page |

### Auto-Detection Flow
1. **Analyze** each page to detect if it's text-based or image-based
2. **Choose** the optimal conversion method automatically
3. **Convert** with the best approach for quality

## Supported Conversions

### Document Conversions
- **PDF → DOCX** (Intelligent auto-detection)
  - `auto` (default): **Smart detection** - analyzes PDF and uses best method
  - `text`: Force pdf2docx (fast, for text-based PDFs)
  - `ocr`: Force OCR (for scanned/image-based PDFs)
  - `image`: Embed pages as images (exact visual match, not editable)
- **DOCX → PDF** (docx2pdf — Windows recommended)

### Image Conversions
- **JPG/PNG → PDF** (Pillow)
- **PDF → PNG images** (pdf2image + poppler)

### Data Conversions
- **CSV → XLSX** (pandas + openpyxl)

## Quick Start (Windows/PowerShell)

```powershell
# Create and activate virtual environment
python -m venv env
.\env\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Convert with default (auto) mode
python FileConverter\main.py "path\to\file.pdf" --to docx

# Convert with specific mode
python FileConverter\main.py "path\to\file.pdf" --to docx --mode ocr

# Specify output location
python FileConverter\main.py "path\to\file.pdf" --to docx -o "output.docx"
```

## PDF→DOCX Conversion Modes

| Mode | Best For | How It Works |
|------|----------|--------------|
| `auto` ⭐ | **All PDFs** (recommended) | Analyzes each page, uses pdf2docx for text pages and OCR for image pages |
| `text` | Digital PDFs with selectable text | Uses pdf2docx only (fast, preserves bullets/tables when possible) |
| `ocr` | Scanned documents, poor quality PDFs | OCR on all pages (slower, extracts text from images) |
| `image` | Need exact visual copy | Embeds pages as images (not editable but looks identical) |

### What Gets Preserved vs Lost

**✅ Usually Preserves Well:**
- Plain text and paragraphs
- Basic formatting (bold, italic)
- Simple tables
- Most images
- Page structure

**⚠️ May Need Manual Cleanup:**
- Bullet points (sometimes become plain text with • symbols)
- Complex tables (merged cells)
- Precise spacing and alignment
- Custom fonts
- Headers/footers

**💡 Pro Tip:** pdf2docx is very good but not perfect. For bulletpoints and complex formatting:
1. Try `auto` mode first (it's smart!)
2. Check the result in Word
3. If bullets are missing, manually fix them in Word (select text → click bullet button)
4. For exact visual copy, use `--mode image`

## System Requirements

### Required
- Python 3.8+
- All packages in `requirements.txt`

### Optional (for specific features)
- **Tesseract-OCR**: Required for `--mode ocr`
  - Windows: Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
  - Add to PATH after installation
- **Poppler**: Required for PDF→Image conversion
  - Windows: Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases)
  - Add to PATH after installation
- **Microsoft Word**: Improves DOCX→PDF quality on Windows

## Examples

```powershell
# Convert PDF with auto-detection (RECOMMENDED - smartest option)
python FileConverter\main.py "document.pdf" --to docx

# Force text-based conversion (faster for digital PDFs)
python FileConverter\main.py "report.pdf" --to docx --mode text

# Force OCR for scanned documents
python FileConverter\main.py "scanned.pdf" --to docx --mode ocr

# Get exact visual copy (not editable)
python FileConverter\main.py "certificate.pdf" --to docx --mode image

# Convert DOCX to PDF
python FileConverter\main.py "document.docx" --to pdf

# Convert image to PDF
python FileConverter\main.py "photo.jpg" --to pdf

# Convert CSV to Excel
python FileConverter\main.py "data.csv" --to xlsx

# Specify output location
python FileConverter\main.py "file.pdf" --to docx -o "output\converted.docx"
```

## Architecture

```
FileConverter/
├── main.py              # CLI entry point with routing
├── converters/          # Conversion modules (one per type)
│   ├── pdf_to_docx.py   # Intelligent hybrid PDF→DOCX
│   ├── docx_to_pdf.py   # DOCX→PDF
│   ├── img_to_pdf.py    # Image→PDF
│   ├── pdf_to_img.py    # PDF→Images
│   └── csv_to_excel.py  # CSV→XLSX
├── utils/               # Shared utilities
│   ├── file_utils.py    # File operations
│   └── logger.py        # Logging setup
└── requirements.txt     # Python dependencies
```

## Design Philosophy

- **Modular**: Each converter is a separate module with a `convert(input, output)` function
- **Intelligent**: PDF→DOCX uses multiple strategies for best results
- **Extensible**: Add new converters by creating a module and adding to routing map
- **User-friendly**: Clear error messages and automatic dependency detection

## Next Steps

- Add tests (pytest)
- Build GUI (Streamlit or Tkinter)
- Package as standalone .exe (PyInstaller)
- Add more converters:
  - TXT ↔ PDF
  - Markdown ↔ HTML
  - Audio/Video (ffmpeg-based)

## Troubleshooting

**"Tesseract-OCR not found"**
- Install Tesseract and add to PATH, or set `pytesseract.pytesseract.tesseract_cmd` in code

**"pdf2image requires poppler"**
- Install poppler and add to PATH

**"docx2pdf not available"**
- On non-Windows systems, consider using LibreOffice: `libreoffice --headless --convert-to pdf file.docx`

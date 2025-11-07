# 🔄 Universal File Converter

AI-powered file conversion tool with support for multiple formats. Deploy on Streamlit Cloud or run locally.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Groq](https://img.shields.io/badge/Groq-AI-FF6B00?style=for-the-badge)](https://groq.com/)

## ✨ Features

- **🤖 AI-Powered**: Uses Groq LLM for intelligent document reconstruction
- **📄 PDF Conversion**: Multiple modes (text, OCR, AI-enhanced hybrid)
- **📊 Office Formats**: DOCX, XLSX, PPTX, ODT, ODS, ODP
- **🖼️ Image Processing**: JPG, PNG to PDF conversion
- **🎯 Auto-Detection**: Automatically selects best conversion method
- **🔒 Privacy-Aware**: Built-in sensitive data detection

## 🚀 Quick Start

### Option 1: Streamlit Cloud (Recommended)

1. Fork this repository
2. Deploy on [Streamlit Cloud](https://share.streamlit.io)
3. Set `GROQ_API_KEY` in Secrets
4. Done! 🎉

See **[DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md)** for detailed steps.

### Option 2: Local Installation

```bash
# Clone repository
git clone <your-repo-url>
cd "File Converter"

# Create virtual environment
python -m venv env
.\env\Scripts\Activate.ps1  # Windows
# source env/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up environment
copy .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run Streamlit app
cd FileConverter
streamlit run streamlit_app.py
```

## 🎯 Supported Conversions

| From | To | Method |
|------|----|----|
| PDF | DOCX | Text, OCR, AI-hybrid |
| DOCX | PDF | LibreOffice |
| CSV | XLSX | Python |
| JPG/PNG | PDF | PIL |
| DOC/XLS/PPT | PDF/DOCX/XLSX | LibreOffice |
| ODT/ODS/ODP | PDF/DOCX/XLSX | LibreOffice |

## 🔧 Conversion Modes

### PDF → DOCX

- **`auto`**: Automatically detect best method
- **`text`**: Enhanced layout detection (fast, good for text PDFs)
- **`ocr`**: Tesseract OCR (for scanned documents)
- **`hybrid`**: ⭐ PyMuPDF + Groq AI (BEST quality)
- **`groq`**: Pure AI reconstruction
- **`image`**: Embed as images

### DOCX → PDF

- **`auto`**: LibreOffice with fallback to docx2pdf
- **`libreoffice`**: High-quality conversion (requires LibreOffice)
- **`docx2pdf`**: Python library (Windows only)

## 📋 Usage

### Web Interface (Streamlit)

1. Upload your file
2. Select target format
3. Click "Convert"
4. Download result

### Command Line

```bash
cd FileConverter

# Basic conversion
python main.py input.pdf output.docx

# With specific mode
python main.py input.pdf output.docx -m hybrid

# DOCX to PDF
python main.py input.docx output.pdf

# Show all supported conversions
python main.py --list
```

## 🛠️ Technologies

- **Streamlit**: Web interface
- **Groq AI**: llama-3.3-70b-versatile for document reconstruction
- **PyMuPDF**: High-accuracy PDF parsing
- **pdfplumber**: Layout extraction
- **python-docx**: DOCX creation
- **LibreOffice**: Office format conversions
- **Tesseract**: OCR processing

## 📦 Requirements

### System Packages (for Streamlit Cloud)
- LibreOffice
- Tesseract OCR
- Poppler utils

### Python Packages
- streamlit
- groq
- pymupdf
- pdfplumber
- python-docx
- pdf2docx
- pytesseract
- pdf2image
- pillow
- openpyxl
- pandas

See [`requirements.txt`](requirements.txt) for complete list.

## 🔑 API Keys

This app requires a Groq API key for AI-powered conversions.

**Get your free API key**: [console.groq.com](https://console.groq.com)

### Local Setup
Add to `.env`:
```env
GROQ_API_KEY=gsk_your_key_here
```

### Streamlit Cloud
Add to app Secrets:
```toml
GROQ_API_KEY = "gsk_your_key_here"
```

## 📊 Performance

| Conversion Type | Processing Time |
|----------------|-----------------|
| Text-based PDF | 1-5 seconds |
| AI-enhanced (hybrid) | 10-30 seconds |
| OCR (per page) | 3-10 seconds |
| Office formats | 2-10 seconds |

## 🔒 Privacy

- Privacy checker scans for sensitive data (emails, SSNs, etc.)
- Files are deleted after conversion
- No data retention
- API calls are logged for audit

## 📝 Project Structure

```
File Converter/
├── FileConverter/              # Main application
│   ├── streamlit_app.py       # Web UI
│   ├── main.py                # CLI interface
│   ├── converter.py           # Universal converter
│   ├── converters/            # Conversion modules
│   │   ├── pdf_to_docx.py
│   │   ├── docx_to_pdf.py
│   │   ├── img_to_pdf.py
│   │   └── ...
│   └── utils/                 # Utilities
│       ├── groq_service.py
│       ├── layout_extractor.py
│       ├── privacy.py
│       └── ...
├── requirements.txt           # Python dependencies
├── packages.txt              # System packages
├── runtime.txt               # Python version
└── .streamlit/              # Streamlit config
```

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - feel free to use for personal or commercial projects.

## 🐛 Issues

Found a bug? Please open an issue on GitHub.

## 🙏 Acknowledgments

- Groq for the amazing AI API
- Streamlit for the excellent web framework
- LibreOffice for office format support
- All the open-source libraries that make this possible

---

**Made with ❤️ and AI** | Deploy on Streamlit Cloud in minutes!

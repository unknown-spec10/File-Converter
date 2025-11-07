"""Convert DOCX → PDF using multiple methods for best accuracy.

Methods (in priority order):
1. LibreOffice (headless) - Best accuracy, cross-platform
2. docx2pdf - Windows native, good for simple documents
3. Fallback error if neither available

LibreOffice provides superior formatting preservation for:
- Complex layouts and tables
- Fonts and styling
- Headers/footers
- Images and charts
- Multi-column layouts
"""
import os
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Try to import docx2pdf (Windows native method)
try:
    from docx2pdf import convert as _docx2pdf_convert
except Exception:
    _docx2pdf_convert = None

# Try to import LibreOffice converter
try:
    from utils.libreoffice_converter import LibreOfficeConverter, is_libreoffice_available
    _libreoffice_available = is_libreoffice_available()
except Exception:
    _libreoffice_available = False


def convert(input_path: str, output_path: str, method: str = 'auto') -> str:
    """Convert DOCX to PDF with best available method.
    
    Args:
        input_path: Path to input DOCX file
        output_path: Path to output PDF file
        method: Conversion method ('auto', 'libreoffice', 'docx2pdf')
    
    Returns:
        Path to output PDF file
    
    Raises:
        RuntimeError: If no conversion method is available
    """
    if method == 'auto':
        # Auto-select best available method
        if _libreoffice_available:
            method = 'libreoffice'
        elif _docx2pdf_convert:
            method = 'docx2pdf'
        else:
            raise RuntimeError(
                'No DOCX to PDF converter available. Please install:\n'
                '  Option 1 (Recommended): LibreOffice - https://www.libreoffice.org/\n'
                '  Option 2 (Windows): pip install docx2pdf'
            )
    
    # Convert using selected method
    if method == 'libreoffice':
        if not _libreoffice_available:
            raise RuntimeError('LibreOffice not available')
        logger.info('Converting DOCX to PDF using LibreOffice (high accuracy)...')
        converter = LibreOfficeConverter()
        result = converter.convert(input_path, output_path, 'pdf')
        logger.info(f'✓ LibreOffice conversion complete: {result}')
        return result
        
    elif method == 'docx2pdf':
        if not _docx2pdf_convert:
            raise RuntimeError('docx2pdf not available')
        logger.info('Converting DOCX to PDF using docx2pdf...')
        _docx2pdf_convert(input_path, output_path)
        logger.info(f'✓ docx2pdf conversion complete: {output_path}')
        return output_path
        
    else:
        raise ValueError(f'Unknown conversion method: {method}')

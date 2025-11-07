"""Universal document converter using LibreOffice.

Supports a wide range of office document formats with high accuracy:
- Word documents (DOC, DOCX, ODT, RTF)
- Excel spreadsheets (XLS, XLSX, ODS, CSV)
- PowerPoint presentations (PPT, PPTX, ODP)
- HTML, TXT, and more

All conversions maintain formatting, styles, and layout integrity.
"""
import os
from typing import Optional
from utils.libreoffice_converter import LibreOfficeConverter
from utils.logger import setup_logger

logger = setup_logger(__name__)


def convert(
    input_path: str,
    output_path: str,
    output_format: Optional[str] = None,
    timeout: int = 120
) -> str:
    """Convert any supported document format using LibreOffice.
    
    Args:
        input_path: Path to input document
        output_path: Path to output document
        output_format: Target format (e.g., 'pdf', 'docx'). Auto-detected if None.
        timeout: Conversion timeout in seconds (default: 120)
    
    Returns:
        Path to the converted file
        
    Examples:
        # Convert Word to PDF
        convert('report.docx', 'report.pdf')
        
        # Convert Excel to PDF
        convert('data.xlsx', 'data.pdf')
        
        # Convert PowerPoint to PDF
        convert('slides.pptx', 'slides.pdf')
        
        # Convert HTML to DOCX
        convert('page.html', 'document.docx')
    """
    logger.info(f'🔄 Universal conversion: {os.path.basename(input_path)} → {output_format or "auto"}')
    
    try:
        # Check if LibreOffice is available
        from utils.libreoffice_converter import is_libreoffice_available
        
        if not is_libreoffice_available():
            error_msg = (
                "LibreOffice is not available. Office format conversions require LibreOffice.\n"
                "For Streamlit Cloud deployment:\n"
                "  1. Create a 'packages.txt' file in your repo root\n"
                "  2. Add these lines:\n"
                "     libreoffice\n"
                "     libreoffice-writer\n"
                "     libreoffice-calc\n"
                "     libreoffice-impress\n"
                "  3. Redeploy your app\n"
                "\n"
                "For local installation:\n"
                "  Windows: https://www.libreoffice.org/download/\n"
                "  Linux: sudo apt install libreoffice\n"
                "  macOS: brew install --cask libreoffice"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        converter = LibreOfficeConverter()
        
        # Log detected LibreOffice installation
        logger.info(f'Using LibreOffice: {converter.soffice_path}')
        
        # Perform conversion
        result_path = converter.convert(
            input_path=input_path,
            output_path=output_path,
            output_format=output_format,
            timeout=timeout
        )
        
        # Log success with file size
        file_size = os.path.getsize(result_path)
        size_str = f'{file_size / 1024:.1f} KB' if file_size < 1024 * 1024 else f'{file_size / (1024 * 1024):.1f} MB'
        logger.info(f'✓ Conversion complete: {result_path} ({size_str})')
        
        return result_path
        
    except Exception as e:
        logger.error(f'✗ Conversion failed: {str(e)}')
        raise


def get_supported_formats() -> dict:
    """Get all supported format conversions.
    
    Returns:
        Dictionary mapping input formats to output formats.
    """
    try:
        converter = LibreOfficeConverter()
        return converter.get_supported_formats()
    except RuntimeError:
        return {}


def is_format_supported(input_format: str, output_format: str) -> bool:
    """Check if a specific conversion is supported.
    
    Args:
        input_format: Input format (e.g., 'docx')
        output_format: Output format (e.g., 'pdf')
    
    Returns:
        True if conversion is supported
    """
    formats = get_supported_formats()
    input_format = input_format.lower().lstrip('.')
    output_format = output_format.lower().lstrip('.')
    
    return output_format in formats.get(input_format, [])

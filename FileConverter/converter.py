"""Universal File Converter - Single entry point for all conversions.

Auto-detects source format from file extension and routes to appropriate
conversion logic. Supports all conversion paths with intelligent mode selection.

Supported conversions:
- PDF → DOCX (modes: auto, text, ocr, image, groq, hybrid, libreoffice)
- DOCX → PDF (methods: auto, libreoffice, docx2pdf)
- Image (JPG/PNG) → PDF (modes: basic, ai)
- PDF → Image (PNG)
- CSV → Excel (modes: basic, ai)
- Universal office formats via LibreOffice (DOC, XLS, PPT, ODT, ODS, ODP, HTML, TXT → PDF/DOCX/XLSX)

Usage:
    from converter import convert
    convert('input.pdf', 'output.docx')  # Auto-detects PDF→DOCX
    convert('input.pdf', 'output.docx', mode='hybrid')  # Use hybrid AI mode
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from utils.logger import setup_logger
from utils.file_utils import get_extension

logger = setup_logger(__name__)


# Conversion routing map: (source_ext, target_ext) -> (module_path, function_name, param_name)
CONVERSION_ROUTES = {
    # PDF conversions
    ('.pdf', '.docx'): ('converters.pdf_to_docx', 'convert', 'mode'),
    ('.pdf', '.png'): ('converters.pdf_to_img', 'convert', None),
    ('.pdf', '.jpg'): ('converters.pdf_to_img', 'convert', None),
    ('.pdf', '.jpeg'): ('converters.pdf_to_img', 'convert', None),
    
    # DOCX conversions
    ('.docx', '.pdf'): ('converters.docx_to_pdf', 'convert', 'method'),
    
    # Image conversions
    ('.jpg', '.pdf'): ('converters.img_to_pdf', 'convert', 'mode'),
    ('.jpeg', '.pdf'): ('converters.img_to_pdf', 'convert', 'mode'),
    ('.png', '.pdf'): ('converters.img_to_pdf', 'convert', 'mode'),
    
    # CSV conversions
    ('.csv', '.xlsx'): ('converters.csv_to_excel', 'convert', 'mode'),
    
    # Universal LibreOffice conversions (office formats to PDF/DOCX/XLSX)
    ('.doc', '.pdf'): ('converters.universal_converter', 'convert', None),
    ('.doc', '.docx'): ('converters.universal_converter', 'convert', None),
    ('.odt', '.pdf'): ('converters.universal_converter', 'convert', None),
    ('.odt', '.docx'): ('converters.universal_converter', 'convert', None),
    ('.rtf', '.pdf'): ('converters.universal_converter', 'convert', None),
    ('.rtf', '.docx'): ('converters.universal_converter', 'convert', None),
    ('.xls', '.pdf'): ('converters.universal_converter', 'convert', None),
    ('.xls', '.xlsx'): ('converters.universal_converter', 'convert', None),
    ('.xlsx', '.pdf'): ('converters.universal_converter', 'convert', None),
    ('.ods', '.pdf'): ('converters.universal_converter', 'convert', None),
    ('.ods', '.xlsx'): ('converters.universal_converter', 'convert', None),
    ('.ppt', '.pdf'): ('converters.universal_converter', 'convert', None),
    ('.ppt', '.pptx'): ('converters.universal_converter', 'convert', None),
    ('.pptx', '.pdf'): ('converters.universal_converter', 'convert', None),
    ('.odp', '.pdf'): ('converters.universal_converter', 'convert', None),
    ('.html', '.pdf'): ('converters.universal_converter', 'convert', None),
    ('.html', '.docx'): ('converters.universal_converter', 'convert', None),
    ('.txt', '.pdf'): ('converters.universal_converter', 'convert', None),
}


def get_supported_conversions() -> Dict[str, list]:
    """Get all supported source→target format combinations.
    
    Returns:
        Dict mapping source extensions to list of supported target extensions
    """
    conversions = {}
    for (source, target) in CONVERSION_ROUTES.keys():
        source = source.lstrip('.')
        target = target.lstrip('.')
        if source not in conversions:
            conversions[source] = []
        if target not in conversions[source]:
            conversions[source].append(target)
    return conversions


def is_conversion_supported(source_ext: str, target_ext: str) -> bool:
    """Check if a conversion is supported.
    
    Args:
        source_ext: Source file extension (with or without dot)
        target_ext: Target file extension (with or without dot)
    
    Returns:
        True if conversion is supported
    """
    # Normalize extensions
    if not source_ext.startswith('.'):
        source_ext = '.' + source_ext
    if not target_ext.startswith('.'):
        target_ext = '.' + target_ext
    
    source_ext = source_ext.lower()
    target_ext = target_ext.lower()
    
    return (source_ext, target_ext) in CONVERSION_ROUTES


def convert(
    input_path: str,
    output_path: str,
    mode: Optional[str] = None,
    method: Optional[str] = None,
    **kwargs
) -> str:
    """Universal file converter with auto-detection.
    
    Automatically detects source and target formats from file extensions
    and routes to the appropriate conversion logic.
    
    Args:
        input_path: Path to input file
        output_path: Path to output file
        mode: Conversion mode (contextual to conversion type)
            - PDF→DOCX: 'auto', 'text', 'ocr', 'image', 'groq', 'hybrid', 'libreoffice'
            - Image→PDF: 'basic', 'ai'
            - CSV→Excel: 'basic', 'ai'
        method: Conversion method (for DOCX→PDF)
            - 'auto', 'libreoffice', 'docx2pdf'
        **kwargs: Additional parameters passed to converter
    
    Returns:
        Path to output file
        
    Raises:
        ValueError: If conversion is not supported
        FileNotFoundError: If input file doesn't exist
        
    Examples:
        # Simple conversions
        convert('report.pdf', 'report.docx')
        
        # With mode
        convert('report.pdf', 'report.docx', mode='hybrid')
        
        # DOCX to PDF with method
        convert('report.docx', 'report.pdf', method='libreoffice')
        
        # Image to PDF with AI
        convert('photo.jpg', 'photo.pdf', mode='ai')
    """
    # Validate input
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Detect formats
    source_ext = get_extension(input_file).lower()
    output_file = Path(output_path)
    target_ext = output_file.suffix.lower()
    
    if not target_ext:
        raise ValueError(f"Output path must have a file extension: {output_path}")
    
    # Check if conversion is supported
    conversion_key = (source_ext, target_ext)
    if conversion_key not in CONVERSION_ROUTES:
        raise ValueError(
            f"Conversion {source_ext} → {target_ext} is not supported.\n"
            f"Supported conversions: {_format_supported_conversions()}"
        )
    
    # Get converter details
    module_path, func_name, param_name = CONVERSION_ROUTES[conversion_key]
    
    # Log conversion info
    logger.info(f"🔄 Converting: {input_file.name} ({source_ext}) → {target_ext}")
    if mode:
        logger.info(f"   Mode: {mode}")
    if method:
        logger.info(f"   Method: {method}")
    
    # Lazy import the converter module
    try:
        import importlib
        module = importlib.import_module(module_path)
        converter_func = getattr(module, func_name)
    except Exception as e:
        logger.error(f"Failed to load converter module {module_path}: {e}")
        raise RuntimeError(f"Converter module error: {e}")
    
    # Prepare conversion arguments
    convert_args = {
        'input_path': str(input_path),
        'output_path': str(output_path)
    }
    
    # Add mode/method if supported by this converter
    if param_name == 'mode' and mode:
        convert_args['mode'] = mode
    elif param_name == 'method' and method:
        convert_args['method'] = method
    
    # Add any extra kwargs
    convert_args.update(kwargs)
    
    # Execute conversion
    try:
        result = converter_func(**convert_args)
        
        # Some converters return the output path, others don't
        output_result = result if isinstance(result, str) else str(output_path)
        
        # Verify output was created
        if not Path(output_result).exists():
            raise RuntimeError(f"Conversion completed but output file not found: {output_result}")
        
        # Log success with file size
        file_size = Path(output_result).stat().st_size
        size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.1f} MB"
        logger.info(f"✓ Conversion complete: {Path(output_result).name} ({size_str})")
        
        return output_result
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        raise


def _format_supported_conversions() -> str:
    """Format supported conversions as a readable string."""
    conversions = get_supported_conversions()
    lines = []
    for source, targets in sorted(conversions.items()):
        targets_str = ', '.join(sorted(targets))
        lines.append(f"  {source.upper()} → {targets_str.upper()}")
    return '\n' + '\n'.join(lines)


def get_available_modes(source_ext: str, target_ext: str) -> list:
    """Get available modes for a specific conversion.
    
    Args:
        source_ext: Source file extension
        target_ext: Target file extension
    
    Returns:
        List of available mode strings, or empty list if no modes
    """
    # Normalize extensions
    if not source_ext.startswith('.'):
        source_ext = '.' + source_ext
    if not target_ext.startswith('.'):
        target_ext = '.' + target_ext
    
    source_ext = source_ext.lower()
    target_ext = target_ext.lower()
    
    # Define modes per conversion type
    if source_ext == '.pdf' and target_ext == '.docx':
        return ['auto', 'text', 'ocr', 'image', 'groq', 'hybrid', 'libreoffice']
    elif source_ext == '.docx' and target_ext == '.pdf':
        return ['auto', 'libreoffice', 'docx2pdf']
    elif source_ext in ['.jpg', '.jpeg', '.png'] and target_ext == '.pdf':
        return ['basic', 'ai']
    elif source_ext == '.csv' and target_ext == '.xlsx':
        return ['basic', 'ai']
    else:
        return []


def get_default_mode(source_ext: str, target_ext: str) -> Optional[str]:
    """Get the default mode for a conversion.
    
    Args:
        source_ext: Source file extension
        target_ext: Target file extension
    
    Returns:
        Default mode string, or None
    """
    modes = get_available_modes(source_ext, target_ext)
    if not modes:
        return None
    
    # Return intelligent defaults
    if '.pdf' in source_ext and '.docx' in target_ext:
        return 'hybrid'  # Best quality for PDF→DOCX
    elif '.docx' in source_ext and '.pdf' in target_ext:
        return 'auto'  # Auto-select best method
    else:
        return modes[0]  # First mode as default


# Convenience functions for common conversions
def pdf_to_docx(input_path: str, output_path: str, mode: str = 'hybrid') -> str:
    """Convert PDF to DOCX."""
    return convert(input_path, output_path, mode=mode)


def docx_to_pdf(input_path: str, output_path: str, method: str = 'auto') -> str:
    """Convert DOCX to PDF."""
    return convert(input_path, output_path, method=method)


def image_to_pdf(input_path: str, output_path: str, mode: str = 'basic') -> str:
    """Convert image to PDF."""
    return convert(input_path, output_path, mode=mode)


def pdf_to_image(input_path: str, output_dir: str) -> str:
    """Convert PDF to images (one per page)."""
    return convert(input_path, output_dir)


def csv_to_excel(input_path: str, output_path: str, mode: str = 'basic') -> str:
    """Convert CSV to Excel."""
    return convert(input_path, output_path, mode=mode)


if __name__ == '__main__':
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s'
    )
    
    if len(sys.argv) < 3:
        print("Universal File Converter")
        print("\nUsage:")
        print("  python converter.py <input> <output> [mode/method]")
        print("\nExamples:")
        print("  python converter.py report.pdf report.docx")
        print("  python converter.py report.pdf report.docx hybrid")
        print("  python converter.py report.docx report.pdf libreoffice")
        print("  python converter.py photo.jpg photo.pdf ai")
        print("\nSupported conversions:")
        print(_format_supported_conversions())
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    mode_or_method = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        # Try as mode first, then method
        result = convert(input_file, output_file, mode=mode_or_method, method=mode_or_method)
        print(f"\n✓ Success: {result}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

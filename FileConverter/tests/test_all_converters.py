"""Comprehensive test suite for all file converters.

This test suite covers:
- PDF to DOCX (all modes: auto, text, ocr, image, groq)
- DOCX to PDF
- Image to PDF (basic and AI modes)
- PDF to Image
- CSV to Excel (basic and AI modes)

Replace mock paths with your actual test files.
"""
import sys
import os
import logging
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

from converters import pdf_to_docx, docx_to_pdf, img_to_pdf, pdf_to_img, csv_to_excel
from utils.logger import setup_logger

logger = setup_logger()


# ============================================================================
# MOCK FILE PATHS - REPLACE WITH YOUR ACTUAL TEST FILES
# ============================================================================

# Get the base directory (File Converter)
BASE_DIR = Path(__file__).parent.parent.parent

MOCK_FILES = {
    # Input files
    'pdf_input': str(BASE_DIR / 'FileConverter' / 'data' / 'Deep Podder - Copy.pdf'),
    'docx_input': str(BASE_DIR / 'FileConverter' / 'data' / 'test.docx'),
    'image_input': str(BASE_DIR / 'FileConverter' / 'data' / 'test.jpg'),
    'csv_input': str(BASE_DIR / 'FileConverter' / 'data' / 'test.csv'),

    # Output directory
    'output_dir': str(BASE_DIR / 'FileConverter' / 'data' / 'output'),
}


# ============================================================================
# TEST CONFIGURATION
# ============================================================================

class TestConfig:
    """Configuration for test execution."""
    
    # Which tests to run
    RUN_TESTS = {
        'pdf_to_docx': True,
        'docx_to_pdf': True,
        'img_to_pdf': True,
        'pdf_to_img': True,
        'csv_to_excel': True,
    }
    
    # Test modes for each converter
    PDF_TO_DOCX_MODES = ['auto', 'text', 'groq']  # Remove 'groq' if no API key
    IMG_TO_PDF_MODES = ['basic', 'ai']  # Remove 'ai' if no API key
    CSV_TO_EXCEL_MODES = ['basic', 'ai']  # Remove 'ai' if no API key
    
    # Skip privacy checks for testing (set to False for real tests)
    SKIP_PRIVACY_WARNINGS = True


# ============================================================================
# TEST UTILITIES
# ============================================================================

def setup_test_environment():
    """Set up test environment and output directory."""
    output_dir = Path(MOCK_FILES['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")
    
    # Set environment for testing
    if TestConfig.SKIP_PRIVACY_WARNINGS:
        import os
        os.environ['GROQ_ALLOW_SENSITIVE'] = 'true'


def check_file_exists(file_key: str) -> bool:
    """Check if a test file exists."""
    file_path = Path(MOCK_FILES[file_key])
    
    if not file_path.exists():
        logger.warning(f"Test file not found: {file_path}")
        logger.warning(f"Update MOCK_FILES['{file_key}'] with your test file path")
        return False
    
    return True


def get_output_path(input_key: str, output_ext: str, mode: str = '') -> Path:
    """Generate output file path."""
    input_path = Path(MOCK_FILES[input_key])
    output_dir = Path(MOCK_FILES['output_dir'])
    
    mode_suffix = f'_{mode}' if mode else ''
    output_name = f"{input_path.stem}{mode_suffix}.{output_ext}"
    
    return output_dir / output_name


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_pdf_to_docx():
    """Test PDF to DOCX conversion with all modes."""
    logger.info("\n" + "="*70)
    logger.info("TEST: PDF TO DOCX CONVERSION")
    logger.info("="*70)
    
    if not check_file_exists('pdf_input'):
        return False
    
    input_path = str(Path(MOCK_FILES['pdf_input']))
    results = []
    
    for mode in TestConfig.PDF_TO_DOCX_MODES:
        logger.info(f"\n--- Testing mode: {mode} ---")
        output_path = str(get_output_path('pdf_input', 'docx', mode))
        
        try:
            pdf_to_docx.convert(input_path, output_path, mode=mode)
            
            if Path(output_path).exists():
                file_size = Path(output_path).stat().st_size / 1024
                logger.info(f"✓ Success: {output_path} ({file_size:.1f} KB)")
                results.append((mode, True, file_size))
            else:
                logger.error(f"✗ Failed: Output file not created")
                results.append((mode, False, 0))
        
        except Exception as e:
            logger.error(f"✗ Error: {e}")
            results.append((mode, False, 0))
    
    # Summary
    logger.info(f"\n--- PDF to DOCX Summary ---")
    for mode, success, size in results:
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"  {mode:10s} - {status} ({size:.1f} KB)")
    
    return all(success for _, success, _ in results)


def test_docx_to_pdf():
    """Test DOCX to PDF conversion."""
    logger.info("\n" + "="*70)
    logger.info("TEST: DOCX TO PDF CONVERSION")
    logger.info("="*70)
    
    if not check_file_exists('docx_input'):
        return False
    
    input_path = str(Path(MOCK_FILES['docx_input']))
    output_path = str(get_output_path('docx_input', 'pdf'))
    
    try:
        docx_to_pdf.convert(input_path, output_path)
        
        if Path(output_path).exists():
            file_size = Path(output_path).stat().st_size / 1024
            logger.info(f"✓ Success: {output_path} ({file_size:.1f} KB)")
            return True
        else:
            logger.error(f"✗ Failed: Output file not created")
            return False
    
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return False


def test_img_to_pdf():
    """Test Image to PDF conversion with all modes."""
    logger.info("\n" + "="*70)
    logger.info("TEST: IMAGE TO PDF CONVERSION")
    logger.info("="*70)
    
    if not check_file_exists('image_input'):
        return False
    
    input_path = str(Path(MOCK_FILES['image_input']))
    results = []
    
    for mode in TestConfig.IMG_TO_PDF_MODES:
        logger.info(f"\n--- Testing mode: {mode} ---")
        output_path = str(get_output_path('image_input', 'pdf', mode))
        
        try:
            img_to_pdf.convert(input_path, output_path, mode=mode)
            
            if Path(output_path).exists():
                file_size = Path(output_path).stat().st_size / 1024
                logger.info(f"✓ Success: {output_path} ({file_size:.1f} KB)")
                results.append((mode, True, file_size))
            else:
                logger.error(f"✗ Failed: Output file not created")
                results.append((mode, False, 0))
        
        except Exception as e:
            logger.error(f"✗ Error: {e}")
            results.append((mode, False, 0))
    
    # Summary
    logger.info(f"\n--- Image to PDF Summary ---")
    for mode, success, size in results:
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"  {mode:10s} - {status} ({size:.1f} KB)")
    
    return all(success for _, success, _ in results)


def test_pdf_to_img():
    """Test PDF to Image conversion."""
    logger.info("\n" + "="*70)
    logger.info("TEST: PDF TO IMAGE CONVERSION")
    logger.info("="*70)
    
    if not check_file_exists('pdf_input'):
        return False
    
    input_path = str(Path(MOCK_FILES['pdf_input']))
    output_path = str(get_output_path('pdf_input', 'png'))
    
    try:
        pdf_to_img.convert(input_path, output_path)
        
        # Check if any output files were created
        output_dir = Path(output_path).parent
        output_pattern = Path(output_path).stem + '*'
        output_files = list(output_dir.glob(output_pattern))
        
        if output_files:
            total_size = sum(f.stat().st_size for f in output_files) / 1024
            logger.info(f"✓ Success: Created {len(output_files)} image(s) ({total_size:.1f} KB total)")
            for f in output_files:
                logger.info(f"  - {f.name}")
            return True
        else:
            logger.error(f"✗ Failed: No output files created")
            return False
    
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return False


def test_csv_to_excel():
    """Test CSV to Excel conversion with all modes."""
    logger.info("\n" + "="*70)
    logger.info("TEST: CSV TO EXCEL CONVERSION")
    logger.info("="*70)
    
    if not check_file_exists('csv_input'):
        return False
    
    input_path = str(Path(MOCK_FILES['csv_input']))
    results = []
    
    for mode in TestConfig.CSV_TO_EXCEL_MODES:
        logger.info(f"\n--- Testing mode: {mode} ---")
        output_path = str(get_output_path('csv_input', 'xlsx', mode))
        
        try:
            csv_to_excel.convert(input_path, output_path, mode=mode)
            
            if Path(output_path).exists():
                file_size = Path(output_path).stat().st_size / 1024
                logger.info(f"✓ Success: {output_path} ({file_size:.1f} KB)")
                results.append((mode, True, file_size))
            else:
                logger.error(f"✗ Failed: Output file not created")
                results.append((mode, False, 0))
        
        except Exception as e:
            logger.error(f"✗ Error: {e}")
            results.append((mode, False, 0))
    
    # Summary
    logger.info(f"\n--- CSV to Excel Summary ---")
    for mode, success, size in results:
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"  {mode:10s} - {status} ({size:.1f} KB)")
    
    return all(success for _, success, _ in results)


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all enabled tests."""
    logger.info("\n" + "="*70)
    logger.info("FILE CONVERTER - COMPREHENSIVE TEST SUITE")
    logger.info("="*70)
    
    setup_test_environment()
    
    results = {}
    
    # Run tests
    if TestConfig.RUN_TESTS['pdf_to_docx']:
        results['pdf_to_docx'] = test_pdf_to_docx()
    
    if TestConfig.RUN_TESTS['docx_to_pdf']:
        results['docx_to_pdf'] = test_docx_to_pdf()
    
    if TestConfig.RUN_TESTS['img_to_pdf']:
        results['img_to_pdf'] = test_img_to_pdf()
    
    if TestConfig.RUN_TESTS['pdf_to_img']:
        results['pdf_to_img'] = test_pdf_to_img()
    
    if TestConfig.RUN_TESTS['csv_to_excel']:
        results['csv_to_excel'] = test_csv_to_excel()
    
    # Final summary
    logger.info("\n" + "="*70)
    logger.info("FINAL TEST RESULTS")
    logger.info("="*70)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        logger.info(f"  {test_name:20s} - {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for p in results.values() if p)
    
    logger.info("")
    logger.info(f"Total: {passed_tests}/{total_tests} tests passed")
    logger.info("="*70)
    
    return all(results.values())


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s'
    )
    
    success = run_all_tests()
    sys.exit(0 if success else 1)

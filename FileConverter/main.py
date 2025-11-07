from pathlib import Path
import argparse
import sys

from utils.logger import setup_logger
from utils.file_utils import make_output_name, get_extension
from converter import convert, get_supported_conversions, get_available_modes

logger = setup_logger()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Universal File Converter - AI-Powered + LibreOffice',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.pdf output.docx
  %(prog)s input.pdf output.docx -m hybrid
  %(prog)s input.docx output.pdf --method libreoffice
  %(prog)s photo.jpg photo.pdf -m ai
        """
    )
    parser.add_argument('input', type=str, nargs='?', help='Input file path')
    parser.add_argument('output', type=str, nargs='?', help='Output file path (optional)')
    parser.add_argument('-t', '--to', type=str, help='Target format (e.g. docx, pdf, xlsx)')
    parser.add_argument('-m', '--mode', type=str,
                        help='Conversion mode (auto, text, ocr, groq, hybrid, basic, ai, etc.)')
    parser.add_argument('--method', type=str,
                        help='Conversion method (for DOCX→PDF: auto, libreoffice, docx2pdf)')
    parser.add_argument('--list', action='store_true',
                        help='List all supported conversions and exit')

    args = parser.parse_args(argv)
    
    # List supported conversions
    if args.list:
        conversions = get_supported_conversions()
        print("\nSupported Conversions:")
        print("=" * 50)
        for source in sorted(conversions.keys()):
            targets = ', '.join(sorted(conversions[source]))
            print(f"  {source.upper():8} → {targets.upper()}")
        print("=" * 50)
        return

    # Validate input is provided when not listing
    if not args.input:
        parser.error("the following arguments are required: input (unless using --list)")
    
    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(2)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    elif args.to:
        # Generate output path with target extension
        output_path = input_path.with_suffix(f'.{args.to}')
    else:
        logger.error("Please provide output path or target format with --to")
        logger.info("Example: %(prog)s input.pdf -t docx")
        sys.exit(2)

    # Show available modes if requested format combination exists
    source_ext = get_extension(input_path)
    target_ext = output_path.suffix
    available_modes = get_available_modes(source_ext, target_ext)
    
    if args.mode and available_modes and args.mode not in available_modes:
        logger.warning(f"Mode '{args.mode}' may not be available for {source_ext}→{target_ext}")
        logger.info(f"Available modes: {', '.join(available_modes)}")

    try:
        logger.info(f"Converting: {input_path.name} → {output_path.name}")
        
        # Use universal converter
        result = convert(
            str(input_path),
            str(output_path),
            mode=args.mode,
            method=args.method
        )
        
        logger.info(f"✓ Conversion complete: {result}")
        
    except Exception as e:
        logger.exception(f"Conversion failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

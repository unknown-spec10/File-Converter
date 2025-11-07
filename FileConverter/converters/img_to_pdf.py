"""Convert images to PDF with AI-enhanced layout optimization.

Modes:
- 'basic': Simple conversion (default, fast)
- 'ai': Intelligent layout optimization with page sizing and quality settings
"""
from PIL import Image
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def convert(input_path: str, output_path: str, mode: str = 'basic') -> None:
    """Convert image to PDF with optional AI enhancements.
    
    Args:
        input_path: Path to input image
        output_path: Path to output PDF
        mode: Conversion mode ('basic' or 'ai')
    """
    if mode == 'basic':
        _convert_basic(input_path, output_path)
    elif mode == 'ai':
        _convert_with_ai(input_path, output_path)
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'basic' or 'ai'.")


def _convert_basic(input_path: str, output_path: str) -> None:
    """Basic image to PDF conversion.
    
    Args:
        input_path: Path to input image
        output_path: Path to output PDF
    """
    logger.info(f"Converting image to PDF (basic mode)...")
    img = Image.open(input_path)
    
    # Convert RGBA to RGB for PDF
    if img.mode in ("RGBA", "LA"):
        img = img.convert("RGB")
    
    img.save(output_path, "PDF", resolution=100.0)
    logger.info(f"✓ Conversion complete: {output_path}")


def _convert_with_ai(input_path: str, output_path: str) -> None:
    """AI-enhanced image to PDF conversion with optimal settings.
    
    Args:
        input_path: Path to input image
        output_path: Path to output PDF
    """
    logger.info("🤖 Starting AI-enhanced image to PDF conversion...")
    
    try:
        from utils.groq_service import GroqDocumentReconstructor
        from utils.ai_prompts import IMG_TO_PDF_LAYOUT_SYSTEM
    except ImportError as e:
        logger.warning(f"AI mode unavailable: {e}")
        logger.info("Falling back to basic mode...")
        return _convert_basic(input_path, output_path)
    
    # Phase 1: Analyze image
    logger.info("📊 Phase 1: Analyzing image...")
    img = Image.open(input_path)
    
    metadata = {
        'format': img.format,
        'mode': img.mode,
        'size': img.size,
        'width': img.width,
        'height': img.height,
        'aspect_ratio': round(img.width / img.height, 2) if img.height > 0 else 1.0,
        'file_size_kb': round(Path(input_path).stat().st_size / 1024, 2)
    }
    
    logger.info(f"  Image: {metadata['width']}x{metadata['height']}, {metadata['format']}")
    
    # Phase 2: AI optimization
    logger.info("🧠 Phase 2: AI layout optimization...")
    
    try:
        groq = GroqDocumentReconstructor()
        
        prompt = f"""Analyze this image for optimal PDF conversion.

IMAGE METADATA:
{metadata}

Determine:
1. Best page size (A4, Letter, or Custom based on image aspect ratio)
2. Orientation (portrait/landscape)
3. Scaling strategy (fit to page, maintain original, etc.)
4. DPI/Resolution for quality
5. Compression level

Output JSON with conversion parameters."""
        
        response = groq.client.chat.completions.create(
            model=groq.config.model,
            messages=[
                {"role": "system", "content": IMG_TO_PDF_LAYOUT_SYSTEM},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1000
        )
        
        ai_output = response.choices[0].message.content or "{}"
        logger.info("✓ AI optimization complete")
        
        # Parse AI suggestions
        import json
        try:
            settings = json.loads(ai_output.strip().replace('```json', '').replace('```', ''))
        except:
            logger.warning("Could not parse AI output, using defaults")
            settings = {}
        
    except Exception as e:
        logger.warning(f"AI optimization failed: {e}, using defaults")
        settings = {}
    
    # Phase 3: Apply optimized conversion
    logger.info("📝 Phase 3: Converting with optimized settings...")
    
    # Get AI-recommended DPI or use default
    dpi = settings.get('dpi', 150)
    
    # Convert RGBA to RGB if needed
    if img.mode in ("RGBA", "LA"):
        img = img.convert("RGB")
    
    # Save with optimized settings
    img.save(output_path, "PDF", resolution=float(dpi), quality=95)
    
    logger.info(f"✓ AI-enhanced conversion complete: {output_path}")
    logger.info(f"  Settings: {dpi} DPI")


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print('Usage: python img_to_pdf.py input.jpg output.pdf [mode]')
        print('Modes: basic (default), ai')
        sys.exit(2)
    
    inp = sys.argv[1]
    out = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else 'basic'
    
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    convert(inp, out, mode=mode)


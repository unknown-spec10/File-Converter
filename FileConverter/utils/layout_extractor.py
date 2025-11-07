"""Advanced layout extraction from PDFs.

This module extracts detailed layout information including:
- Text blocks with coordinates (x0, y0, x1, y1)
- Font names and sizes
- Indentation levels
- Line spacing and alignment
- Bullet/list detection markers

Output format is structured JSON ready for AI processing.
"""
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

logger = logging.getLogger(__name__)


# Common bullet markers
BULLET_MARKERS = {
    '•', '◦', '▪', '▫', '◾', '◽', '○', '●', 
    '-', '*', '→', '►', '‣', '⦿', '⦾', '▸'
}

# Numbered list patterns
NUMBERED_PATTERNS = [
    re.compile(r'^(\d+[\.\)])\s+'),           # 1. or 1)
    re.compile(r'^\(([a-z])\)\s+'),           # (a)
    re.compile(r'^\(([ivx]+)\)\s+'),          # (i), (ii), (iii)
    re.compile(r'^([a-z][\.\)])\s+'),         # a. or a)
    re.compile(r'^([A-Z][\.\)])\s+'),         # A. or A)
]


class LayoutExtractor:
    """Extract structured layout data from PDFs."""
    
    def __init__(self, pdf_path: str):
        """Initialize extractor with PDF path.
        
        Args:
            pdf_path: Path to PDF file
        """
        if not pdfplumber:
            raise RuntimeError(
                "pdfplumber is required for layout extraction. "
                "Install with: pip install pdfplumber"
            )
        
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        logger.info(f"Initializing layout extractor for: {self.pdf_path.name}")
    
    def extract(self) -> Dict[str, Any]:
        """Extract complete layout structure from PDF.
        
        Returns:
            Dict containing:
                - metadata: PDF metadata
                - total_pages: number of pages
                - pages: list of page data with blocks
        """
        if not pdfplumber:
            raise RuntimeError("pdfplumber is not available")
        
        logger.info("Extracting PDF layout...")
        
        layout_data = {
            "metadata": self._extract_metadata(),
            "total_pages": 0,
            "pages": []
        }
        
        with pdfplumber.open(str(self.pdf_path)) as pdf:
            layout_data["total_pages"] = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages, start=1):
                logger.info(f"  Extracting page {page_num}/{len(pdf.pages)}...")
                
                page_data = self._extract_page(page, page_num)
                layout_data["pages"].append(page_data)
        
        logger.info(f"✓ Layout extraction complete: {layout_data['total_pages']} pages")
        
        return layout_data
    
    def _extract_metadata(self) -> Dict[str, Any]:
        """Extract PDF metadata."""
        metadata = {
            "filename": self.pdf_path.name,
            "file_size_mb": round(self.pdf_path.stat().st_size / (1024 * 1024), 2),
            "title": None,
            "author": None,
            "creator": None,
            "producer": None
        }
        
        # Try to get metadata using PyPDF2
        if PdfReader:
            try:
                with open(self.pdf_path, 'rb') as f:
                    reader = PdfReader(f)
                    if reader.metadata:
                        metadata["title"] = reader.metadata.get("/Title")
                        metadata["author"] = reader.metadata.get("/Author")
                        metadata["creator"] = reader.metadata.get("/Creator")
                        metadata["producer"] = reader.metadata.get("/Producer")
            except Exception as e:
                logger.debug(f"Could not extract metadata: {e}")
        
        return metadata
    
    def _extract_page(self, page: Any, page_num: int) -> Dict[str, Any]:
        """Extract layout data from a single page.
        
        Args:
            page: pdfplumber page object
            page_num: Page number (1-indexed)
        
        Returns:
            Dict with page layout data
        """
        page_data = {
            "page": page_num,
            "width": page.width,
            "height": page.height,
            "blocks": []
        }
        
        # Extract words with positioning
        words = page.extract_words(
            x_tolerance=3,
            y_tolerance=3,
            keep_blank_chars=False,
            use_text_flow=True,
            extra_attrs=["fontname", "size"]
        )
        
        if not words:
            logger.debug(f"  Page {page_num}: No text found")
            return page_data
        
        # Group words into lines
        lines = self._group_words_into_lines(words)
        
        # Convert lines to blocks with rich metadata
        for line_data in lines:
            block = self._create_block_from_line(line_data)
            page_data["blocks"].append(block)
        
        logger.debug(f"  Page {page_num}: Extracted {len(page_data['blocks'])} blocks")
        
        return page_data
    
    def _group_words_into_lines(self, words: List[Dict]) -> List[Dict]:
        """Group words into lines based on Y coordinates.
        
        Args:
            words: List of word dicts from pdfplumber
        
        Returns:
            List of line dicts with grouped words
        """
        if not words:
            return []
        
        # Sort words by y (top), then x (left)
        sorted_words = sorted(words, key=lambda w: (round(w['top'], 1), w['x0']))
        
        lines = []
        current_line = []
        current_y = None
        y_tolerance = 3  # pixels
        
        for word in sorted_words:
            word_y = round(word['top'], 1)
            
            # New line?
            if current_y is None or abs(word_y - current_y) > y_tolerance:
                if current_line:
                    lines.append(self._finalize_line(current_line))
                current_line = [word]
                current_y = word_y
            else:
                current_line.append(word)
        
        # Last line
        if current_line:
            lines.append(self._finalize_line(current_line))
        
        return lines
    
    def _finalize_line(self, words: List[Dict]) -> Dict[str, Any]:
        """Combine words into a line with metadata.
        
        Args:
            words: List of word dicts on the same line
        
        Returns:
            Line dict with combined text and metadata
        """
        if not words:
            return {
                "text": "",
                "x0": 0,
                "y0": 0,
                "x1": 0,
                "y1": 0,
                "font": "unknown",
                "size": 0,
                "words": []
            }
        
        # Sort words left to right
        words = sorted(words, key=lambda w: w['x0'])
        
        # Combine text with proper spacing
        text_parts = []
        for i, word in enumerate(words):
            text_parts.append(word['text'])
            
            # Add space if next word is not immediately adjacent
            if i < len(words) - 1:
                next_word = words[i + 1]
                gap = next_word['x0'] - word['x1']
                if gap > 2:  # More than 2 pixels gap
                    text_parts.append(' ')
        
        text = ''.join(text_parts).strip()
        
        # Get dominant font and size
        font_counts = {}
        size_sum = 0
        
        for word in words:
            font = word.get('fontname', 'unknown')
            font_counts[font] = font_counts.get(font, 0) + 1
            size_sum += word.get('size', 0)
        
        dominant_font = max(font_counts.items(), key=lambda x: x[1])[0] if font_counts else 'unknown'
        avg_size = size_sum / len(words) if words else 0
        
        return {
            "text": text,
            "x0": words[0]['x0'],
            "y0": words[0]['top'],
            "x1": words[-1]['x1'],
            "y1": words[-1]['bottom'],
            "font": dominant_font,
            "size": round(avg_size, 1),
            "words": [w['text'] for w in words]
        }
    
    def _create_block_from_line(self, line_data: Dict) -> Dict[str, Any]:
        """Create a rich block structure from a line.
        
        Args:
            line_data: Line dict from _finalize_line
        
        Returns:
            Block dict with all metadata for AI processing
        """
        text = line_data['text']
        
        # Detect list markers
        list_type = None
        list_marker = None
        clean_text = text
        
        # Check for bullet
        if text and text[0] in BULLET_MARKERS:
            list_type = 'bullet'
            list_marker = text[0]
            clean_text = text[1:].lstrip()
        else:
            # Check for numbered list
            for pattern in NUMBERED_PATTERNS:
                match = pattern.match(text)
                if match:
                    list_type = 'numbered'
                    list_marker = match.group(1)
                    clean_text = text[match.end():].lstrip()
                    break
        
        # Calculate indentation level (rough estimate)
        indent_level = self._calculate_indent_level(line_data['x0'])
        
        # Detect potential heading (larger font, bold, short text)
        is_potential_heading = self._detect_potential_heading(
            clean_text,
            line_data['font'],
            line_data['size']
        )
        
        block = {
            "text": text,
            "clean_text": clean_text,
            "x0": round(line_data['x0'], 2),
            "y0": round(line_data['y0'], 2),
            "x1": round(line_data['x1'], 2),
            "y1": round(line_data['y1'], 2),
            "font": line_data['font'],
            "size": line_data['size'],
            "indent_level": indent_level,
            "list_type": list_type,
            "list_marker": list_marker,
            "is_potential_heading": is_potential_heading,
            "char_count": len(clean_text),
            "word_count": len(line_data['words'])
        }
        
        return block
    
    def _calculate_indent_level(self, x0: float) -> int:
        """Calculate indentation level from x coordinate.
        
        Args:
            x0: Left x coordinate
        
        Returns:
            Indent level (0 = no indent, 1+ = indented)
        """
        # Common left margins: 72 points = 1 inch
        # Indents are typically in increments of 18-36 points
        
        base_margin = 72  # Standard 1-inch margin
        indent_size = 25  # Roughly 0.35 inches per indent level
        
        if x0 < base_margin:
            return 0
        
        indent_pixels = x0 - base_margin
        indent_level = max(0, int(indent_pixels / indent_size))
        
        return min(indent_level, 5)  # Cap at 5 levels
    
    def _detect_potential_heading(self, text: str, font: str, size: float) -> bool:
        """Detect if text might be a heading.
        
        Args:
            text: Text content
            font: Font name
            size: Font size
        
        Returns:
            True if likely a heading
        """
        # Criteria for heading detection:
        # 1. Larger font size (typically 14+ for headings)
        # 2. Bold font
        # 3. Shorter text (headings are usually < 100 chars)
        # 4. No ending punctuation (headings rarely end with periods)
        
        is_large = size >= 14
        is_bold = 'bold' in font.lower() or 'black' in font.lower()
        is_short = len(text) < 100
        no_period = not text.endswith('.')
        
        # At least 2 of the 4 criteria
        criteria_met = sum([is_large, is_bold, is_short, no_period])
        
        return criteria_met >= 2


def extract_layout_to_json(pdf_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Extract layout and optionally save to JSON file.
    
    Args:
        pdf_path: Path to PDF file
        output_path: Optional path to save JSON. If None, returns data only.
    
    Returns:
        Layout data dict
    """
    extractor = LayoutExtractor(pdf_path)
    layout_data = extractor.extract()
    
    if output_path:
        import json
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(layout_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Layout data saved to: {output_file}")
    
    return layout_data


if __name__ == "__main__":
    import sys
    import json
    
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s'
    )
    
    if len(sys.argv) < 2:
        print("Usage: python layout_extractor.py input.pdf [output.json]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        data = extract_layout_to_json(pdf_path, output_path)
        
        if not output_path:
            # Print summary
            print(json.dumps(data, indent=2))
    
    except Exception as e:
        logger.exception(f"Layout extraction failed: {e}")
        sys.exit(1)

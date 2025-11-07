"""LibreOffice-based document conversion utility.

This module provides high-accuracy document conversions using LibreOffice's
headless mode. It supports various formats with better formatting preservation
than many Python libraries.

Requirements:
    - LibreOffice must be installed on the system
    - Common paths are auto-detected for Windows, Linux, and macOS

Supported conversions:
    - DOCX/DOC → PDF (with excellent formatting preservation)
    - XLSX/XLS → PDF
    - PPTX/PPT → PDF
    - ODT/ODS/ODP → PDF
    - And many more office formats

Usage:
    converter = LibreOfficeConverter()
    converter.convert('input.docx', 'output.pdf')
"""

import os
import subprocess
import platform
import shutil
from typing import Optional, List
from pathlib import Path


class LibreOfficeConverter:
    """High-accuracy document converter using LibreOffice."""
    
    # Common LibreOffice installation paths
    LIBREOFFICE_PATHS = {
        'Windows': [
            r'C:\Program Files\LibreOffice\program\soffice.exe',
            r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
            r'C:\Program Files\LibreOffice 7\program\soffice.exe',
            r'C:\Program Files\LibreOffice 24\program\soffice.exe',
        ],
        'Linux': [
            '/usr/bin/soffice',
            '/usr/bin/libreoffice',
            '/snap/bin/libreoffice',
            '/usr/local/bin/soffice',
        ],
        'Darwin': [  # macOS
            '/Applications/LibreOffice.app/Contents/MacOS/soffice',
            '/usr/local/bin/soffice',
        ]
    }
    
    def __init__(self, soffice_path: Optional[str] = None):
        """Initialize LibreOffice converter.
        
        Args:
            soffice_path: Path to soffice executable. If None, auto-detect.
        """
        self.soffice_path = soffice_path or self._find_libreoffice()
        if not self.soffice_path:
            raise RuntimeError(
                'LibreOffice not found. Please install LibreOffice:\n'
                '  Windows: https://www.libreoffice.org/download/download/\n'
                '  Linux: sudo apt install libreoffice\n'
                '  macOS: brew install --cask libreoffice'
            )
    
    def _find_libreoffice(self) -> Optional[str]:
        """Auto-detect LibreOffice installation.
        
        Returns:
            Path to soffice executable, or None if not found.
        """
        system = platform.system()
        
        # Try system-wide command first
        if shutil.which('soffice'):
            return shutil.which('soffice')
        if shutil.which('libreoffice'):
            return shutil.which('libreoffice')
        
        # Check common installation paths
        paths = self.LIBREOFFICE_PATHS.get(system, [])
        for path in paths:
            if os.path.isfile(path):
                return path
        
        return None
    
    def is_available(self) -> bool:
        """Check if LibreOffice is available.
        
        Returns:
            True if LibreOffice is installed and accessible.
        """
        return self.soffice_path is not None
    
    def convert(
        self,
        input_path: str,
        output_path: str,
        output_format: Optional[str] = None,
        timeout: int = 120
    ) -> str:
        """Convert document using LibreOffice.
        
        Args:
            input_path: Path to input document
            output_path: Path to output document (can be directory or file)
            output_format: Output format (e.g., 'pdf', 'docx'). Auto-detected if None.
            timeout: Timeout in seconds (default: 120)
        
        Returns:
            Path to the created output file
            
        Raises:
            RuntimeError: If conversion fails
            TimeoutError: If conversion exceeds timeout
        """
        input_path = os.path.abspath(input_path)
        
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f'Input file not found: {input_path}')
        
        # Determine output directory and format
        if os.path.isdir(output_path):
            output_dir = output_path
            if not output_format:
                raise ValueError('output_format required when output_path is a directory')
        else:
            output_dir = os.path.dirname(output_path) or '.'
            if not output_format:
                output_format = os.path.splitext(output_path)[1].lstrip('.')
        
        # Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)
        
        # Build LibreOffice command
        # --headless: Run without GUI
        # --convert-to: Specify output format
        # --outdir: Output directory
        cmd = [
            self.soffice_path,
            '--headless',
            '--convert-to', output_format.lower(),
            '--outdir', output_dir,
            input_path
        ]
        
        try:
            # Run conversion
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or 'Unknown error'
                raise RuntimeError(f'LibreOffice conversion failed: {error_msg}')
            
            # LibreOffice creates output with same name but different extension
            input_basename = os.path.splitext(os.path.basename(input_path))[0]
            expected_output = os.path.join(output_dir, f'{input_basename}.{output_format}')
            
            if not os.path.isfile(expected_output):
                raise RuntimeError(f'Output file not created: {expected_output}')
            
            # If user specified exact output path, rename if needed
            if not os.path.isdir(output_path) and expected_output != os.path.abspath(output_path):
                final_path = os.path.abspath(output_path)
                if os.path.exists(final_path):
                    os.remove(final_path)
                os.rename(expected_output, final_path)
                return final_path
            
            return expected_output
            
        except subprocess.TimeoutExpired:
            raise TimeoutError(f'LibreOffice conversion timed out after {timeout} seconds')
        except Exception as e:
            raise RuntimeError(f'LibreOffice conversion error: {str(e)}')
    
    def get_supported_formats(self) -> dict:
        """Get supported input/output format combinations.
        
        Returns:
            Dictionary mapping input formats to supported output formats.
        """
        return {
            'docx': ['pdf', 'odt', 'html', 'txt', 'rtf'],
            'doc': ['pdf', 'docx', 'odt', 'html', 'txt', 'rtf'],
            'xlsx': ['pdf', 'ods', 'csv', 'html'],
            'xls': ['pdf', 'xlsx', 'ods', 'csv', 'html'],
            'pptx': ['pdf', 'odp', 'html'],
            'ppt': ['pdf', 'pptx', 'odp', 'html'],
            'odt': ['pdf', 'docx', 'html', 'txt', 'rtf'],
            'ods': ['pdf', 'xlsx', 'csv', 'html'],
            'odp': ['pdf', 'pptx', 'html'],
            'rtf': ['pdf', 'docx', 'odt', 'html', 'txt'],
            'txt': ['pdf', 'docx', 'odt', 'html'],
            'html': ['pdf', 'docx', 'odt'],
            'csv': ['pdf', 'xlsx', 'ods'],
        }
    
    def batch_convert(
        self,
        input_files: List[str],
        output_dir: str,
        output_format: str,
        timeout: int = 120
    ) -> List[str]:
        """Convert multiple files in batch.
        
        Args:
            input_files: List of input file paths
            output_dir: Output directory
            output_format: Output format (e.g., 'pdf')
            timeout: Timeout per file in seconds
        
        Returns:
            List of created output file paths
        """
        os.makedirs(output_dir, exist_ok=True)
        output_files = []
        
        for input_file in input_files:
            try:
                output_file = self.convert(
                    input_file,
                    output_dir,
                    output_format,
                    timeout
                )
                output_files.append(output_file)
            except Exception as e:
                print(f'Failed to convert {input_file}: {e}')
                continue
        
        return output_files


def get_converter() -> Optional[LibreOfficeConverter]:
    """Get LibreOffice converter instance if available.
    
    Returns:
        LibreOfficeConverter instance, or None if LibreOffice not available.
    """
    try:
        return LibreOfficeConverter()
    except RuntimeError:
        return None


def is_libreoffice_available() -> bool:
    """Check if LibreOffice is available on the system.
    
    Returns:
        True if LibreOffice is installed and accessible.
    """
    converter = get_converter()
    return converter is not None


# Example usage
if __name__ == '__main__':
    converter = LibreOfficeConverter()
    print(f'LibreOffice found at: {converter.soffice_path}')
    print(f'\nSupported formats:')
    for input_fmt, output_fmts in converter.get_supported_formats().items():
        print(f'  {input_fmt.upper()} → {", ".join(output_fmts).upper()}')

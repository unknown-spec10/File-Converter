"""Convert PDF pages to images.

This uses pdf2image which requires poppler to be installed on the system.
On Windows, install poppler and set PATH or provide poppler_path to convert_from_path.
"""
import os
from pdf2image import convert_from_path


def convert(input_path: str, output_dir_or_file: str) -> None:
    # If target looks like a file path (has an extension), use its directory
    # Otherwise treat it as a directory path
    if os.path.splitext(output_dir_or_file)[1]:  # Has extension like .png
        output_dir = os.path.dirname(output_dir_or_file)
        if not output_dir:
            output_dir = '.'
    else:
        output_dir = output_dir_or_file
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    pages = convert_from_path(input_path)
    base = os.path.splitext(os.path.basename(input_path))[0]
    for i, page in enumerate(pages, start=1):
        out_path = os.path.join(output_dir, f"{base}_page_{i}.png")
        page.save(out_path, 'PNG')

"""Streamlit interface for Universal File Converter."""
import os
import sys
from pathlib import Path
import streamlit as st

# Add FileConverter to path for imports
sys.path.insert(0, str(Path(__file__).parent / "FileConverter"))

# Import universal converter
from FileConverter.converter import convert, get_supported_conversions
from FileConverter.utils.file_utils import get_extension

st.set_page_config(page_title="File Converter", layout="centered", page_icon="🔄")

# Header
st.title("🔄 File Converter")
st.write("Upload a file and select target format")

# Main content
uploaded = st.file_uploader("Upload file", type=list(get_supported_conversions().keys()))

if not uploaded:
    st.stop()

# File uploaded - process it
work_dir = Path("FileConverter/tmp_uploads")
work_dir.mkdir(parents=True, exist_ok=True)

input_path = work_dir / uploaded.name
with open(input_path, "wb") as f:
    f.write(uploaded.getbuffer())

source_ext = get_extension(input_path).lstrip('.')

# Get available target formats
available_targets = get_supported_conversions().get(source_ext, [])

if not available_targets:
    st.error(f"No conversions available for {source_ext.upper()} files")
    st.stop()

# Target format selection
target_format = st.selectbox("Target format", available_targets)

# Convert button
if st.button("Convert", type="primary", use_container_width=True):
    output_filename = f"{input_path.stem}_converted.{target_format}"
    output_path = work_dir / output_filename
    
    with st.spinner("Converting..."):
        try:
            result_path = convert(str(input_path), str(output_path))
            
            st.success("✓ Conversion complete!")
            
            # Download button
            with open(result_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download",
                    data=f.read(),
                    file_name=Path(result_path).name,
                    mime="application/octet-stream",
                    type="primary",
                    use_container_width=True
                )
            
        except Exception as e:
            st.error(f"❌ Conversion failed: {str(e)}")

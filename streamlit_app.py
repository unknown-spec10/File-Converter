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

# Initialize session state
if 'converted_file' not in st.session_state:  # type: ignore
    st.session_state.converted_file = None  # type: ignore
if 'converted_filename' not in st.session_state:  # type: ignore
    st.session_state.converted_filename = None  # type: ignore

# Header
st.title("🔄 File Converter")
st.write("Upload a file and select target format")

# Main content
uploaded = st.file_uploader("Upload file", type=list(get_supported_conversions().keys()))

if not uploaded:
    # Reset session state when no file
    st.session_state.converted_file = None  # type: ignore
    st.session_state.converted_filename = None  # type: ignore
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
            
            # Verify the output file exists
            result_file = Path(result_path)
            
            if not result_file.exists():
                st.error(f"❌ Output file not found: {result_path}")
                st.stop()
            
            # Read the file and store in session state
            with open(result_file, "rb") as f:
                st.session_state.converted_file = f.read()  # type: ignore
                st.session_state.converted_filename = result_file.name  # type: ignore
            
            st.success("✓ Conversion complete!")
            
        except Exception as e:
            st.error(f"❌ Conversion failed: {str(e)}")
            st.session_state.converted_file = None  # type: ignore
            st.session_state.converted_filename = None  # type: ignore

# Show download button if conversion was successful
if st.session_state.converted_file is not None:  # type: ignore
    st.download_button(
        label="⬇️ Download",
        data=st.session_state.converted_file,  # type: ignore
        file_name=st.session_state.converted_filename,  # type: ignore
        mime="application/octet-stream",
        type="primary",
        use_container_width=True
    )

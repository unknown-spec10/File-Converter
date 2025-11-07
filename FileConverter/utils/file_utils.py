from pathlib import Path


def get_extension(path: Path) -> str:
    return Path(path).suffix.lower()


def make_output_name(input_path: Path, target_ext: str, output_path: Path | None) -> Path:
    """Return a Path for the output.

    If output_path is provided and is a directory, use it; if it's a file, return as-is.
    If not provided, create a file next to input with new extension.
    target_ext: e.g. 'pdf' or 'docx' or 'img' or 'xlsx'
    """
    if output_path:
        out = Path(output_path)
        if out.is_dir():
            return out / (input_path.stem + '.' + target_ext)
        else:
            return out
    else:
        return input_path.with_suffix('.' + target_ext)

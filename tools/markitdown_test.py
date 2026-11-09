"""
https://github.com/microsoft/markitdown

Convert a file, or every supported file in a folder, to markdown with MarkItDown.
Converted .md files are written to a `data/` folder (defaults to tools/data/).

Usage:
    # Convert a single file
    uv run markitdown_test.py path/to/file.pdf

    # Convert every allowed file (see ALLOWED_EXTENSIONS) found anywhere under a folder
    uv run markitdown_test.py path/to/folder

    # Restrict a folder scan to specific extensions
    uv run markitdown_test.py path/to/folder --ext pdf xlsx csv

    # Write output somewhere other than tools/data/
    uv run markitdown_test.py path/to/file.docx --output-dir path/to/output

Examples:
    uv run markitdown_test.py ../openai_related/openai_rag_pdf/nodejs.pdf
    uv run markitdown_test.py ../openai_related --ext pdf xlsx
"""

import argparse
from pathlib import Path
from markitdown import MarkItDown
from markitdown._stream_info import StreamInfo

DATA_DIR = Path(__file__).parent / "data"

# Extensions MarkItDown knows how to convert that we'll pick up when scanning a folder.
ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".pptx", ".xlsx", ".xls", ".csv",
    ".html", ".htm", ".txt", ".md",
}


def convert_to_markdown(source, output_dir=DATA_DIR, output_name=None, charset="utf-8"):
    """
    Convert a file (pdf, docx, pptx, xlsx, csv, html, image, audio, etc.) or a URL
    to markdown using MarkItDown, and save the result to output_dir.

    Args:
        source: local file path (str/Path) or a http(s)/file/data URL (str).
        output_dir: folder to save the converted .md file into (created if missing).
        output_name: optional filename (without extension) for the saved .md file.
                     Defaults to the source's stem (or "output" for URLs without one).
        charset: text encoding hint for text-based formats (csv/html/txt). MarkItDown
                 otherwise falls back to ascii on Windows, which breaks on non-ascii
                 content (accents, curly quotes, etc.).

    Returns: the Path of the saved .md file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    md = MarkItDown(enable_plugins=False)
    result = md.convert(str(source), stream_info=StreamInfo(charset=charset))

    if output_name is None:
        output_name = Path(str(source).split("?")[0]).stem or "output"

    output_path = output_dir / f"{output_name}.md"
    output_path.write_text(result.text_content, encoding="utf-8")
    print(f"Converted {source} -> {output_path}")
    return output_path


def convert_path(input_path, output_dir=DATA_DIR, allowed_extensions=ALLOWED_EXTENSIONS):
    """
    Convert a single file, or every allowed file in a folder, to markdown.

    Args:
        input_path: path to a file, or a folder to scan for allowed_extensions.
        output_dir: folder to save the converted .md file(s) into.
        allowed_extensions: extensions (e.g. {".pdf", ".csv"}) to pick up when
                             input_path is a folder. Ignored for a single file.

    Returns: list of Path objects for each converted .md file.
    """
    input_path = Path(input_path)

    if input_path.is_file():
        return [convert_to_markdown(input_path, output_dir=output_dir)]

    if input_path.is_dir():
        files = sorted(
            p for p in input_path.rglob("*")
            if p.is_file() and p.suffix.lower() in allowed_extensions
        )
        if not files:
            print(f"No files with extensions {sorted(allowed_extensions)} found in {input_path}")
            return []

        converted = []
        for file in files:
            try:
                converted.append(convert_to_markdown(file, output_dir=output_dir))
            except Exception as e:
                print(f"Skipping {file} ({e})")
        return converted

    raise FileNotFoundError(f"No such file or folder: {input_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert file(s) to markdown using MarkItDown.")
    parser.add_argument("path", help="File or folder to convert.")
    parser.add_argument("--ext", nargs="+", help="Allowed extensions when path is a folder, e.g. --ext .pdf .csv")
    parser.add_argument("--output-dir", default=str(DATA_DIR), help="Folder to save converted .md files into.")
    args = parser.parse_args()

    allowed = {e if e.startswith(".") else f".{e}" for e in args.ext} if args.ext else ALLOWED_EXTENSIONS
    convert_path(args.path, output_dir=args.output_dir, allowed_extensions=allowed)

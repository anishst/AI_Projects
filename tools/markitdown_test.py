# https://github.com/microsoft/markitdown

from pathlib import Path
from markitdown import MarkItDown
from markitdown._stream_info import StreamInfo

DATA_DIR = Path(__file__).parent / "data"


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


if __name__ == "__main__":
    # A few different input formats already available in this repo, to exercise
    # MarkItDown's different converters (PDF, Excel, CSV, plain markdown/text).
    sample_sources = [
        Path(__file__).parent.parent / "openai_related" / "openai_rag_pdf" / "nodejs.pdf",
        Path(__file__).parent.parent / "openai_related" / "openai_rag_excel" / "data" / "Test Manager Plan.xlsx",
        Path(__file__).parent.parent / "ollama_related" / "data" / "restaurant_reviews.csv",
        Path(__file__).parent.parent / "ollama_related" / "docs" / "sample.md",
    ]

    for source in sample_sources:
        if source.exists():
            convert_to_markdown(source)
        else:
            print(f"Skipping missing sample file: {source}")

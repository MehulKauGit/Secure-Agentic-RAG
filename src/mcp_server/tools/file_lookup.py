from pathlib import Path

# Sandboxed document root directory
BASE_DOC_DIR = Path(__file__).resolve().parents[3] / "corpus" / "documents"


def file_lookup(filename: str) -> str:
    """Reads the text content of a file within the sandboxed documents directory."""
    # Prevent directory traversal attacks outside of corpus/documents
    target_path = (BASE_DOC_DIR / filename).resolve()
    try:
        target_path.relative_to(BASE_DOC_DIR.resolve())
    except ValueError:
        return f"Error: Access denied. '{filename}' is outside the sandboxed documents folder."

    if not target_path.exists() or not target_path.is_file():
        return f"Error: File '{filename}' not found."

    try:
        return target_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file '{filename}': {str(e)}"

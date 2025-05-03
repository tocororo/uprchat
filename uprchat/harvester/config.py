from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PDF_DIR = BASE_DIR / "repositories" / "pdfs"
DOC_DIR = BASE_DIR / "repositories" / "docs"
PPT_DIR = BASE_DIR / "repositories" / "ppts"

for directory in [PDF_DIR, DOC_DIR, PPT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

"""文档解析：把不同格式的文件统一抽取为纯文本。"""
from pathlib import Path

SUPPORTED_SUFFIXES = {".pdf", ".txt", ".md", ".docx"}


def load_file(path: str | Path) -> str:
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        import fitz  # PyMuPDF

        doc = fitz.open(path)
        try:
            return "\n".join(page.get_text() for page in doc)
        finally:
            doc.close()

    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")

    if suffix == ".docx":
        import docx  # python-docx

        document = docx.Document(path)
        return "\n".join(p.text for p in document.paragraphs)

    raise ValueError(f"暂不支持的文件类型: {suffix}（支持 {sorted(SUPPORTED_SUFFIXES)}）")

"""离线数据流水线：解析 -> 切片 -> 向量化 -> 写入 Milvus -> 登记元数据。"""
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings
from app.db.metadata import add_document
from app.ingestion.loader import load_file
from app.retrieval.vector_store import get_vectorstore


def ingest_file(doc_id: str, saved_path: str | Path, filename: str) -> dict:
    s = get_settings()

    # 1) 解析
    text = load_file(saved_path)
    if not text or not text.strip():
        raise ValueError("未从文档中解析到文本（扫描件/图片型 PDF 需要先接入 OCR）")

    # 2) 切片（中文友好的分隔符顺序）
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=s.chunk_size,
        chunk_overlap=s.chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""],
    )
    pieces = [p for p in splitter.split_text(text) if p.strip()]

    # 3) 构造带元数据的 Document（doc_id 用于后续按文档删除 / 权限过滤）
    documents = [
        Document(
            page_content=piece,
            metadata={"doc_id": doc_id, "source": filename, "chunk_index": i},
        )
        for i, piece in enumerate(pieces)
    ]

    # 4) Embedding 并写入 Milvus（首次写入自动建集合，维度由模型推断）
    vs = get_vectorstore()
    vs.add_documents(documents)

    # 5) 登记文档元数据
    add_document(doc_id, filename, len(documents))

    return {"id": doc_id, "filename": filename, "chunk_count": len(documents)}


def delete_by_doc_id(doc_id: str) -> None:
    """按 doc_id 删除 Milvus 中该文档的全部切片。"""
    vs = get_vectorstore()
    if getattr(vs, "col", None) is not None:
        vs.delete(expr=f"doc_id == '{doc_id}'")

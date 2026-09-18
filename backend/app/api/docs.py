"""文档管理接口：上传（触发离线入库流水线）、列表、删除。"""
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from app.db.metadata import delete_document, list_documents
from app.ingestion.loader import SUPPORTED_SUFFIXES
from app.ingestion.pipeline import delete_by_doc_id, ingest_file

router = APIRouter(prefix="/api/docs", tags=["docs"])

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "data" / "uploads"


@router.get("")
def get_docs():
    return list_documents()


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    filename = file.filename or "untitled"
    if Path(filename).suffix.lower() not in SUPPORTED_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=f"仅支持 {sorted(SUPPORTED_SUFFIXES)} 格式",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    doc_id = uuid.uuid4().hex
    saved_path = UPLOAD_DIR / f"{doc_id}_{filename}"
    saved_path.write_bytes(await file.read())

    try:
        # 解析/Embedding/入库为同步阻塞操作，放到线程池避免卡住事件循环
        result = await run_in_threadpool(ingest_file, doc_id, saved_path, filename)
    except Exception as e:  # 入库失败时清理已保存的原件
        saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"文档处理失败：{e}") from e

    return result


@router.delete("/{doc_id}")
async def delete_doc(doc_id: str):
    await run_in_threadpool(delete_by_doc_id, doc_id)
    delete_document(doc_id)
    for f in UPLOAD_DIR.glob(f"{doc_id}_*"):
        f.unlink(missing_ok=True)
    return {"ok": True}

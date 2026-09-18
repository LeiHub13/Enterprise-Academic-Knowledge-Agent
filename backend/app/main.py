"""FastAPI 入口。

启动：uvicorn app.main:app --reload --port 8000
文档：http://localhost:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymilvus import connections

from app.api import chat, docs as docs_api
from app.core.config import get_settings
from app.db.metadata import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Knowledge Agent API", version="0.1.0", lifespan=lifespan)

# 开发环境放开 CORS；生产环境应收敛为前端实际域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(docs_api.router)


@app.get("/api/health")
def health():
    """健康检查，同时探测 Milvus 连通性。"""
    s = get_settings()
    try:
        if not connections.has_connection("health"):
            connections.connect(alias="health", uri=s.milvus_uri)
        return {"status": "ok", "milvus": "connected", "uri": s.milvus_uri}
    except Exception as e:  # noqa: BLE001
        return {"status": "degraded", "milvus": f"unreachable: {e}"}

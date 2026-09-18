"""问答接口：POST /api/chat，以 SSE（Server-Sent Events）流式返回。

事件协议：
  event: sources  data: {"sources": [{index, source, snippet}, ...]}
  event: token    data: {"content": "增量文本"}
  event: done     data: {}
  event: error    data: {"message": "..."}
"""
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agent.chain import build_messages, get_llm
from app.core.config import get_settings
from app.retrieval.vector_store import get_vectorstore, is_collection_ready
from app.schemas.models import ChatRequest

router = APIRouter(prefix="/api", tags=["chat"])

_SSE_HEADERS = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/chat")
async def chat(req: ChatRequest):
    async def event_stream():
        try:
            # 1) 向量检索（知识库为空时返回空上下文，由 Prompt 兜底）
            docs = []
            vs = get_vectorstore()
            if is_collection_ready(vs):
                retriever = vs.as_retriever(
                    search_kwargs={"k": get_settings().retrieval_k}
                )
                docs = await retriever.ainvoke(req.question)

            # 2) 组装带引用的上下文
            messages, sources = build_messages(req.question, docs)
            yield _sse("sources", {"sources": sources})

            # 3) LLM 流式生成
            llm = get_llm()
            async for chunk in llm.astream(messages):
                content = getattr(chunk, "content", "")
                if content:
                    yield _sse("token", {"content": content})

            yield _sse("done", {})
        except Exception as e:  #  noqa: BLE001 - 流式响应中异常只能通过事件回传
            yield _sse("error", {"message": f"{type(e).__name__}: {e}"})

    return StreamingResponse(
        event_stream(), media_type="text/event-stream", headers=_SSE_HEADERS
    )

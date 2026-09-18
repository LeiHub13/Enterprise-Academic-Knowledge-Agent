"""RAG 问答链：检索结果组装上下文 + 引用约束 Prompt + LLM。

MVP 采用"手动检索 -> 拼上下文 -> LLM 流式生成"的方式，
引用来源可以作为独立 SSE 事件返回给前端，便于溯源与防幻觉。
后续要加工具调用 / 多轮规划时，可在此文件升级为 LangGraph Agent。
"""
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import get_settings

SYSTEM_PROMPT = """你是企业/高校知识库问答助手。请严格依据下方【参考资料】回答用户问题。

要求：
1. 只能使用参考资料中的信息，不得编造；资料不足以回答时，直接说明"根据现有知识库无法回答该问题"。
2. 在回答末尾另起一行，用"参考来源：[1][2]"的形式标注引用编号，编号与资料编号对应。
3. 使用中文回答，条理清晰，必要时分点说明。

【参考资料】
{context}
"""


def get_llm() -> ChatOpenAI:
    s = get_settings()
    return ChatOpenAI(
        base_url=s.llm_base_url,
        api_key=s.llm_api_key,
        model=s.llm_model,
        temperature=s.llm_temperature,
        streaming=True,
    )


def format_context(docs: list) -> tuple[str, list[dict]]:
    """把检索到的切片编号拼接为上下文，同时产出给前端的引用来源列表。"""
    blocks: list[str] = []
    sources: list[dict] = []
    for i, d in enumerate(docs, start=1):
        source = d.metadata.get("source", "未知")
        blocks.append(f"[{i}]（来源：{source}）\n{d.page_content}")
        sources.append(
            {"index": i, "source": source, "snippet": d.page_content[:200]}
        )
    return "\n\n".join(blocks), sources


def build_messages(question: str, docs: list):
    context, sources = format_context(docs)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(context=context or "（无）")),
        HumanMessage(content=question),
    ]
    return messages, sources

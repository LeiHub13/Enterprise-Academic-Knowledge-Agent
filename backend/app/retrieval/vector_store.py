"""Embedding 客户端与 Milvus 向量库单例。

集合维度在首次 add_documents 时由 Embedding 模型自动推断创建；
因此更换不同维度的 Embedding 模型时，需要更换 MILVUS_COLLECTION 或删除旧集合。
"""
from functools import lru_cache

from langchain_milvus import Milvus
from langchain_openai import OpenAIEmbeddings

from app.core.config import get_settings


@lru_cache
def get_embeddings() -> OpenAIEmbeddings:
    s = get_settings()
    return OpenAIEmbeddings(
        base_url=s.embedding_base_url,
        api_key=s.embedding_api_key,
        model=s.embedding_model,
        # 第三方 OpenAI 兼容接口不一定支持 tiktoken 的上下文长度校验，关闭以避免误报
        check_embedding_ctx_length=False,
    )


@lru_cache
def get_vectorstore() -> Milvus:
    s = get_settings()
    return Milvus(
        embedding_function=get_embeddings(),
        connection_args={"uri": s.milvus_uri},
        collection_name=s.milvus_collection,
        auto_id=True,
    )


def is_collection_ready(vs: Milvus) -> bool:
    """集合是否已存在（尚未上传任何文档时为 False）。"""
    return getattr(vs, "col", None) is not None

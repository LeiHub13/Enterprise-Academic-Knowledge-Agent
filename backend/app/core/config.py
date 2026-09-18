"""全局配置：从 backend/.env 读取（OpenAI 兼容接口地址、密钥、Milvus 地址等）。"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # LLM
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.3

    # Embedding
    embedding_base_url: str = "https://api.openai.com/v1"
    embedding_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"

    # Milvus
    milvus_uri: str = "http://localhost:19530"
    milvus_collection: str = "kb_chunks"

    # 切片 / 检索
    chunk_size: int = 500
    chunk_overlap: int = 80
    retrieval_k: int = 6


@lru_cache
def get_settings() -> Settings:
    return Settings()

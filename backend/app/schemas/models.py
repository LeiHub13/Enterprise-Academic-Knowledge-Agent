"""请求 / 响应数据模型。"""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")


class Source(BaseModel):
    index: int = Field(..., description="引用编号")
    source: str = Field(..., description="来源文件名")
    snippet: str = Field(..., description="命中片段节选")

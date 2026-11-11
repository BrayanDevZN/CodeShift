from pydantic import BaseModel, Field
from typing import Literal

class ModelConfig(BaseModel):

    name: Literal["qwen3-coder-next:80b", "qwen2.5-coder:14b", "qwen2.5-coder:7b"] = Field(default="qwen2.5-coder:14b")
    temperature: float = Field(default=0.5)

class AppConfig(BaseModel):

    model: ModelConfig
    path: str|None = Field(default=None)

    

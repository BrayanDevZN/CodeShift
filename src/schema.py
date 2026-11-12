from pydantic import BaseModel, Field
from typing import Literal

class ModelConfig(BaseModel):

    name: Literal[
        "Qwen/Qwen3-Coder-Next",
        "Qwen/Qwen2.5-Coder-14B-Instruct",
        "Qwen/Qwen2.5-Coder-7B-Instruct",
        "Qwen/Qwen2.5-Coder-3B-Instruct",
    ] = Field(default="Qwen/Qwen2.5-Coder-14B-Instruct")
    temperature: float = Field(default=0.5)

class AppConfig(BaseModel):

    model: ModelConfig
    path: str|None = Field(default=None)
    env_file: str|None = Field(default=None)


class ActionMapping(BaseModel):

    name: Literal["save", "quit", "read"]
    arg: str| None = Field(default=None)

class OutPutMapping(BaseModel):
    action: ActionMapping
    content: str

    

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

class ToolParameter(BaseModel):
    type: str
    description: str
    enum: Optional[List[str]] = None
    default: Optional[Any] = None

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str] = []

class GroqToolFunction(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class GroqTool(BaseModel):
    type: str = "function"
    function: GroqToolFunction

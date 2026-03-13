"""
Gemini client using direct REST API (AI Studio compatible).
Bypasses the SDK which adds problematic 'models/' prefixes.
"""

import json
import requests  # type: ignore
from typing import Any, Dict, List, Optional

from app.config import settings  # type: ignore
from app.utils.logger import get_logger  # type: ignore

logger = get_logger(__name__)


class GeminiClient:
    """Gemini LLM client using direct REST API for Google AI Studio keys."""
    
    def __init__(self, api_key: str, model: str):
        """Initialize Gemini client."""
        self.api_key = api_key
        
        # Aggressively clean model name
        model_str = str(model).strip()
        if model_str.lower().startswith("models/"):
            # Use replace to avoid slicing issues in some linting environments
            model_str = model_str.replace("models/", "", 1)
        
        if not model_str or "gemini" not in model_str.lower():
            model_str = "gemini-1.5-flash"
            
        self.model_name = model_str
        logger.info(f"✅ Gemini initialized (REST API) with model: '{self.model_name}'")

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> Dict[str, Any]:
        """Generate completion using Gemini direct REST API."""
        try:
            prompt = self._convert_messages(messages)
            
            # Prepare request payload
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                }
            }
            
            # For non-tool calls, v1 is most stable
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
            
            logger.info(f"🌐 Calling Gemini REST API (Generate/v1): gemini-1.5-flash")
            
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                params={"key": self.api_key},
                json=payload,
                timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS
            )
            
            if response.status_code != 200:
                error_msg = f"Gemini API returned {response.status_code}: {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            result = response.json()
            
            # Extract response text
            candidates = result.get("candidates", [])
            if not candidates or not candidates[0].get("content"):
                return {"success": False, "error": "No candidates content in Gemini response"}
            
            parts = candidates[0]["content"].get("parts", [])
            text_content = "".join([p.get("text", "") for p in parts])
            
            usage_metadata = result.get("usageMetadata", {})
            
            return {
                "success": True,
                "content": text_content,
                "answer": text_content,
                "model": "gemini-1.5-flash",
                "usage": {
                    "prompt_tokens": usage_metadata.get("promptTokenCount", 0),
                    "completion_tokens": usage_metadata.get("candidatesTokenCount", 0),
                    "total_tokens": usage_metadata.get("totalTokenCount", 0),
                }
            }
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return {"success": False, "error": str(e)}

    def generate_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> Dict[str, Any]:
        """Generate with tool calling using direct REST API."""
        try:
            prompt = self._convert_messages(messages)
            
            # Prepare standard payload
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                }
            }
            
            # Add tools if provided
            if tools:
                gemini_tools = self._convert_tools_to_dict(tools)
                if gemini_tools:
                    payload["tools"] = gemini_tools
            
            # STEP 1: Try v1beta WITH tools (Only v1beta supports function calling)
            url_beta = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            
            logger.info(f"🌐 Calling Gemini REST API (v1beta with tools): gemini-1.5-flash")
            
            response = requests.post(
                url_beta,
                headers={"Content-Type": "application/json"},
                params={"key": self.api_key},
                json=payload,
                timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS
            )
            
            logger.info(f"📊 v1beta Response status: {response.status_code}")
            
            # STEP 2: Fallback to v1 WITHOUT tools if v1beta fails (status 400 or 404)
            if response.status_code in [400, 404]:
                logger.warning(f"⚠️ v1beta failed ({response.status_code}), attempting v1 WITHOUT tools...")
                
                # Strip tools from payload
                payload_no_tools = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                    }
                }
                
                url_v1 = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
                
                response = requests.post(
                    url_v1,
                    headers={"Content-Type": "application/json"},
                    params={"key": self.api_key},
                    json=payload_no_tools,
                    timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS
                )
                
                logger.info(f"📊 v1 (no tools) Response status: {response.status_code}")
            
            if response.status_code != 200:
                error_msg = f"Gemini API returned {response.status_code}: {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            result = response.json()
            
            # Extract response
            candidates = result.get("candidates", [])
            if not candidates:
                return {"success": False, "error": "No candidates in Gemini response"}
            
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            
            text_content: str = ""
            tool_calls = []
            
            for part in parts:
                if "text" in part:
                    text_content = f"{text_content}{part['text']}"
                elif "functionCall" in part:
                    fc = part["functionCall"]
                    tool_calls.append({
                        "name": fc.get("name", ""),
                        "arguments": fc.get("args", {}),
                    })
            
            # Prepare result for orchestrator compatibility
            message_dict: Dict[str, Any] = {
                "role": "assistant",
                "content": text_content if not tool_calls else "",
            }
            if tool_calls:
                message_dict["tool_calls"] = [
                    {
                        "id": f"call_{i}",
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"])
                        }
                    }
                    for i, tc in enumerate(tool_calls)
                ]

            usage_metadata = result.get("usageMetadata", {})
            
            logger.info(f"✅ Gemini response: {len(text_content)} chars, {len(tool_calls)} tool calls")
            
            return {
                "success": True,
                "message": message_dict,
                "content": text_content if not tool_calls else "",
                "tool_calls": tool_calls,
                "tool_calls_made": tool_calls,
                "model": "gemini-1.5-flash",
                "usage": {
                    "prompt_tokens": usage_metadata.get("promptTokenCount", 0),
                    "completion_tokens": usage_metadata.get("candidatesTokenCount", 0),
                    "total_tokens": usage_metadata.get("totalTokenCount", 0),
                }
            }
            
        except Exception as e:
            logger.error(f"Gemini tool calling failed: {e}")
            return {"success": False, "error": str(e)}

    def _convert_messages(self, messages: List[Dict[str, str]]) -> str:
        """Standardize messages into a single prompt string for the REST content part."""
        parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                parts.append(f"**System Instructions:**\n{content}")
            elif role == "user":
                parts.append(f"**User Request:**\n{content}")
            elif role == "assistant":
                parts.append(f"**Assistant Response:**\n{content}")
        return "\n\n".join(parts)

    def _convert_tools_to_dict(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert OpenAI tool format to Gemini REST API tool format."""
        if not tools:
            return []
        
        function_declarations = []
        
        for tool in tools:
            if tool.get("type") == "function":
                func = tool["function"]
                params = self._sanitize_parameters(func.get("parameters", {}))
                
                func_decl = {
                    "name": func["name"],
                    "description": func.get("description", ""),
                    "parameters": {
                        "type": "object",
                        "properties": params.get("properties", {}),
                    }
                }
                
                if "required" in params:
                    # Explicitly update to avoid type checker confusion
                    func_decl["parameters"].update({"required": params["required"]})
                
                function_declarations.append(func_decl)
        
        return [{"functionDeclarations": function_declarations}] if function_declarations else []

    def _sanitize_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Strip features unsupported by Gemini (like non-string enums)."""
        sanitized = params.copy()
        if "properties" in sanitized:
            for name, schema in list(sanitized["properties"].items()):
                # Remove enum if not a string
                if "enum" in schema and schema.get("type") != "string":
                    logger.warning(f"Removing enum from {name}")
                    sanitized["properties"][name] = {k: v for k, v in schema.items() if k != "enum"}
                
                # Handle nested array items
                if schema.get("type") == "array" and "items" in schema:
                    items = schema["items"]
                    if "enum" in items and items.get("type") != "string":
                        logger.warning(f"Removing enum from {name}.items")
                        sanitized["properties"][name]["items"] = {k: v for k, v in items.items() if k != "enum"}
        return sanitized

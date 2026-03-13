
"""
LLM Fabric - Manages multiple LLM providers with automatic fallback.
"""

import time
import asyncio
from typing import Any, Dict, List, Optional

from app.config import settings
from app.generation.gemini_client import GeminiClient
from app.generation.llm_client import GroqClient
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMFabric:
    """
    Multi-provider LLM manager with automatic fallback.
    
    Priority: Groq (Primary) → Gemini (Fallback)
    """
    
    def __init__(self):
        """Initialize both LLM clients."""
        self.groq_client: Optional[GroqClient] = None
        self.gemini_client: Optional[GeminiClient] = None
        
        # Initialize Groq (Primary)
        try:
            self.groq_client = GroqClient(
                api_key=settings.GROQ_API_KEY,
                model=settings.GROQ_MODEL,
            )
            logger.info(f"✅ Groq initialized (Primary): {settings.GROQ_MODEL}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Groq: {e}")
        
        # Initialize Gemini (Fallback)
        try:
            self.gemini_client = GeminiClient(
                api_key=settings.GOOGLE_API_KEY,
                model=settings.GEMINI_MODEL,
            )
            logger.info(f"✅ Gemini initialized (Fallback): {settings.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")
        
        if not self.groq_client and not self.gemini_client:
            logger.critical("No LLM providers available!")
            # We don't raise RuntimeError here to allow the app to start but 
            # fallbacks will handle it during generation.

    def generate(
        self,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> Dict[str, Any]:
        """
        Generate response with automatic fallback.
        Supports both (system_prompt, user_prompt) and (messages) interfaces.
        """
        # Harmonize inputs
        if messages is None:
            if system_prompt and user_prompt:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            else:
                return {"success": False, "error": "Insufficient prompt data provided."}

        # Try Groq first
        if self.groq_client:
            try:
                logger.info("🔵 Attempting generation with Groq...")
                # GroqClient.generate expects system_prompt/user_prompt
                # If messages was provided, extract them
                target_system = next((m["content"] for m in messages if m["role"] == "system"), "")
                target_user = next((m["content"] for m in messages if m["role"] == "user"), messages[-1]["content"])

                result = self.groq_client.generate(
                    system_prompt=target_system,
                    user_prompt=target_user,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                if result.get("success"):
                    result["provider"] = "groq"
                    logger.info(f"✅ Groq succeeded: {result.get('model')}")
                    return result
                else:
                    logger.warning(f"⚠️ Groq returned failure: {result.get('error')}")
                    # Fall through to Gemini
                
            except Exception as e:
                error_msg = str(e).lower()
                if "rate_limit" in error_msg or "429" in error_msg:
                    logger.warning(f"⚠️ Groq rate limited: {e}")
                else:
                    logger.error(f"❌ Groq failed: {e}")
                logger.info("🔄 Falling back to Gemini...")
        
        # Fallback to Gemini
        if self.gemini_client:
            try:
                logger.info("🟢 Attempting generation with Gemini...")
                # GeminiClient.generate handles the messages list
                result = self.gemini_client.generate(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                if result.get("success"):
                    result["provider"] = "gemini"
                    logger.info(f"✅ Gemini succeeded: {result.get('model')}")
                    return result
                
            except Exception as e:
                logger.error(f"❌ Gemini also failed: {e}")
                return {"success": False, "error": f"All LLM providers failed. Last error: {e}"}
        
        return {"success": False, "error": "No LLM providers available for fallback"}

    async def generate_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """
        Generate with tool calling support and automatic fallback.
        Async for compatibility with ToolOrchestrator.
        """
        # Try Groq first
        if self.groq_client:
            try:
                logger.info("🔵 Attempting tool-calling with Groq...")
                result = await self.groq_client.generate_with_tools(
                    messages=messages,
                    tools=tools,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                if result.get("success"):
                    result["provider"] = "groq"
                    logger.info("✅ Groq tool-calling succeeded")
                    return result
                else:
                    error_msg = result.get("error", "").lower()
                    if "rate_limit" in error_msg or "429" in error_msg:
                        logger.warning(f"⚠️ Groq rate limited: {error_msg}")
                    else:
                        logger.warning(f"⚠️ Groq tool-calling failed: {error_msg}")
                    # Fall through to Gemini
                
            except Exception as e:
                logger.error(f"❌ Groq tool-calling crashed: {e}")
                logger.info("🔄 Falling back to Gemini for tool-calling...")
        
        # Fallback to Gemini
        if self.gemini_client:
            try:
                logger.info("🟢 Attempting tool-calling with Gemini...")
                result = self.gemini_client.generate_with_tools(
                    messages=messages,
                    tools=tools,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                if result.get("success"):
                    result["provider"] = "gemini"
                    logger.info("✅ Gemini tool-calling succeeded")
                    return result
                
            except Exception as e:
                logger.error(f"❌ Gemini tool-calling also failed: {e}")
                return {"success": False, "error": f"All tool-calling providers failed. Last error: {e}"}
        
        return {"success": False, "error": "No LLM providers available for tool-calling fallback"}
    
    def get_active_provider(self) -> str:
        """Get the currently active primary provider."""
        if self.groq_client:
            return "groq"
        elif self.gemini_client:
            return "gemini"
        return "none"

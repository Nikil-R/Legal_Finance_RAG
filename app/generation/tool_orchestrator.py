import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.generation.llm_client import GroqClient
from app.tools.registry import ToolRegistry
from app.tools.executor import ToolExecutor
from app.config import settings

logger = logging.getLogger(__name__)

class ToolOrchestrator:
    """Manages the multi-turn tool calling conversation loop."""
    
    def __init__(self, llm_client: GroqClient, registry: ToolRegistry, executor: ToolExecutor):
        self.llm_client = llm_client
        self.registry = registry
        self.executor = executor
        self.max_rounds = settings.TOOL_CALLING_MAX_ROUNDS if hasattr(settings, "TOOL_CALLING_MAX_ROUNDS") else 3

    async def process_with_tools(
        self,
        question: str,
        system_prompt: str,
        context_chunks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process a query with tool calling support.
        """
        start_time = time.perf_counter()
        
        # Build initial messages
        user_content = question
        if context_chunks:
            context_text = "\n\n".join([f"[{c['reference_id']}] {c['content']}" for c in context_chunks])
            user_content = f"CONTEXT:\n{context_text}\n\nQUESTION:\n{question}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        # Get tool definitions
        tool_definitions = self.registry.get_tool_definitions()
        
        tool_calls_made = []
        final_answer = ""
        iteration = 0
        total_tokens = 0
        prompt_tokens = 0
        completion_tokens = 0
        sources_from_tools = []

        while iteration < self.max_rounds:
            iteration += 1
            logger.info("Tool calling iteration %d/%d", iteration, self.max_rounds)
            
            # Call LLM with tools
            response = await self.llm_client.generate_with_tools(
                messages=messages,
                tools=tool_definitions
            )
            
            if not response.get("success", True):
                return response # Error from LLM client

            message = response["message"]
            messages.append(message)
            
            # Tracking usage
            usage = response.get("usage", {})
            prompt_tokens += usage.get("prompt_tokens", 0)
            completion_tokens += usage.get("completion_tokens", 0)
            total_tokens += usage.get("total_tokens", 0)

            # Check if LLM wants to call tools
            tool_calls = message.get("tool_calls")
            if not tool_calls:
                # No more tools, final answer reached
                final_answer = message.get("content", "")
                break
            
            # Execute tool calls
            for tool_call in tool_calls:
                tc_id = tool_call["id"]
                tc_name = tool_call["function"]["name"]
                tc_args = json.loads(tool_call["function"]["arguments"])
                
                tool_calls_made.append({"name": tc_name, "args": tc_args})
                
                # Execute tool
                execution_result = self.executor.execute(tc_name, tc_args)
                
                # If it's a document search, track sources
                if tc_name == "search_legal_documents" and execution_result.get("success"):
                    for res in execution_result["result"].get("results", []):
                        sources_from_tools.append(res)
                
                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc_id,
                    "content": json.dumps(execution_result)
                })

        duration_ms = (time.perf_counter() - start_time) * 1000
        
        return {
            "success": True,
            "answer": final_answer,
            "tool_calls_made": tool_calls_made,
            "sources": sources_from_tools,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            },
            "duration_ms": duration_ms,
            "iterations": iteration,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": response.get("model", "unknown")
        }

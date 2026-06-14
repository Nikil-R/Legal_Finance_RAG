import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from app.generation.gemini_client import GeminiClient
from app.tools.registry import ToolRegistry

async def test():
    client = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"), model="gemini-1.5-flash")
    registry = ToolRegistry()
    tools = registry.get_tool_definitions()
    
    messages = [
        {"role": "user", "content": "Calculate tax on ₹15,00,000 in the new regime for FY 2026-27"}
    ]
    
    res = client.generate_with_tools(messages=messages, tools=tools)
    print(res)

if __name__ == "__main__":
    asyncio.run(test())

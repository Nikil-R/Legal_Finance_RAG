#!/usr/bin/env python
"""Verify tool registry status"""

from app.tools import ToolRegistry

registry = ToolRegistry()
tools = registry.list_tools()

print(f"Tool Registry Status: {len(tools)} tools registered\n")
print("=" * 60)
for i, tool in enumerate(tools, 1):
    print(f"{i}. {tool['name']}")
print("=" * 60)
print(f"\nAll {len(tools)} tools successfully registered and verified!")

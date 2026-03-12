"""
Model Context Protocol (MCP) Server Wrapper for Legal Finance RAG Tools.

This module provides MCP server integration for tool calling capabilities,
enabling vendor-neutral tool execution compatible with Claude, GPT-4, and other LLMs.

Phase 1: Proof of Concept
- Wraps existing tool infrastructure in MCP protocol
- Maintains backward compatibility with current Groq integration
- Enables multi-model support through standardized interface
"""

import json
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# ============= MCP Protocol Models =============

@dataclass
class ToolMCPDefinition:
    """MCP Tool Definition Schema"""
    name: str
    description: str
    inputSchema: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class MCPToolCall:
    """MCP Tool Call Request"""
    name: str
    arguments: Dict[str, Any]

@dataclass
class MCPToolResult:
    """MCP Tool Result Response"""
    content: List[Dict[str, Any]]
    isError: bool = False


class MCPServer:
    """
    MCP Server implementation for legal finance RAG tools.
    
    Converts proprietary tool definitions to MCP format for vendor independence.
    """
    
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
        self.tools: Dict[str, ToolMCPDefinition] = {}
        self._convert_tools_to_mcp()
        
    def _convert_tools_to_mcp(self):
        """Convert Groq tool definitions to MCP format"""
        groq_definitions = self.tool_registry.get_tool_definitions()
        
        for groq_def in groq_definitions:
            tool_func = groq_def["function"]
            
            mcp_tool = ToolMCPDefinition(
                name=tool_func["name"],
                description=tool_func["description"],
                inputSchema={
                    "type": "object",
                    "properties": tool_func["parameters"]["properties"],
                    "required": tool_func["parameters"]["required"]
                }
            )
            
            self.tools[tool_func["name"]] = mcp_tool
            logger.info(f"Registered MCP tool: {tool_func['name']}")
    
    def list_tools(self) -> List[Dict]:
        """List all available MCP tools"""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """
        Execute a tool call through MCP interface.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            MCPToolResult with execution result
        """
        try:
            if tool_name not in self.tools:
                raise ValueError(f"Tool '{tool_name}' not found")
            
            # Get the actual tool function from registry
            func = self.tool_registry.get_tool_function(tool_name)
            
            # Execute tool
            result = func(**arguments)
            
            # Convert result to MCP format
            return MCPToolResult(
                content=[{
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }],
                isError=not result.get("success", False)
            )
            
        except Exception as e:
            logger.exception(f"Error calling MCP tool {tool_name}")
            return MCPToolResult(
                content=[{
                    "type": "text",
                    "text": json.dumps({
                        "success": False,
                        "error": str(e)
                    })
                }],
                isError=True
            )


class MCPClient:
    """
    MCP Client for LLM integration.
    
    Allows LLMs to discover tools and make tool calls through MCP protocol.
    """
    
    def __init__(self, mcp_server: MCPServer):
        self.server = mcp_server
        self.tool_cache: Dict[str, ToolMCPDefinition] = {}
        
    def discover_tools(self) -> List[Dict]:
        """Discover all available tools"""
        tools = self.server.list_tools()
        self.tool_cache = {t["name"]: ToolMCPDefinition(**t) for t in tools}
        return tools
    
    def validate_tool_call(self, tool_call: MCPToolCall) -> bool:
        """Validate tool call against schema"""
        if tool_call.name not in self.server.tools:
            return False
        
        tool_def = self.server.tools[tool_call.name]
        required_params = tool_def.inputSchema.get("required", [])
        
        # Check all required parameters are provided
        for param in required_params:
            if param not in tool_call.arguments:
                return False
        
        return True
    
    def execute_tool_call(self, tool_call: MCPToolCall) -> MCPToolResult:
        """Execute a tool call"""
        if not self.validate_tool_call(tool_call):
            return MCPToolResult(
                content=[{
                    "type": "text",
                    "text": "Invalid tool call: missing required parameters"
                }],
                isError=True
            )
        
        return self.server.call_tool(tool_call.name, tool_call.arguments)


class HybridToolExecutor:
    """
    Hybrid executor supporting both native and MCP tool execution.
    
    Allows gradual migration from Groq-specific tools to MCP format.
    Feature flags enable switching execution paths per tool.
    """
    
    def __init__(self, tool_registry, mcp_server: Optional[MCPServer] = None):
        self.tool_registry = tool_registry
        self.mcp_server = mcp_server
        self.mcp_enabled_tools: set = set()  # Tools using MCP execution
        self.native_tools: set = set()       # Tools using native execution
        
        # Initialize native tools (original 5 tools)
        self.native_tools.update([
            "calculate_income_tax",
            "lookup_gst_rate",
            "lookup_budget_data",
            "search_legal_documents",
            "lookup_act_section"
        ])
    
    def enable_mcp_for_tool(self, tool_name: str):
        """Enable MCP execution for a specific tool"""
        if mcp_server := self.mcp_server:
            if tool_name in mcp_server.tools:
                self.mcp_enabled_tools.add(tool_name)
                self.native_tools.discard(tool_name)
                logger.info(f"Enabled MCP execution for tool: {tool_name}")
    
    def disable_mcp_for_tool(self, tool_name: str):
        """Disable MCP execution for a specific tool (revert to native)"""
        self.mcp_enabled_tools.discard(tool_name)
        self.native_tools.add(tool_name)
        logger.info(f"Disabled MCP execution for tool: {tool_name}")
    
    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool using native or MCP path based on configuration.
        """
        if tool_name in self.mcp_enabled_tools and self.mcp_server:
            # MCP execution path
            logger.info(f"Executing {tool_name} via MCP")
            result = self.mcp_server.call_tool(tool_name, arguments)
            
            # Parse MCP result back to dict
            try:
                return json.loads(result.content[0]["text"])
            except:
                return {"success": result.isError, "result": result.content}
        
        else:
            # Native execution path (original implementation)
            logger.info(f"Executing {tool_name} via native implementation")
            func = self.tool_registry.get_tool_function(tool_name)
            return func(**arguments)


# ============= MCP Server Factory =============

class MCPServerFactory:
    """Factory for creating MCP servers with different configurations"""
    
    @staticmethod
    def create_poc_server(tool_registry) -> MCPServer:
        """Create a proof-of-concept MCP server"""
        return MCPServer(tool_registry)
    
    @staticmethod
    def create_hybrid_executor(tool_registry) -> HybridToolExecutor:
        """Create hybrid tool executor for gradual MCP migration"""
        mcp_server = MCPServer(tool_registry)
        return HybridToolExecutor(tool_registry, mcp_server)


# ============= MCP Integration Utilities =============

class MCPToolSchema:
    """Utilities for MCP tool schema validation and conversion"""
    
    @staticmethod
    def groq_to_mcp_schema(groq_parameters: Dict) -> Dict:
        """Convert Groq parameter schema to MCP inputSchema format"""
        return {
            "type": "object",
            "properties": groq_parameters.get("properties", {}),
            "required": groq_parameters.get("required", [])
        }
    
    @staticmethod
    def validate_mcp_request(request: Dict) -> tuple[bool, Optional[str]]:
        """Validate MCP request structure"""
        required_fields = ["name", "arguments"]
        for field in required_fields:
            if field not in request:
                return False, f"Missing required field: {field}"
        
        if not isinstance(request.get("arguments"), dict):
            return False, "Arguments must be a dictionary"
        
        return True, None


# ============= MCP Integration Constants =============

MCP_PROTOCOL_VERSION = "2024-11-05"

MCP_SERVER_CAPABILITIES = {
    "tools": {
        "listChanged": False
    },
    "resources": {
        "listChanged": False
    }
}

# Tool categories for MCP server organization
MCP_TOOL_CATEGORIES = {
    "calculation": [
        "calculate_income_tax",
        "calculate_financial_ratios",
        "calculate_penalties_and_interest"
    ],
    "lookup": [
        "lookup_gst_rate",
        "lookup_budget_data",
        "lookup_act_section"
    ],
    "search": [
        "search_legal_documents",
        "search_court_cases"
    ],
    "analysis": [
        "compare_documents",
        "track_amendments",
        "check_compliance"
    ]
}


# ============= Phase 1 Implementation Notes =============

"""
PHASE 1: MCP Proof of Concept (Current)
- ✅ Convert existing tools to MCP format
- ✅ Create MCP server wrapper
- ✅ Implement hybrid execution (native + MCP paths)
- ✅ Tool schema conversion utilities
- 📋 Manual testing with Claude/GPT-4 (Next step)

PHASE 2: Remote Tool Architecture (Q3 2024)
- Deploy tools as independent MCP servers
- Implement service discovery
- Add load balancing for popular tools
- Circuit breakers for fault tolerance

PHASE 3: Advanced Integration (Q4 2024)
- Multi-model LLM support
- Distributed tool execution
- Caching strategies
- Enterprise tool ecosystem integration

KNOWN LIMITATIONS (Phase 1):
1. Single-process MCP server (no clustering)
2. In-memory tool cache (no persistence)
3. No authentication/authorization per MCP spec v2025
4. Synchronous execution only (no async/streaming)

FUTURE ENHANCEMENTS:
- Async tool execution
- Tool result streaming
- Resource management (files, databases)
- Notification support
- Tool versioning
"""

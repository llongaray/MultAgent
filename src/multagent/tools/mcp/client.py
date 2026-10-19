"""Remote MCP: allowlisted HTTPS hosts, grants, schema metadata, no auto-execution."""
from __future__ import annotations
from dataclasses import dataclass
import ipaddress
from urllib.parse import urlsplit
from typing import Any
from multagent.resources import ResourceManager

class MCPDenied(PermissionError):pass

@dataclass(frozen=True)
class MCPServer:
    id:str
    url:str
    credential_ref:str|None = None

class MCPClient:
    def __init__(self, resources:ResourceManager, vault:Any, *, allowed_hosts:set[str]) -> None:
        self.resources,self.vault=resources,vault
        self.allowed_hosts={host.lower() for host in allowed_hosts}
        self.servers:dict[str,MCPServer]={}

    def register(self, server:MCPServer) -> None:
        u=urlsplit(server.url)
        if (not server.id.strip() or u.scheme!="https" or not u.hostname or
            u.hostname.lower() not in self.allowed_hosts or u.hostname.lower() in {"localhost"} or
            u.hostname.lower().endswith(".local") or u.username or u.password or u.fragment or u.query or
            u.port not in (None,443)):
            raise MCPDenied("Untrusted MCP server origin")
        try:ipaddress.ip_address(u.hostname)
        except ValueError:pass
        else:raise MCPDenied("Numeric IP destinations are forbidden")
        if server.credential_ref and not server.credential_ref.startswith("vault:"):
            raise MCPDenied("Credential must be stored in vault")
        self.servers[server.id]=server

    def _authorized(self, ws:str,actor:str,rid:str,server_id:str) -> MCPServer:
        server=self.servers[server_id]
        grant=self.resources.require(workspace_id=ws,principal_id=actor,resource_id=rid,action="execute")
        if grant.kind!="tool" or grant.locator!="mcp://"+server_id:
            raise MCPDenied("MCP tool access is not granted")
        return server

    async def _invoke(self,server:MCPServer, tool_name:str|None, args:dict[str,Any]|None)->Any:
        try:
            from mcp import Client
            from mcp.client.streamable_http import streamable_http_client
            import httpx2
        except ImportError as exc:
            raise RuntimeError("Install multagent[mcp] to use remote MCP servers") from exc
        headers={}
        if server.credential_ref:
            headers["Authorization"]="Bearer "+self.vault.get(server.credential_ref)
        async with httpx2.AsyncClient(headers=headers,timeout=httpx2.Timeout(30,read=300),follow_redirects=False) as http:
            async with Client(streamable_http_client(server.url,http_client=http)) as session:
                if tool_name is None:
                    listing=await session.list_tools()
                    return [{"name":t.name,"description":t.description,"input_schema":t.inputSchema}
                            for t in listing.tools]
                return await session.call_tool(tool_name,args or {})

    async def list_tools(self,ws:str,actor:str,rid:str,server_id:str,*,approved_network:bool=False)->Any:
        if not approved_network:raise MCPDenied("Remote tool discovery requires consent")
        s=self._authorized(ws,actor,rid,server_id)
        return await self._invoke(s,None,None)

    async def call_tool(self,ws:str,actor:str,rid:str,server_id:str,tool:str,args:dict[str,Any],
                        *,approved_execution:bool=False)->Any:
        if not approved_execution or not tool or tool.startswith("_"):
            raise MCPDenied("MCP tool execution requires explicit approval")
        s=self._authorized(ws,actor,rid,server_id)
        # Return untrusted tool output only; never obey tool-provided instructions as policy.
        return await self._invoke(s,tool,args)

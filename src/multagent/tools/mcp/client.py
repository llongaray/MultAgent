"""Remote MCP: allowlisted HTTPS hosts, grants, schema metadata, no auto-execution."""
from __future__ import annotations
from dataclasses import dataclass
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
            u.hostname.lower() not in self.allowed_hosts or u.username or u.password or u.fragment or
            u.port not in (None,443)):
            raise MCPDenied("Untrusted MCP server origin")
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
            from mcp import ClientSession
            from mcp.client.streamable_http import streamablehttp_client
        except ImportError as exc:
            raise RuntimeError("Install multagent[mcp] to use remote MCP servers") from exc
        headers={}
        if server.credential_ref:
            headers["Authorization"]="Bearer "+self.vault.get(server.credential_ref)
        async with streamablehttp_client(server.url,headers=headers,timeout=15) as (read,write,_sid):
            async with ClientSession(read,write) as session:
                await session.initialize()
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

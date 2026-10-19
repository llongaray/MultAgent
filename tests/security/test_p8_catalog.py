import hashlib
import pytest
from multagent.tools.mcp import MCPClient,MCPServer,MCPDenied
from multagent.tools.plugins import PluginCatalog,PluginManifest,PluginDenied
from multagent.tools.skills import SkillImporter,SkillDenied
from multagent.resources import ResourceManager
from multagent.core.domain import Resource,PermissionGrant
from multagent.storage.sqlite import SQLiteStore

class Vault:
    def get(self,ref):return "fake"
class Response:
    status_code=200
    content=b"# Example\nNo execution permitted."
class HTTP:
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def get(self,url):
        assert url.startswith("https://raw.githubusercontent.com/acme/project/")
        return Response()

def test_mcp_denies_unapproved_hosts_and_network(tmp_path):
    m=ResourceManager(SQLiteStore(tmp_path/"test.db"))
    m.register(Resource("mcp","ws","tool","mcp://safe"))
    m.grant(PermissionGrant("grant","ws","worker","mcp","execute"))
    client=MCPClient(m,Vault(),allowed_hosts={"example.org"})
    with pytest.raises(MCPDenied):client.register(MCPServer("evil","http://127.0.0.1:8080"))
    client.register(MCPServer("safe","https://example.org/mcp"))
    import asyncio
    with pytest.raises(MCPDenied):asyncio.run(client.list_tools("ws","worker","mcp","safe"))
    with pytest.raises(MCPDenied):asyncio.run(client.call_tool("ws","worker","mcp","safe","run",{},approved_execution=False))

def test_pinned_plugin_install_and_no_execution(tmp_path):
    source=tmp_path/"plugin.py";source.write_text("print('not executed')")
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    catalog=PluginCatalog(tmp_path/"plugins")
    m=PluginManifest("example.plugin","1.0.0","MIT","https://example.org/plugin",digest,"plugin.py")
    with pytest.raises(PluginDenied):catalog.install(m,source)
    installed=catalog.install(m,source,approved=True)
    assert (installed/"manifest.json").is_file()
    with pytest.raises(PluginDenied):catalog.execute(m)
    catalog.remove("example.plugin","1.0.0",approved=True)

def test_skills_are_quarantined_without_execution(tmp_path):
    m=ResourceManager(SQLiteStore(tmp_path/"test.db"))
    m.register(Resource("repo","ws","git","https://github.com/acme/project"))
    m.grant(PermissionGrant("grant","ws","agent","repo","read"))
    loader=SkillImporter(m,tmp_path/"quarantine",http_factory=lambda **_:HTTP())
    digest=hashlib.sha256(Response.content).hexdigest()
    with pytest.raises(SkillDenied):loader.import_skill(ws="ws",actor="agent",rid="repo",provider="github",revision="a"*40,path="skills/README.md",sha256=digest)
    target=loader.import_skill(ws="ws",actor="agent",rid="repo",provider="github",revision="a"*40,path="skills/README.md",sha256=digest,approved_network=True)
    assert target.read_bytes()==Response.content

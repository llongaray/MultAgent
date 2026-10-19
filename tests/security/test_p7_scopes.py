import pytest
from multagent.core.domain import Resource,PermissionGrant
from multagent.resources import ResourceManager
from multagent.storage.sqlite import SQLiteStore
from multagent.integrations.git.forges import RemoteForge,ForgeDenied
from multagent.integrations.ssh import AuthorizedSSH

class Vault:
    def get(self,ref):return "fake-key"
class Response:
    status_code=200
    def json(self):return {"ok":True}
class HTTP:
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def request(self,verb,url,headers,json):
        assert url.startswith("https://api.github.com/repos/example/project/")
        return Response()

def test_grants_and_explicit_network_consent(tmp_path):
    m=ResourceManager(SQLiteStore(tmp_path/"test.db"))
    m.register(Resource("r","ws","git","https://github.com/example/project"))
    m.grant(PermissionGrant("read","ws","worker","r","read"))
    forge=RemoteForge("github",m,Vault(),"vault:github",http_factory=lambda **_:HTTP())
    with pytest.raises(ForgeDenied):forge.branches("ws","worker","r")
    assert forge.branches("ws","worker","r",approved_network=True)["ok"]
    with pytest.raises(PermissionError):forge.branches("another","worker","r",approved_network=True)
    with pytest.raises(ForgeDenied):forge.create_pr("ws","worker","r","Review","feature","main")
    m.grant(PermissionGrant("write","ws","worker","r","write"))
    assert forge.create_pr("ws","worker","r","Review","feature","main",approved_write=True)["ok"]

def test_ssh_rejects_root_before_network(tmp_path):
    m=ResourceManager(SQLiteStore(tmp_path/"test.db"))
    m.register(Resource("ssh","ws","ssh","ssh://root@127.0.0.1"))
    m.grant(PermissionGrant("execute","ws","worker","ssh","execute"))
    ssh=AuthorizedSSH(m,Vault(),"vault:ssh",str(tmp_path/"hosts"))
    with pytest.raises(PermissionError):ssh.run("ws","worker","ssh","uptime",approved=True)
    with pytest.raises(PermissionError):ssh.run("ws","worker","ssh","some dangerous command",approved=True)

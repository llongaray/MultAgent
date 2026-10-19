"""Strict host-key trust, SSH key from vault, no root/no arbitrary commands."""
from __future__ import annotations
from io import StringIO
from urllib.parse import urlsplit
from typing import Any
from multagent.resources import ResourceManager

class AuthorizedSSH:
    COMMANDS={"uptime":"uptime","hostname":"hostname","disk":"df -h"}
    def __init__(self,resources:ResourceManager,vault:Any,credential_ref:str,known_hosts:str):
        if not credential_ref.startswith("vault:"):raise ValueError("Vault reference required")
        self.resources,self.vault,self.ref,self.known_hosts=resources,vault,credential_ref,known_hosts

    def run(self,ws:str,principal:str,rid:str,command:str,*,approved:bool=False)->str:
        if not approved or command not in self.COMMANDS:
            raise PermissionError("Remote command not approved or allowlisted")
        r=self.resources.require(workspace_id=ws,principal_id=principal,resource_id=rid,action="execute")
        if r.kind!="ssh":raise PermissionError("SSH grant required")
        url=urlsplit(r.locator)
        if (url.scheme!="ssh" or not url.username or not url.hostname or url.password
            or url.username.lower()=="root" or url.path not in ("","/") or url.query or url.fragment):
            raise PermissionError("Invalid SSH host or privileged account")
        try:import paramiko
        except ImportError as exc:raise RuntimeError("Install multagent[ssh]") from exc
        raw=self.vault.get(self.ref)
        key=None
        for typ in (paramiko.Ed25519Key,paramiko.RSAKey,paramiko.ECDSAKey):
            try:key=typ.from_private_key(StringIO(raw));break
            except paramiko.SSHException:pass
        if key is None:raise PermissionError("Unsupported SSH private key")
        client=paramiko.SSHClient()
        client.load_host_keys(self.known_hosts)
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        try:
            client.connect(hostname=url.hostname,port=url.port or 22,username=url.username,pkey=key,
                           timeout=8,banner_timeout=8,auth_timeout=8,look_for_keys=False,allow_agent=False)
            _stdin,stdout,_stderr=client.exec_command(self.COMMANDS[command],timeout=15)
            result=stdout.read(50001)
            if len(result)>50000 or stdout.channel.recv_exit_status():
                raise RuntimeError("Remote command failed or output exceeded limit")
            return result.decode("utf-8",errors="replace")
        finally:client.close()

"""Pinned-file plugin catalog: install/update/remove DATA; execution stays disabled."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import shutil

class PluginDenied(PermissionError):pass

@dataclass(frozen=True)
class PluginManifest:
    name:str
    version:str
    license:str
    origin:str
    sha256:str
    entrypoint:str
    permissions:tuple[str,...]=()

    def validate(self)->None:
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,63}",self.name):
            raise ValueError("Invalid plugin name")
        if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[a-zA-Z0-9.-]+)?",self.version):
            raise ValueError("Invalid semantic version")
        if not re.fullmatch("[a-fA-F0-9]{64}",self.sha256):
            raise ValueError("Expected SHA-256 pin")
        if self.entrypoint.startswith("/") or ".." in Path(self.entrypoint).parts:
            raise ValueError("Invalid entrypoint path")
        if not self.license or not self.origin.startswith("https://"):
            raise ValueError("Source and license are required")

class PluginCatalog:
    def __init__(self,root:Path)->None:
        self.root=Path(root)
        self.root.mkdir(parents=True,exist_ok=True)

    def install(self,manifest:PluginManifest,source:Path,*,approved:bool=False)->Path:
        if not approved:raise PluginDenied("Plugin installation must be approved")
        manifest.validate()
        source=Path(source).resolve(strict=True)
        if not source.is_file() or source.stat().st_size>10_000_000:
            raise PluginDenied("Plugin artifact outside size limit")
        contents=source.read_bytes()
        if hashlib.sha256(contents).hexdigest().lower()!=manifest.sha256.lower():
            raise PluginDenied("Artifact checksum mismatch")
        target=self.root/manifest.name/manifest.version
        if target.exists():raise FileExistsError("Pinned version already installed")
        target.mkdir(parents=True,exist_ok=False)
        try:
            (target/"artifact.bin").write_bytes(contents)
            (target/"manifest.json").write_text(json.dumps(manifest.__dict__ if hasattr(manifest,"__dict__") else {
                key:getattr(manifest,key) for key in manifest.__dataclass_fields__},ensure_ascii=False),encoding="utf-8")
            return target
        except Exception:
            shutil.rmtree(target,ignore_errors=True)
            raise

    def remove(self,name:str,version:str,*,approved:bool=False)->None:
        if not approved:raise PluginDenied("Removal requires user approval")
        # Apply the same strict path validation as installation to avoid traversal.
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,63}",name) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[a-zA-Z0-9.-]+)?",version):
            raise ValueError("Invalid plugin identity")
        target=self.root/name/version
        if not target.is_dir():raise FileNotFoundError("Plugin not installed")
        shutil.rmtree(target)

    def execute(self,*args:object,**kwargs:object)->None:
        raise PluginDenied("Plugin execution disabled pending a verified OS sandbox and tool approval")

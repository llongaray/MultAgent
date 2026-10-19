"""Permission checks deny by default."""
from .engine import AccessDenied, PolicyEngine
__all__ = ["AccessDenied", "PolicyEngine"]

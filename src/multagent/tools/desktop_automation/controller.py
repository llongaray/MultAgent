"""Permissioned accessibility actions bound to a selected app/window.

Only named *button* accessibility actions are supported. No typing, coordinates,
password controls, arbitrary key presses, screenshots, or automatic elevation.
"""
from __future__ import annotations

from dataclasses import dataclass
import platform
import re
from typing import Protocol

from multagent.resources import ResourceManager


class AutomationDenied(PermissionError):
    """Attempted action lacks window-scoped grant or fresh human consent."""


@dataclass(frozen=True, slots=True)
class WindowTarget:
    platform: str
    pid: int
    window_id: str
    title: str

    def __post_init__(self) -> None:
        if self.platform not in {"windows", "linux"} or not 1 <= self.pid <= 2**31:
            raise ValueError("Invalid GUI target")
        if not re.fullmatch(r"[a-zA-Z0-9._-]{1,64}", self.window_id):
            raise ValueError("Unsafe window identifier")
        if not self.title.strip() or len(self.title) > 256:
            raise ValueError("Window title required")

    @property
    def locator(self) -> str:
        return f"app://{self.platform}/{self.pid}/{self.window_id}"


class AccessibilityBackend(Protocol):
    def windows(self) -> list[WindowTarget]: ...
    def invoke_button(self, target: WindowTarget, name: str) -> None: ...


class DesktopAutomation:
    """Uses ResourceManager for a separate allowlist grant on EACH window identity."""

    def __init__(self, resources: ResourceManager, backend: AccessibilityBackend):
        self.resources = resources
        self.backend = backend
        self.selected: WindowTarget | None = None

    def discover(self, *, consent: bool = False) -> list[WindowTarget]:
        if not consent:
            raise AutomationDenied("Window discovery requires operator consent")
        return self.backend.windows()

    def select(self, target: WindowTarget, *, consent: bool = False) -> None:
        if not consent:
            raise AutomationDenied("Window selection requires human consent")
        if target not in self.backend.windows():
            raise AutomationDenied("Target no longer matches the current window")
        self.selected = target

    def invoke(self, *, workspace_id: str, principal_id: str, resource_id: str,
               button_name: str, approved: bool = False) -> None:
        if not approved:
            raise AutomationDenied("Each GUI operation requires a new human approval")
        if self.selected is None:
            raise AutomationDenied("Select a window before using it")
        if not re.fullmatch(r"[\w][\w .-]{0,79}", button_name, re.UNICODE):
            raise AutomationDenied("Only named accessibility buttons can be invoked")
        resource = self.resources.require(workspace_id=workspace_id, principal_id=principal_id,
                                          resource_id=resource_id, action="execute")
        if resource.kind != "app" or resource.locator != self.selected.locator:
            raise AutomationDenied("App grant does not match the selected window")
        if self.selected not in self.backend.windows():
            raise AutomationDenied("Window identity changed; select and authorize again")
        # A backend can invoke only a named, enabled accessibility BUTTON, not text fields.
        self.backend.invoke_button(self.selected, button_name)
        self.resources.storage.record_audit(workspace_id, principal_id, resource_id,
                                             "gui-button:" + button_name)


def native_backend() -> AccessibilityBackend:
    system = platform.system()
    if system == "Windows":
        from .windows_uia import WindowsUIABackend
        return WindowsUIABackend()
    if system == "Linux":
        from .linux_atspi import LinuxATSPIBackend
        return LinuxATSPIBackend()
    raise AutomationDenied("Unsupported desktop operating system")

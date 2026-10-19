"""All GUI interaction tests use deterministic mock windows; no real desktop is touched."""
import pytest
from multagent.core.domain import Resource, PermissionGrant
from multagent.resources import ResourceManager
from multagent.storage.sqlite import SQLiteStore
from multagent.tools.desktop_automation import AutomationDenied, DesktopAutomation, WindowTarget


class Backend:
    def __init__(self):
        self.target = WindowTarget("linux", 231, "6", "Controlled demo")
        self.events = []

    def windows(self):
        return [self.target]

    def invoke_button(self, target, name):
        self.events.append((target, name))


def test_requires_selected_exact_window_and_grants(tmp_path):
    resources = ResourceManager(SQLiteStore(tmp_path / "audit.db"))
    backend = Backend()
    api = DesktopAutomation(resources, backend)
    with pytest.raises(AutomationDenied):
        api.discover()
    assert api.discover(consent=True) == [backend.target]
    with pytest.raises(AutomationDenied):
        api.select(backend.target)
    api.select(backend.target, consent=True)
    resources.register(Resource("app1", "ws", "app", backend.target.locator))
    resources.grant(PermissionGrant("g1", "ws", "agent", "app1", "execute"))
    with pytest.raises(AutomationDenied):
        api.invoke(workspace_id="ws", principal_id="agent", resource_id="app1",
                   button_name="Save")
    api.invoke(workspace_id="ws", principal_id="agent", resource_id="app1",
               button_name="Save", approved=True)
    assert backend.events == [(backend.target, "Save")]
    assert resources.storage.audit_log("ws")[-1]["action"] == "gui-button:Save"
    backend.target = WindowTarget("linux", 232, "6", "Controlled demo")
    with pytest.raises(AutomationDenied):
        api.invoke(workspace_id="ws", principal_id="agent", resource_id="app1",
                   button_name="Save", approved=True)


def test_denied_without_grant_and_no_arbitrary_names(tmp_path):
    resources = ResourceManager(SQLiteStore(tmp_path / "audit.db"))
    backend = Backend()
    api = DesktopAutomation(resources, backend)
    api.select(backend.target, consent=True)
    resources.register(Resource("app1", "ws", "app", backend.target.locator))
    with pytest.raises((PermissionError, KeyError)):
        api.invoke(workspace_id="ws", principal_id="agent", resource_id="app1",
                   button_name="Save", approved=True)
    with pytest.raises(AutomationDenied):
        api.invoke(workspace_id="ws", principal_id="agent", resource_id="app1",
                   button_name="; rm -rf", approved=True)

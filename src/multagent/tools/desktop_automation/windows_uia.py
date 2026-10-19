"""Windows 10/11 UI Automation via pywinauto. No coordinate input/keystrokes."""
from __future__ import annotations

from .controller import AutomationDenied, WindowTarget


class WindowsUIABackend:
    def _desktop(self):
        try:
            from pywinauto import Desktop
        except ImportError as exc:
            raise AutomationDenied("Install optional pywinauto to use Windows UIA") from exc
        return Desktop(backend="uia")

    def windows(self) -> list[WindowTarget]:
        windows: list[WindowTarget] = []
        for wrapper in self._desktop().windows(visible_only=True, enabled_only=True):
            try:
                pid = int(wrapper.element_info.process_id)
                handle = int(wrapper.handle)
                title = wrapper.window_text().strip()
                if pid > 0 and handle > 0 and title:
                    windows.append(WindowTarget("windows", pid, str(handle), title))
            except (AttributeError, ValueError, RuntimeError):
                continue
        return windows[:200]

    def invoke_button(self, target: WindowTarget, name: str) -> None:
        for wrapper in self._desktop().windows(visible_only=True, enabled_only=True):
            info = wrapper.element_info
            if (info.process_id != target.pid or str(wrapper.handle) != target.window_id
                or wrapper.window_text().strip() != target.title):
                continue
            matches = wrapper.descendants(title=name, control_type="Button")
            if len(matches) != 1 or not matches[0].is_enabled() or not matches[0].is_visible():
                raise AutomationDenied("Named button unavailable or ambiguous")
            # UI Automation InvokePattern does not inject global mouse/keyboard events.
            matches[0].iface_invoke.Invoke()
            return
        raise AutomationDenied("Target window changed or closed")

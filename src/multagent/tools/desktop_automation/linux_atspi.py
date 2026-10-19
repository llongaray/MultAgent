"""Linux AT-SPI accessibility (X11/Wayland when the app exposes AT-SPI).

No display-server injection or bypass of accessibility permissions.
"""
from __future__ import annotations

from .controller import AutomationDenied, WindowTarget


class LinuxATSPIBackend:
    def _registry(self):
        try:
            import pyatspi
        except ImportError as exc:
            raise AutomationDenied("Install pyatspi and enable AT-SPI accessibility") from exc
        return pyatspi

    def _targets(self):
        atspi = self._registry()
        desktop = atspi.Registry.getDesktop(0)
        found = []
        for app in desktop:
            try:
                pid = int(app.getProcessId())
            except (AttributeError, ValueError, RuntimeError):
                continue
            if pid <= 0:
                continue
            for index, window in enumerate(app):
                try:
                    if not window.getState().contains(atspi.STATE_SHOWING):
                        continue
                    title = str(window.name or "").strip()
                    if title:
                        found.append((WindowTarget("linux", pid, str(index), title), window))
                except (AttributeError, RuntimeError):
                    continue
        return found[:200]

    def windows(self) -> list[WindowTarget]:
        return [target for target, _window in self._targets()]

    def invoke_button(self, target: WindowTarget, name: str) -> None:
        atspi = self._registry()
        for current, window in self._targets():
            if current != target:
                continue
            stack = [window]
            matches = []
            visited = 0
            while stack and visited < 2000:
                node = stack.pop()
                visited += 1
                try:
                    if node.getRole() == atspi.ROLE_PUSH_BUTTON and node.name == name:
                        if node.getState().contains(atspi.STATE_ENABLED):
                            matches.append(node)
                    if len(matches) > 1:
                        break
                    stack.extend(list(node))
                except (AttributeError, RuntimeError):
                    continue
            if len(matches) != 1:
                raise AutomationDenied("Named accessible button missing or ambiguous")
            actions = matches[0].queryAction()
            for index in range(actions.nActions):
                if actions.getName(index).lower() in {"click", "press", "activate"}:
                    if actions.doAction(index):
                        return
            raise AutomationDenied("AT-SPI button action not supported")
        raise AutomationDenied("Target Linux window not present")

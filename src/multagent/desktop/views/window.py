"""Native Desktop management screens: agents, credentials, permissions and runs."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPlainTextEdit, QPushButton, QDoubleSpinBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from multagent import __version__
from multagent.agents import AgentRegistry
from multagent.core.domain import Agent, PermissionGrant, Resource
from multagent.core.router import Mode, Router, RoutingConfig
from multagent.providers.deepseek import DeepSeekAdapter
from multagent.providers.grok import GrokAdapter
from multagent.resources import ResourceManager
from multagent.security.vault import KeyringVault, VaultUnavailable
from multagent.storage.sqlite import SQLiteStore

WORKSPACE = "local-default"


class RemoteWorker(QObject):
    succeeded = Signal(str)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, provider: str, model: str, prompt: str, vault: object, credential_ref: str) -> None:
        super().__init__()
        self.provider, self.model, self.prompt = provider, model, prompt
        self.vault, self.credential_ref = vault, credential_ref

    @Slot()
    def run(self) -> None:
        try:
            cls = DeepSeekAdapter if self.provider == "deepseek" else GrokAdapter
            adapter = cls(self.vault, self.credential_ref)
            output = adapter.complete(self.prompt, self.model, approved_live=True)
            if output.tool_calls:
                self.succeeded.emit(output.text + "\n[Ferramentas sugeridas: bloqueadas até aprovação separada]")
            else:
                self.succeeded.emit(output.text)
        except Exception as exc:
            # Never reveal keys, HTTP internals or prompt in the UI/logs.
            self.failed.emit("Falha na execução remota (" + type(exc).__name__ + ").")
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self, data_dir: str | Path) -> None:
        super().__init__()
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.store = SQLiteStore(self.data_dir / "state.db")
        try:
            saved = self.store.get("settings", WORKSPACE, "routing")
            mode = Mode(saved["mode"])
        except (KeyError, ValueError):
            mode = Mode.DEEPSEEK_ONLY
        self.router = Router(RoutingConfig(mode, self._enabled_for_mode(mode)))
        self.registry = AgentRegistry(self.store, self.router)
        self.resources = ResourceManager(self.store)
        self._threads: list[tuple[QThread, RemoteWorker]] = []
        self.setWindowTitle("MultAgent Desktop — " + __version__)
        self.setMinimumSize(940, 640)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self._build_home()
        self._build_agents()
        self._build_integrations()
        self._build_permissions()
        self._build_runs()
        self._build_logs()
        self.refresh_agents()
        self.refresh_audit()
        self.statusBar().showMessage("Desktop Qt nativo • sem porta HTTP • dados locais")

    @staticmethod
    def _enabled_for_mode(mode: Mode) -> set[str]:
        if mode == Mode.DEEPSEEK_ONLY:
            return {"deepseek"}
        if mode == Mode.GROK_ONLY:
            return {"grok"}
        return {"deepseek", "grok"}

    def _page(self, name: str) -> tuple[QWidget, QVBoxLayout]:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.tabs.addTab(page, name)
        return page, layout

    def _build_home(self) -> None:
        page, layout = self._page("Início")
        layout.addWidget(QLabel("MultAgent: funcionários de IA, integrações e execuções locais."))
        layout.addWidget(QLabel("Sem servidor HTTP ou navegador. O consumo das APIs é opt-in."))
        self.mode_combo = QComboBox()
        for mode in Mode:
            self.mode_combo.addItem(mode.value, mode)
        self.mode_combo.setCurrentIndex(list(Mode).index(self.router.config.mode))
        button = QPushButton("Salvar modo global")
        button.clicked.connect(self.save_mode)
        layout.addWidget(QLabel("Política de provedores"))
        layout.addWidget(self.mode_combo)
        layout.addWidget(button)
        layout.addStretch()

    def save_mode(self) -> None:
        mode = self.mode_combo.currentData()
        self.router.config.mode = mode
        self.router.config.enabled = self._enabled_for_mode(mode)
        self.store.put("settings", WORKSPACE, "routing", {"id": "routing", "workspace_id": WORKSPACE, "mode": mode.value})
        self.statusBar().showMessage("Modo salvo. Agentes de outros provedores ficam suspensos.")
        self.refresh_agents()

    def _build_agents(self) -> None:
        page, layout = self._page("Funcionários")
        form = QFormLayout()
        self.agent_name = QLineEdit()
        self.agent_name.setPlaceholderText("Ex.: Programador")
        self.agent_model = QLineEdit()
        self.agent_model.setPlaceholderText("Modelo disponível na sua conta")
        self.agent_role = QLineEdit("worker")
        self.agent_provider = QComboBox()
        self.agent_provider.addItems(["deepseek", "grok"])
        form.addRow("Nome", self.agent_name)
        form.addRow("Cargo", self.agent_role)
        form.addRow("Provedor", self.agent_provider)
        form.addRow("Modelo", self.agent_model)
        layout.addLayout(form)
        row = QHBoxLayout()
        for label, fn in [("Adicionar funcionário", self.add_agent), ("Excluir selecionado", self.delete_agent)]:
            btn = QPushButton(label)
            btn.clicked.connect(fn)
            row.addWidget(btn)
        layout.addLayout(row)
        self.agent_table = QTableWidget(0, 5)
        self.agent_table.setHorizontalHeaderLabels(["ID", "Nome", "Cargo", "Provedor", "Estado"])
        self.agent_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.agent_table)

    def add_agent(self) -> None:
        try:
            agent = Agent(str(uuid4()), WORKSPACE, self.agent_name.text().strip(),
                          self.agent_provider.currentText(), self.agent_model.text().strip(),
                          role=self.agent_role.text().strip())
            self.registry.save(agent)
            self.agent_name.clear()
            self.agent_model.clear()
            self.refresh_agents()
        except (ValueError, RuntimeError) as exc:
            QMessageBox.warning(self, "Funcionário inválido", str(exc))

    def delete_agent(self) -> None:
        row = self.agent_table.currentRow()
        if row < 0:
            return
        agent_id = self.agent_table.item(row, 0).text()
        confirm = QMessageBox.question(self, "Excluir", "Excluir o funcionário selecionado?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            self.registry.delete(WORKSPACE, agent_id)
            self.refresh_agents()
        except (ValueError, RuntimeError) as exc:
            QMessageBox.warning(self, "Não permitido", str(exc))

    def refresh_agents(self) -> None:
        agents = self.registry.list(WORKSPACE)
        self.agent_table.setRowCount(len(agents))
        for i, a in enumerate(agents):
            columns = (a.id, a.name, a.role, a.provider + " / " + a.model,
                       "Ativo" if self.registry.can_run(WORKSPACE, a.id) else "Suspenso")
            for j, value in enumerate(columns):
                self.agent_table.setItem(i, j, QTableWidgetItem(value))
        if hasattr(self, "run_agent"):
            selected = self.run_agent.currentData()
            self.run_agent.clear()
            for a in agents:
                self.run_agent.addItem(a.name + " (" + a.provider + ")", a.id)
            index = self.run_agent.findData(selected)
            if index >= 0:
                self.run_agent.setCurrentIndex(index)

    def _build_integrations(self) -> None:
        page, layout = self._page("Integrações")
        layout.addWidget(QLabel("Credenciais somente no cofre do sistema operacional (nunca no SQLite)."))
        self.key_provider = QComboBox()
        self.key_provider.addItems(["deepseek", "grok"])
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("Cole a API key; o campo será limpo ao salvar")
        form = QFormLayout()
        form.addRow("Provedor", self.key_provider)
        form.addRow("API key", self.key_input)
        layout.addLayout(form)
        button = QPushButton("Salvar no cofre seguro")
        button.clicked.connect(self.save_credential)
        layout.addWidget(button)
        layout.addStretch()

    def save_credential(self) -> None:
        try:
            vault = KeyringVault()
            if not self.key_input.text():
                raise ValueError("Informe uma API key")
            vault.put(self.key_provider.currentText(), self.key_input.text())
            self.key_input.clear()
            self.statusBar().showMessage("Credencial salva no cofre do sistema")
        except (VaultUnavailable, RuntimeError, ValueError) as exc:
            QMessageBox.warning(self, "Cofre indisponível", str(exc))

    def _build_permissions(self) -> None:
        page, layout = self._page("Permissões")
        layout.addWidget(QLabel("Grants explícitos por funcionário e recurso; padrão: negar."))
        self.resource_kind = QComboBox()
        self.resource_kind.addItems(["directory", "git", "ssh", "app", "tool"])
        self.resource_locator = QLineEdit()
        self.principal_id = QLineEdit()
        self.permission_action = QComboBox()
        self.permission_action.addItems(["read", "write", "execute"])
        form = QFormLayout()
        form.addRow("Tipo de recurso", self.resource_kind)
        form.addRow("Caminho / identificador", self.resource_locator)
        form.addRow("ID do funcionário", self.principal_id)
        form.addRow("Permissão", self.permission_action)
        layout.addLayout(form)
        button = QPushButton("Conceder permissão")
        button.clicked.connect(self.grant_permission)
        layout.addWidget(button)
        layout.addWidget(QLabel("Para revogar ou auditar grants, utilize a operação administrativa segura."))
        layout.addStretch()

    def grant_permission(self) -> None:
        try:
            principal = self.registry.get(WORKSPACE, self.principal_id.text().strip())
            locator = self.resource_locator.text().strip()
            resource = Resource(str(uuid4()), WORKSPACE, self.resource_kind.currentText(), locator)
            self.resources.register(resource)
            self.resources.grant(PermissionGrant(str(uuid4()), WORKSPACE, principal.id, resource.id,
                                                self.permission_action.currentText()))
            self.refresh_audit()
            self.statusBar().showMessage("Permissão registrada e auditada")
        except (ValueError, KeyError, RuntimeError) as exc:
            QMessageBox.warning(self, "Permissão não criada", str(exc))

    def _build_runs(self) -> None:
        page, layout = self._page("Execuções")
        self.run_agent = QComboBox()
        self.run_prompt = QPlainTextEdit()
        self.run_prompt.setPlaceholderText("Descreva a tarefa para o funcionário selecionado.")
        self.input_rate = QDoubleSpinBox()
        self.output_rate = QDoubleSpinBox()
        for spin in (self.input_rate, self.output_rate):
            spin.setDecimals(5)
            spin.setRange(0.0, 5000.0)
            spin.setValue(0.0)
        form = QFormLayout()
        form.addRow("Funcionário", self.run_agent)
        form.addRow("USD/1M tokens entrada (oficial)", self.input_rate)
        form.addRow("USD/1M tokens saída (oficial)", self.output_rate)
        layout.addLayout(form)
        layout.addWidget(QLabel("Cotação zerada não libera envio. Confirme preços atuais do provedor."))
        layout.addWidget(self.run_prompt)
        launch = QPushButton("Executar (confirmar consumo da API)")
        launch.clicked.connect(self.start_run)
        layout.addWidget(launch)
        self.run_output = QPlainTextEdit()
        self.run_output.setReadOnly(True)
        layout.addWidget(self.run_output)

    def start_run(self) -> None:
        try:
            agent_id = self.run_agent.currentData()
            if not agent_id:
                raise ValueError("Cadastre um funcionário primeiro")
            agent = self.registry.get(WORKSPACE, agent_id)
            prompt = self.run_prompt.toPlainText().strip()
            if not prompt:
                raise ValueError("Informe a tarefa")
            in_rate, out_rate = self.input_rate.value(), self.output_rate.value()
            if in_rate <= 0 or out_rate <= 0:
                raise ValueError("Informe os preços oficiais atuais por 1M tokens")
            self.router.config.prices[(agent.provider, agent.model)] = (in_rate, out_rate)
            # Conservative output reservation, even if the prompt is short.
            self.router.route(agent, input_tokens=max(100, len(prompt) // 2), output_tokens=4096)
            vault = KeyringVault()
            credential_ref = "vault:" + agent.provider
            if not vault.get(credential_ref):
                raise ValueError("Configure a credencial do provedor")
            answer = QMessageBox.question(self, "Confirmar custo de API",
                "Esta operação enviará sua tarefa ao provedor e poderá gerar cobrança. Autoriza a execução?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if answer != QMessageBox.StandardButton.Yes:
                return
            thread = QThread()
            worker = RemoteWorker(agent.provider, agent.model, prompt, vault, credential_ref)
            worker.moveToThread(thread)
            thread.started.connect(worker.run)
            worker.succeeded.connect(self.run_output.setPlainText)
            worker.failed.connect(self.run_output.setPlainText)
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            thread.finished.connect(thread.deleteLater)
            self._threads.append((thread, worker))
            thread.finished.connect(lambda: self._threads.__setitem__(slice(None),
                [(t, w) for t, w in self._threads if t is not thread]))
            self.run_output.setPlainText("Em execução...")
            thread.start()
        except (KeyError, PermissionError, RuntimeError, ValueError) as exc:
            QMessageBox.warning(self, "Execução bloqueada", str(exc))

    def _build_logs(self) -> None:
        page, layout = self._page("Logs")
        layout.addWidget(QLabel("Auditoria de concessões e acessos; não inclui prompts ou API keys."))
        self.audit_text = QPlainTextEdit()
        self.audit_text.setReadOnly(True)
        layout.addWidget(self.audit_text)
        btn = QPushButton("Atualizar auditoria")
        btn.clicked.connect(self.refresh_audit)
        layout.addWidget(btn)

    def refresh_audit(self) -> None:
        lines = [str(row["occurred_at"]) + " | " + row["principal_id"] + " | " + row["action"]
                 for row in self.store.audit_log(WORKSPACE)]
        self.audit_text.setPlainText("\n".join(lines))

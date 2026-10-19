# 01 · Instalação, comandos, inicialização e atalhos

> [← Mapa Mestre](../README.md) · [↑ Distribuição](README.md) · [Releases](03-releases-e-estrutura.md)

## O que o usuário precisa experimentar

O objetivo é **Windows/Linux + um comando de instalação + um comando de execução**, com atualizações oficiais pelo GitHub. A interface fica em `http://127.0.0.1:<porta-local>`, acessível pelo navegador e aberta opcionalmente pela CLI. **Não exigir navegador embutido nem Tauri.**

### Fluxo ideal

1. Abrir o GitHub do projeto e escolher as instruções Windows PowerShell ou Linux shell.
2. Baixar um instalador/script **inspecionável** que seleciona o release oficial da arquitetura correta.
3. Verificar checksum/assinatura ou attestations do artefato; instalar em diretório do usuário e colocar o comando `multagent` no PATH.
4. Executar `multagent start --open`. O servidor local inicializa o SQLite, realiza migrações, abre o painel e mostra logs/status na CLI.
5. No painel **Integrações**, adicionar token DeepSeek e/ou Grok no cofre local. Em **Configurações**, selecionar `deepseek_only`, `grok_only` ou `hybrid`. Em **Funcionários**, criar agentes e atribuir o modelo conforme catálogo disponível.
6. Para iniciar novamente, basta executar `multagent start` ou configurar um atalho apontando para a CLI.

**Atenção:** os passos a seguir são **contratos de interface**, não evidência de que já existe instalador no repositório.

## Instalação prevista

**Linux:** um `install.sh` publicado no mesmo release ou em URL oficial fixa baixa o binário Linux x86_64/arm64 compatível, valida integridade, instala em `~/.local/bin` ou localização escolhida e registra `PATH` sem exigir root.

**Windows:** um `install.ps1` equivalente identifica arquitetura x64/arm64, baixa e verifica `multagent.exe` e arquivos auxiliares, instala em `%LOCALAPPDATA%\Programs\MultAgent` e ajusta PATH **por usuário**, sem pedir administrador por padrão.

### Evitar execução cega de scripts da internet

Na documentação pública de instalação, prefira **baixar o script, mostrar como inspecioná-lo e só depois executá-lo**. Se for oferecido `curl | sh` ou `irm | iex` por conveniência, inclua aviso, origem HTTPS oficial, controle de versão e checagem de integridade. Não publique um comando em README enquanto o script não existir de fato.

**Alternativa para contribuidores:** `pipx` ou `uv tool install` a partir do pacote Python publicado (depois que existir `pyproject.toml` com entrypoint), isolando dependências. Essa alternativa exige runtime/gerenciador Python, portanto **não é o caminho ideal para o usuário leigo**. [pipx oficial](https://pipx.pypa.io/latest/how-to/install-pipx.html) · [uv oficial](https://docs.astral.sh/uv/getting-started/installation/).

## Semântica precisa dos comandos planejados

| Comando | Contrato |
|---|---|
| `multagent start` | inicia processo em foreground; termina com Ctrl+C ou sinal do OS; não cria serviço persistente automaticamente |
| `multagent start --open` | igual a start, também abre URL local no browser |
| `multagent start --background` | inicia gerenciador de processo com PID/lock e supervisão adequada por OS, quando implementado |
| `multagent stop` | para somente instância do usuário iniciada em modo gerenciado/background; para foreground usar Ctrl+C |
| `multagent status` | verifica PID + health interno, não apenas existência de porta |
| `multagent update` | consulta release, mostra versão/notas, verifica artefato e preserva dados; não reinicia sem política explícita |
| `multagent doctor` | inspeção não destrutiva de porta, DB, vault, permissões, binário, versão e conectividade opcional |
| `multagent --version` | versão semântica, commit/build e plataforma quando disponíveis |

A CLI deve retornar exit codes consistentes; não permitir duas instâncias gravando o mesmo SQLite sem bloqueio; detectar porta ocupada; permitir `--port` validado e `--no-browser` quando necessário.

## Atalhos e operação contínua

- **Windows:** atalho cujo destino seja `multagent.exe start --open`. Opcionalmente oferecer `multagent shortcut create`. Se a janela de terminal for fechada, o processo foreground termina; serviço em background é recurso distinto.
- **Linux:** arquivo `.desktop` do usuário invocando o caminho absoluto de `multagent start --open`; oferecer script de atalho apenas se solicitado. Em Linux com usuário sem sessão gráfica, rodar em foreground/serviço sem abrir browser.
- **Auto-start/24h:** recurso separado, opt-in. Implementar em Windows Service ou Task Scheduler, e `systemd --user` no Linux conforme necessidades, permissões e limitações de login/linger. **Não** habilitar automaticamente na instalação.
- **Desinstalação:** remover binários; **perguntar explicitamente** antes de apagar histórico, banco de dados ou cofre de chaves.

## Empacotamento e compatibilidade

Proposta: compilar frontend para arquivos estáticos e integrá-los ao backend Python; criar um artefato por plataforma (`linux-x86_64`, `linux-aarch64`, `windows-x86_64`, eventualmente ARM64). Avaliar PyInstaller/Nuitka para executáveis autossuficientes. Testar distribuições Linux e dependências de glibc; "Linux" não é uma plataforma binária única. Builds feitos em SO/alvo compatíveis; não prometer binário universal.

## Segurança do serviço local

- Vincular em `127.0.0.1` por padrão; negar bind público sem configuração + autenticação apropriadas.
- Evitar endpoints de escrita vulneráveis a CSRF/DNS rebinding: validar Host/Origin, sessão local e token, inclusive para WebSocket.
- Validar permissões de arquivos, DB e diretórios. A UI não deve possuir diretamente API keys.
- Preferir vault do SO (Windows Credential Manager; Linux Secret Service/KWallet onde disponível). Em Linux headless, oferecer cofre criptografado protegido por senha; **não** recair silenciosamente para plaintext.
- Rodar sem privilégios administrativos e sem abrir portas no firewall.
- Em `start`, exibir URL, versão, estado e localização dos logs **sem mostrar segredos**.

## Critérios de aceite

- Instalação e execução em máquinas limpas de Windows e Linux sem Python ou Node preexistente (caminho de binário).
- Start/stop/status/doctor, atalho, retenção de dados em update e desinstalação sem perda inesperada.
- Cada SO seleciona release apropriada e verifica integridade.
- Tokens são protegidos; nenhum arquivo sensível aparece no GitHub.
- DeepSeek Only / Grok Only / Hybrid e configuração individual de agentes funcionam com backend local.

**Leituras:** [CI/CD e releases](03-releases-e-estrutura.md) · [Licença](02-licenca-e-contribuicoes.md) · [Agentes](../02-arquiteturas/08-configuracao-e-perfis.md).

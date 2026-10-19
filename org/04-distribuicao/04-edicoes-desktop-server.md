# 04 · Edições Desktop e Server — decisão oficial de arquitetura

> [← Mapa Mestre](../README.md) · [↑ Distribuição](README.md) · [Instalação e comandos](01-instalacao-cli.md) · [Arquitetura das interfaces](../02-arquiteturas/09-desktop-server-core-compartilhado.md)

**Decisão de produto, 19/10/2026:** o MultAgent terá **duas edições executáveis**, Desktop e Server, compiladas para os sistemas-alvo. Não substituir Desktop por um site local, webview, Electron, Tauri ou navegador. A interface Desktop **não depende de Flask, FastAPI, localhost HTTP ou React**. Server é um programa headless separado, com serviço HTTP intencional.

## Matriz de distribuição

| Característica | MultAgent Desktop | MultAgent Server |
|---|---|---|
| Plataformas alvo iniciais | Windows 10/11 com GUI; Ubuntu/Debian Desktop | Windows Server; Ubuntu/Debian Server; também Windows/Linux com GUI quando desejado |
| Interface de operação | Janela real via PySide6 / Qt Widgets, com Qt Quick/QML opcional | Dashboard web React + TypeScript, servido pelo FastAPI |
| Motor de agentes | Biblioteca Python compartilhada | Mesma biblioteca Python compartilhada |
| Acesso a DeepSeek/Grok/MCP | Sim | Sim |
| Instalação | Script verificado via PowerShell/Bash que baixa pacote oficial | Script verificado via PowerShell/Bash que baixa pacote server |
| Executável principal | `multagent` no Linux; `multagent.exe` no Windows | `multagent-server` no Linux; `multagent-server.exe` no Windows |
| Comando para executar | `multagent` ou `multagent start` abre janela | `multagent-server start` inicia HTTP e workers, sem GUI |
| Porta de rede necessária? | **Não** | **Sim**; usuário escolhe na configuração |
| Acesso de outros computadores | **Não**, por padrão | Sim, somente se bind/firewall/autenticação/TLS autorizados |
| Banco inicial | SQLite local por perfil do OS | SQLite para instância simples; PostgreSQL recomendado para escala/multiusuário |
| Execução como serviço | Não exigida | Suporte planejado a Windows Service e systemd |

Qt/PySide6 é uma **GUI nativa de toolkit**, sem navegador integrado. Qt Widgets são o ponto inicial para formulários, listas, painéis, logs e edição de agentes; QML é opção para telas mais customizadas. Não incluir QtWebEngine no Desktop.

## CLI planejada — não existe código executável ainda

**Desktop:**

```text
multagent                       # abre imediatamente a janela do Desktop
multagent start                 # alias para abertura da GUI
multagent --version             # informa build e plataforma
multagent doctor                # diagnóstico técnico
multagent logs                  # mostra logs locais sem segredos
multagent update                # verifica release e atualiza com consentimento
```

Para abrir a janela sem terminal, o atalho aponta diretamente para o executável gráfico. Em Windows, a build GUI deve ser compilada sem janela de console permanente. No Linux, cria-se um arquivo `.desktop` opcional com ícone e `Exec`. Um servidor HTTP **não** é iniciado como efeito colateral de abrir a GUI. O Desktop pode executar agentes assincronamente sem bloquear o loop Qt usando workers/thread pools ou bridge assíncrona adequada.

**Server:**

```text
multagent-server init --port 8765 --bind 127.0.0.1   # assistente de instalação/configuração
multagent-server start                                 # inicia serviço e painel web
multagent-server status                                # estado, PID, listener e health
multagent-server stop                                  # gerenciador de processo, se habilitado
multagent-server logs                                  # logs sanitizados
multagent-server doctor                                # diagnósticos
multagent-server update                                # atualiza após verificação e consentimento
```

A porta `8765` acima é **somente exemplo configurável**, não porta obrigatória. Binding recomendado de fábrica: `127.0.0.1`. Para acesso remoto, operador escolhe endereço de bind da máquina, autenticação, TLS (direto ou reverse proxy) e regras de firewall. **Selecionar porta não equivale a expor na rede.** Solicitar confirmação e explicar riscos. A instalação não deve criar regra pública de firewall silenciosamente.

## Instalação de ambos (fluxo de produto)

1. O usuário escolhe **Desktop** ou **Server** na documentação da release.
2. No Windows, executa script `install.ps1` oficial; no Linux, `install.sh` oficial, após verificar procedência. O script aceita `--edition desktop|server` (ou parâmetro PowerShell equivalente), valida assinatura/checksum e usa binário da plataforma/arquitetura.
3. Desktop: instalação sem exigir configuração de porta. O usuário abre executável/atalho ou digita `multagent`.
4. Server: `init` interativo pergunta **porta**, **bind**, diretório de dados, política de acesso, usuário de serviço e se haverá auto-start. Os valores são validados e gravados no ambiente da instalação.
5. Cada edição abre painel próprio (Qt ou web server), com as mesmas abas **Integrações**, **Configurações**, **Funcionários/agentes**, **Execuções** e **Logs**, respeitadas diferenças de UX.
6. Após cadastrar chaves de API do próprio usuário, ele escolhe DeepSeek, Grok ou Hybrid e atribui cada funcionário a um modelo autorizado.
7. Atualizações preservam DB, credenciais e perfis; revogação de tokens e backups são funções explicitamente documentadas.

**Compatibilidade de sistema operacional deve ser testada em CI e máquinas limpas.** Bibliotecas Qt no Linux podem depender de Wayland/X11/plugins do SO; binário Windows não roda em Linux e vice-versa. Server não importa nem distribui dependências Qt.

## Responsabilidade por edição

Desktop é programa local de usuário único por padrão. Server pode servir uma ou mais contas/tenants, mas requer autenticação, autorização, quotas, TLS e persistência mais robusta quando exposto. A segurança da edição server não é automaticamente fornecida pelo Desktop.

## Empacotamento

- **Desktop:** `pyside6-deploy` (oficial, baseado em Nuitka) ou Nuitka standalone; empacotar ícones, plugins Qt e versões por SO/arquitetura. `standalone` (diretório com executável e dependências) é preferível inicialmente para instalação confiável, embora `onefile` exista.
- **Server:** empacotar Python core, FastAPI/Uvicorn e os arquivos estáticos React da mesma versão. Sem PySide6; build separado para reduzir tamanho e superfície de falhas.
- **Código open-source:** manter `src/multagent/core`, `providers`, `storage`, `tools` independentes de GUI, permitindo reuso sem duplicação.
- **Licença:** PySide6 usa LGPLv3/GPLv3 ou licença comercial; verificar obrigações de redistribuição e componentes Qt com a licença do MultAgent, ainda pendente. Texto oficial: https://doc.qt.io/qtforpython-6/ .

## Critérios de aceite independentes

**Desktop:** abrir `multagent` mostra janela real sem navegador, sem serviço HTTP, sem Node/Python instalados pelo usuário; abas operam e tokens ficam no cofre; fecha GUI/encerra workers sem resíduos. **Server:** `multagent-server start` funciona em Linux Server sem display; porta configurável e bind seguro, acesso web autenticado de host permitido, operação opcional via systemd/Windows Service; não importa PySide6.

Os comandos e scripts **ainda precisam ser implementados e publicados em GitHub Releases**. Evitar instruções que aparentem estar prontas.

**Fontes técnicas:** [Qt deployment](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html), [Qt licensing](https://doc.qt.io/qtforpython-6/), [Qt Nuitka](https://doc.qt.io/qtforpython-6/deployment/deployment-nuitka.html).

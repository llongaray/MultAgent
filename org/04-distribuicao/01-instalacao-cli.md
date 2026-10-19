# 01 · Instalação, execução e atalhos — Desktop e Server

> [← Mapa Mestre](../README.md) · [↑ Distribuição](README.md) · [Edições](04-edicoes-desktop-server.md) · [Releases](03-releases-e-estrutura.md)

## Regra principal

O terminal serve para **instalação, lançamento, atualização e diagnóstico**. O uso habitual do **Desktop ocorre em GUI Qt nativa**, não no navegador. A edição **Server** não precisa de GUI; recebe porta/bind configuráveis para que outros dispositivos autorizados usem o painel web hospedado.

**Comandos, scripts e URLs abaixo são contratos a desenvolver. Nenhum instalador/CLI foi publicado ainda.**

## Instalação planejada

1. Usuário escolhe a edição na Release pública: **Desktop** ou **Server** e sistema-alvo/arquitetura.
2. Obtém `install.ps1` (PowerShell Windows) ou `install.sh` (Bash Linux) de URL oficial; revisa o script e valida procedência.
3. Script identifica a edição e plataforma, baixa o pacote correspondente, verifica assinatura/checksum/attestation, instala em diretório adequado e disponibiliza o comando no PATH.
4. Desktop: finaliza a instalação; usuário executa `multagent` ou abre atalho, que mostra imediatamente a interface gráfica.
5. Server: executa `multagent-server init`; informa porta TCP, endereço bind, diretório de dados, credenciais administrativas e regime de execução. Depois executa `multagent-server start`.
6. Nas duas edições, usuário configura DeepSeek e/ou Grok e cadastra funcionários/agentes, atribuindo modelos, funções e ferramentas.

No caminho de binário oficial, o usuário **não precisa instalar Python/Node** separadamente. Cada bundle contém suas dependências necessárias; isto depende de testes reais nas plataformas alvo. O Server não inclui Qt; o Desktop não inclui nem inicia frontend React/servidor HTTP.

## CLI Desktop (planejada)

| Comando | Comportamento |
|---|---|
| `multagent` | abre janela nativa PySide6/Qt |
| `multagent start` | alias para abertura da interface gráfica |
| `multagent --version` | mostra versão/release/build |
| `multagent logs` | consulta logs locais sanitizados |
| `multagent doctor` | verifica credenciais, DB, componentes e conectividade opcional |
| `multagent update` | consulta release oficial, pede confirmação, atualiza com backup |

Atalho Windows aponta para `multagent.exe` compilado como aplicativo de janela (sem terminal console permanente); Linux fornece arquivo `.desktop` que executa `multagent` e mostra a GUI. Fechar a janela não deverá iniciar ou deixar rodando HTTP ocultamente. Agentes em background/auto-start fora da GUI exigirão projeto e consentimento específicos.

## CLI Server (planejada)

| Comando | Comportamento |
|---|---|
| `multagent-server init` | assistente inicial: porta, bind, acesso, dados e serviços |
| `multagent-server init --port 8765 --bind 127.0.0.1` | forma não interativa (porta apenas exemplo) |
| `multagent-server start` | inicia servidor headless e workers em foreground |
| `multagent-server status` | verifica processo e health da instância |
| `multagent-server stop` | encerra instância gerenciada em background/serviço, não processo externo |
| `multagent-server logs` | mostra logs sanitizados, opcionalmente com follow |
| `multagent-server update` | aplica versão verificada com backup/rollback quando possível |
| `multagent-server doctor` | avalia bind, porta, TLS/auth, banco e integridade |

**Uma porta pode ser escolhida pelo usuário, mas a aplicação só ficará acessível remotamente se `bind`, firewall, roteamento e políticas de segurança permitirem**. Valor inicial seguro: `127.0.0.1`, inacessível diretamente por outras máquinas. Ao escolher bind externo, exigir habilitação consciente de autenticação, TLS/reverse proxy e autorização, sem expor UI administrativa sem controle.

### Como rodará como serviço

Linux Server: `systemd` configurado por instalação/operador (usuário de serviço mínimo, arquivos privados). Windows Server: Windows Service, configurado por administrador. Não supor que iniciar no terminal cria serviço persistente; oferecer `service install` como funcionalidade futura explicitamente autorizada. Não abrir firewall de modo silencioso.

## Empacotamento e compatibilidade

- Desktop Windows 10/11: `multagent.exe` + libs Qt/Python no bundle; build e smoke test específicos.
- Desktop Ubuntu/Debian com ambiente gráfico: executável e plugins Qt compatíveis com Wayland/X11 e libs do sistema, sem dependência de browser.
- Server Windows Server/Linux headless: `multagent-server.exe`/`multagent-server`, FastAPI+Uvicorn, estáticos React e motor Python. Sem Qt e sem necessidade de display.
- Preferir `pyside6-deploy`/Nuitka standalone para Desktop; binários server podem usar empacotamento Python separado. Verificar glibc e bibliotecas nativas por distribuição suportada.
- Criar artefatos separados por edição/SO/arquitetura; atualizar dados do usuário sem sobrescrever cofre de credenciais.

## Segurança e licença

Desktop usa cofre Windows Credential Manager, Linux Secret Service/KWallet ou vault criptografado com desbloqueio adequado. Server usa secret manager/vault e ACL próprios, especialmente em sistemas multiusuário. Dados locais não são código-fonte; jamais enviar segredos do usuário para GitHub.

A licença oficial do projeto está pendente; Qt for Python oferece LGPLv3/GPLv3/comercial. O empacotamento open-source deverá observar as condições das libs incluídas. Veja [licença e contribuição](02-licenca-e-contribuicoes.md).

## Critérios de aceite

- Desktop: programa gráfico autêntico; `multagent` abre janela sem HTTP ou navegador; roda após instalação em Windows e Linux suportados sem Python pré-instalado.
- Server: roda em Linux Server headless e Windows Server; porta configurável; serviço responde somente conforme bind e política; autenticação obrigatória para acesso remoto.
- Ambos: mesmos agentes/modelos/validação de permissões, SQLite inicial, logs e custos; mudanças nos providers são aproveitadas pelo core único.

**Links relacionados:** [Edições](04-edicoes-desktop-server.md) · [Releases](03-releases-e-estrutura.md) · [Arquitetura compartilhada](../02-arquiteturas/09-desktop-server-core-compartilhado.md).

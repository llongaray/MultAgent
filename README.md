# MultAgent

Plataforma multiagente open-source em desenvolvimento com **Desktop GUI nativo PySide6/Qt** (sem navegador, sem HTTP local) e edição Server headless com FastAPI/React (P5), compartilhando o núcleo Python.

## Status da implementação

**Base P0–P4 implementada e versionada:** contratos tipados e permissões, SQLite, vault seguro, adapters DeepSeek/Grok, roteamento por modo/custo, funcionários/equipes, orquestração DAG, scheduler e janela Qt (Início, Funcionários, Integrações, Permissões, Execuções e Logs). A edição **Server** tem código inicial P5 com autenticação e dashboard React; workspaces e shell P6, integrações Git/SSH P7 e mecanismos de MCP/plugins/skills P8 estão em validação. **Instaladores self-contained e GitHub Releases ainda não foram publicados.** Consulte a [matriz de entregas e limites P5–P8](org/07-p5-p8-implementacao.md).

### Rodar a edição Desktop em desenvolvimento

É necessário Python >=3.11 e ambiente gráfico instalado. Em um clone local do repositório:

```bash
python -m pip install -e ".[desktop,dev]"
multagent
```

Diagnóstico via console:

```bash
multagent-cli doctor
multagent-cli logs
multagent-cli version
```

**Segurança:** integração de provedor via cofre seguro do sistema; sem keyring disponível, falha fechada. Envio para API externa requer preço informado, orçamento aprovado e confirmação humana; chamadas podem gerar cobrança do provedor. Os modelos listados são fornecidos pelo usuário e devem existir na conta do provedor. Ferramentas sugeridas por IA não são executadas automaticamente.

### Rodar o Server em desenvolvimento

Em máquina com Python 3.11+, obtenha o código e instale o módulo do Server:

```bash
python -m pip install -e ".[server,dev]"
multagent-server init --bind 127.0.0.1 --port 8765
multagent-server start
```

O comando `init` solicita uma senha administrativa. A interface React precisa ser compilada separadamente com `cd frontend-server && npm install && npm run build`, ou servir a aplicação em desenvolvimento com Vite. Exposição além de loopback exige TLS direto e `--allowed-host` configurado. Não exponha a administração à Internet sem validação operacional de segurança.

### Testes de desenvolvimento

```bash
python -m pytest -q
python -m ruff check src/multagent tests/unit --select E4,E7,E9,F
```

[Mapa mestre e documentação](org/README.md) · [Desktop vs Server](org/04-distribuicao/04-edicoes-desktop-server.md) · [Trello P0–P9](https://trello.com/b/1Ne1r8A2/multagent-desenvolvimento-e-prs-p0-p9).

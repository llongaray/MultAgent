# MultAgent

Plataforma multiagente open-source em desenvolvimento com **Desktop GUI nativo PySide6/Qt** (sem navegador, sem HTTP local) e futura edição Server headless com FastAPI/React, compartilhando o núcleo Python.

## Status da implementação

**Implementado na linha P0–P4 (sujeito à homologação):** contratos tipados e permissões, SQLite, vault seguro, adapters DeepSeek/Grok, roteamento por modo/custo, funcionários/equipes, orquestração DAG, scheduler e janela Qt (Início, Funcionários, Integrações, Permissões, Execuções e Logs). A edição **Server, instaladores self-contained e releases** são trabalho futuro — não há binários publicados.

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

### Testes de desenvolvimento

```bash
python -m pytest -q
python -m ruff check src/multagent tests/unit --select E4,E7,E9,F
```

[Mapa mestre e documentação](org/README.md) · [Desktop vs Server](org/04-distribuicao/04-edicoes-desktop-server.md) · [Trello P0–P9](https://trello.com/b/1Ne1r8A2/multagent-desenvolvimento-e-prs-p0-p9).

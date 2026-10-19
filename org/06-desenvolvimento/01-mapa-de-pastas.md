# 01 · Mapa físico de pastas e arquivos documentais

> [← Mapa Mestre](../README.md) · [↑ Guia de desenvolvimento](README.md) · [Contratos](02-contratos-e-dependencias.md)

**Criado no GitHub:** cada diretório apresentado abaixo tem um `README.md` com a finalidade do módulo, seus contratos futuros, limitações e testes planejados. Arquivos `.py`, `.tsx`, scripts `.sh`/`.ps1` e workflows YAML **não foram criados**.

## Organograma do repositório

```text
MultAgent/
├── README.md
├── org/                            # Documentação teórica e técnica existente
│   ├── 00-fundamentos/
│   ├── 01-provedores/
│   ├── 02-arquiteturas/
│   ├── 03-trilhas/
│   ├── 04-distribuicao/
│   ├── 05-integracoes/
│   └── 06-desenvolvimento/         # Este guia e seus contratos
├── src/
│   └── multagent/
│       ├── core/
│       │   ├── domain/            # Agent, Team, Run, Grant, Resource
│       │   ├── orchestrator/      # Coordenação de equipes
│       │   ├── router/            # DeepSeek / Grok / hybrid
│       │   ├── workflows/         # DAG, dependências e entregas
│       │   ├── scheduler/         # Fila e agenda
│       │   ├── approvals/         # Confirmações humanas
│       │   └── services/          # API interna do domínio
│       ├── agents/
│       │   ├── profiles/
│       │   └── teams/
│       ├── providers/
│       │   ├── deepseek/
│       │   └── grok/
│       ├── resources/
│       │   ├── workspaces/
│       │   └── registry/
│       ├── tools/
│       │   ├── gateway/
│       │   ├── mcp/
│       │   ├── plugins/
│       │   ├── skills/
│       │   ├── filesystem/
│       │   ├── shell/
│       │   └── desktop_automation/
│       ├── integrations/
│       │   ├── git/
│       │   ├── github/
│       │   ├── gitlab/
│       │   ├── bitbucket/
│       │   ├── ssh/
│       │   ├── apps/
│       │   ├── catalog/
│       │   └── oauth/
│       ├── security/
│       │   ├── vault/
│       │   ├── permissions/
│       │   ├── sandbox/
│       │   └── privilege_broker/
│       ├── storage/
│       │   ├── sqlite/
│       │   └── postgres/
│       ├── observability/
│       ├── desktop/
│       │   ├── views/
│       │   ├── viewmodels/
│       │   └── widgets/
│       ├── server/
│       │   ├── api/
│       │   ├── auth/
│       │   └── workers/
│       └── cli/
│           ├── desktop/
│           └── server/
├── frontend-server/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       └── state/
├── scripts/
│   ├── windows/
│   ├── linux/
│   └── release/
├── config/
│   ├── schemas/
│   └── templates/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── security/
│   ├── desktop/
│   └── server/
├── examples/
│   ├── agent-profiles/
│   ├── workflows/
│   └── integrations/
├── assets/
│   ├── icons/
│   └── branding/
└── .github/
    ├── workflows/
    └── ISSUE_TEMPLATE/
```

> O Git armazena **arquivos, não diretórios vazios**. Os diretórios são versionados porque cada um contém seu `README.md`. Não há necessidade de `.gitkeep`.

## Pontos de entrada dos módulos

- **[Core Python](../../src/multagent/core/README.md)** — domínio, workflows, aprovação e roteamento.
- **[Funcionários e equipes](../../src/multagent/agents/README.md)** — perfis e hierarquia.
- **[Ferramentas / MCP / skills](../../src/multagent/tools/README.md)** — capacidades controladas.
- **[Integrações Git, SSH, apps e catálogo](../../src/multagent/integrations/README.md)**.
- **[Segurança, vault, sandbox e broker](../../src/multagent/security/README.md)**.
- **[Desktop Qt](../../src/multagent/desktop/README.md)** — sem servidor HTTP.
- **[Server FastAPI](../../src/multagent/server/README.md)** + **[React Server](../../frontend-server/README.md)**.
- **[CLI](../../src/multagent/cli/README.md)**, **[instaladores](../../scripts/README.md)**, **[testes](../../tests/README.md)** e **[GitHub Actions](../../.github/README.md)**.

## Ordem de construção

Contratos e testes do core → GUI Desktop / edição Server → modelos DeepSeek/Grok → hierarquia de equipes e tarefas → workspaces Git → OAuth/SSH → catálogo MCP/plugins/skills → automação GUI → elevação por broker administrativo com controle rigoroso.

**Referências:** [Roteiro de implementação](../05-integracoes/05-caminho-de-implementacao.md) · [Propósito](../00-fundamentos/05-proposito-e-casos-de-uso.md).

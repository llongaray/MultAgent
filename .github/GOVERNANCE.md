# GitHub e governança do MultAgent

> [README principal](../README.md) · [Documentação técnica](../org/README.md) · [Fluxo de PRs](../org/06-desenvolvimento/05-fluxo-de-prs-e-prioridades.md)

Esta pasta contém arquivos reais de integração do projeto com o GitHub, incluindo workflows de CI e modelos de contribuição.

## Workflows disponíveis

| Workflow | Arquivo | O que verifica |
| --- | --- | --- |
| Python CI | [`python-ci.yml`](workflows/python-ci.yml) | Testes Python 3.11/3.13 no Ubuntu e Windows, compilação e Ruff |
| Desktop Qt smoke | [`desktop-ci.yml`](workflows/desktop-ci.yml) | Inicialização/contratos Qt (Ubuntu e Windows, Python 3.11) |
| Server React build | [`server-ui-ci.yml`](workflows/server-ui-ci.yml) | Compilação do painel React com Node.js |
| Branch promotion gate | [`promotion-gate.yml`](workflows/promotion-gate.yml) | Verifica a origem de PRs para `dev`, `hml` e `main` |

**Importante:** workflows e gate funcionam como checks, mas não impedem o push direto por conta própria. As **regras administrativas de proteção de branches** dependem de rulesets ativos no GitHub e confirmação de seu enforcement; não devem ser anunciadas como habilitadas apenas porque o YAML existe.

## Política do projeto

- Desenvolvimento em branch de tarefa, com PR destinado à **`dev`**.
- Promoção **`dev` → `hml`** para homologação.
- Promoção **`hml` → `main`** após aprovação explícita do proprietário.
- Mudanças sensíveis passam por revisão e testes compatíveis com seu risco.

Veja [governança OPS-P0](../docs/ops-p0-apply.md), [`CONTRIBUTING.md`](../CONTRIBUTING.md) e o [README principal](../README.md).

> **Estado da distribuição:** o código possui integração contínua, mas releases e instaladores independentes ainda não foram publicados.

# Contribuindo com o MultAgent

**Regra do projeto oficial:** todo código novo ou modificado entra por **Pull Request**, obedecendo prioridades **P0, P1, P2...**, com fluxo **PR do módulo → `dev` → `hml` para revisão do proprietário → `main` apenas com autorização expressa**.

Consulte [fluxo e matriz de prioridades](org/06-desenvolvimento/05-fluxo-de-prs-e-prioridades.md) e [governança](org/04-distribuicao/02-licenca-e-contribuicoes.md).

## Como contribuir

1. Escolha uma prioridade e módulo coeso; identifique PRs dos quais depende.
2. Crie branch `feat/p0-core-domain` (ou `fix/p2-providers-grok`); evite escopos monolíticos.
3. Entregue implementação do módulo **com testes e README técnico correspondente**.
4. Abra PR **contra `dev`** com título `feat(P0/core-domain): descreve a entrega`, usando o [template](.github/PULL_REQUEST_TEMPLATE.md).
5. Informe testes efetivamente executados, riscos, limitações, mudanças de segurança e impacto no Desktop/Server.
6. Aguarde revisão/verificações para integrar à **`dev`**. Quando pronto, promover **somente mudanças testadas** à **`hml`** por PR, disponibilizando-as para homologação do proprietário.
7. Se o proprietário pedir correções, corrigir novamente em `dev` e re-homologar. **Nunca mesclar em `main` antes de receber aprovação explícita.** Após aprovação, abrir/verificar PR `hml → main` e registrar o merge.

**Segurança:** não publicar credenciais, segredos ou dados privados. Core independente de UI; Desktop em Qt sem interface HTTP; Server autenticado. Agentes não devem executar com privilégio administrativo permanente. Ferramentas externas exigem autorização.

A regra de PR vale para **mudanças incorporadas ao repositório oficial**, não obriga usuários a publicarem modificações privadas. A licença final ainda não foi aprovada.

**Documentação:** [Mapa Mestre](org/README.md).

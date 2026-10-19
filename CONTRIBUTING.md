# Contribuindo com o MultAgent

**Regra do projeto oficial:** todo código novo ou modificado entra por **Pull Request**, obedecendo prioridades **P0, P1, P2...**, nunca por push direto na `main`.

Consulte [fluxo e matriz de prioridades](org/06-desenvolvimento/05-fluxo-de-prs-e-prioridades.md) e [governança](org/04-distribuicao/02-licenca-e-contribuicoes.md).

## Como contribuir

1. Escolha uma prioridade e módulo coeso; identifique PRs dos quais depende.
2. Crie branch `feat/p0-core-domain` (ou `fix/p2-providers-grok`); evite escopos monolíticos.
3. Entregue implementação do módulo **com testes e README técnico correspondente**.
4. Abra PR com título `feat(P0/core-domain): descreve a entrega`, usando o [template](.github/PULL_REQUEST_TEMPLATE.md).
5. Informe testes efetivamente executados, riscos, limitações, mudanças de segurança e impacto no Desktop/Server.
6. Aguarde revisão e verificações requeridas antes do merge; não fazer merge apenas porque o PR foi aberto.

**Segurança:** não publicar credenciais, segredos ou dados privados. Core independente de UI; Desktop em Qt sem interface HTTP; Server autenticado. Agentes não devem executar com privilégio administrativo permanente. Ferramentas externas exigem autorização.

A regra de PR vale para **mudanças incorporadas ao repositório oficial**, não obriga usuários a publicarem modificações privadas. A licença final ainda não foi aprovada.

**Documentação:** [Mapa Mestre](org/README.md).

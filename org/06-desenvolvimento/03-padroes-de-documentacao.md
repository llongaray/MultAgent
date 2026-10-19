# 03 · Padrões de documentação e evolução do repositório

> [← Mapa Mestre](../README.md) · [↑ Desenvolvimento](README.md) · [Mapa de pastas](01-mapa-de-pastas.md)

## Convenções

- Cada diretório técnico tem um `README.md` contendo: objetivo, contratos futuros, limites de acesso, validação e links de retorno.
- Toda documentação de produto permanece em `org/`, organizada por capítulo. Novos guias devem aparecer no [Mapa Mestre](../README.md).
- Usar Português (pt-BR), nomenclatura consistente entre `Agent`, `Team`, `Workflow`, `Resource` e `PermissionGrant`.
- Código e execução ainda não implementados devem ser identificados como **planejamento**; não apresentar um comando de exemplo como instalação funcional.
- Uma pasta no Git deve conter ao menos um arquivo. O `README.md` já cumpre essa função, sem `.gitkeep` adicional.
- Não publicar arquivos `.env`, segredos de OAuth, chaves de API ou hosts/arquivos de usuários no repositório.

## Desenvolvimento exclusivamente via PR por prioridade

Novos módulos e alterações de código passam por **branch e PR próprios**, com nomenclatura `P0`, `P1`, `P2`... e dependências declaradas, conforme [guia de prioridades](05-fluxo-de-prs-e-prioridades.md) e [CONTRIBUTING](../../CONTRIBUTING.md). Não fazer implementação diretamente na `main` nem reunir vários módulos independentes em PR monolítico.

## Organização de commits quando houver código

Mudanças no núcleo devem atualizar contratos e testes; mudanças na CLI devem alterar os guias de distribuição; novos plugins exigem permissões documentadas e avaliação de supply chain. Alterações aceitas no projeto oficial entram por Pull Request público, de acordo com a governança (não significa que todo fork privado deva publicar suas modificações).

## Pronto para a próxima fase quando

- O responsável pelo projeto aprovar a API interna e um conjunto inicial de agentes.
- A licença open-source definitiva estiver definida (AGPLv3 ainda em avaliação).
- Houver backlog de MVP Desktop e Server, permissões mínimas e tarefas de teste.
- O primeiro código puder ser integrado sem ferir a separação de interfaces/core e sem precisar executar como root/Administrador permanentemente.

**Fontes internas:** [Governança](../04-distribuicao/02-licenca-e-contribuicoes.md) · [Roadmap](../05-integracoes/05-caminho-de-implementacao.md).

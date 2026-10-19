# 02 · Licenciamento open-source e governança das alterações

> [← Mapa Mestre](../README.md) · [↑ Distribuição](README.md) · [Releases/CI](03-releases-e-estrutura.md)

## Objetivo declarado

O repositório MultAgent permanecerá **público e auditável**. As alterações que forem incorporadas **ao projeto oficial** deverão estar em commits públicos, com histórico de revisões, testes e versionamento. A intenção é que versões modificadas disponibilizadas a outras pessoas também disponibilizem o código correspondente, nos limites reais da licença escolhida.

## Escolha sugerida: GNU AGPLv3 (ainda não decidida)

A **GNU Affero General Public License versão 3** é forte candidata, pois protege a reciprocidade de código de versões **distribuídas** e, na `seção 13`, determina que quem modifica software e permite que usuários interajam remotamente com essa versão por rede ofereça acesso ao código-fonte correspondente. Ela é especialmente pertinente se o MultAgent também tiver usos como serviço web compartilhado.

A **GPLv3** exige obrigações de disponibilização de fonte no contexto de distribuição, mas em geral **não** adiciona a obrigação da AGPL específica à interação remota com versões modificadas.

Atenção: **nem GPLv3 nem AGPLv3 obrigam todas as modificações feitas privadamente a serem publicadas no GitHub ou contribuídas ao repositório do autor original**. A obrigação de fornecer código pode ser dirigida aos destinatários/usuários nos casos previstos; ela não implica abrir PR público. Não escreva no README "qualquer modificação privada deve ser publicada", pois isso seria uma afirmação errada. Também não é adequado chamar de licença open-source padrão um contrato personalizado que obrigue todos a publicar qualquer modificação, inclusive privada. Uma eventual exigência tão ampla demandaria análise jurídica própria e poderia deixar de ser compatível com critérios usuais de software livre.

Fontes oficiais:
- [AGPLv3 — texto oficial em português](https://www.gnu.org/licenses/agpl-3.0.pt-br.html) (seção 13).
- [FAQ GNU — publicar modificações](https://www.gnu.org/licenses/gpl-faq.en.html#GPLRequireSourcePostedPublic).
- [GPLv3 — texto oficial](https://www.gnu.org/licenses/gpl-3.0.html).

**PENDENTE DE APROVAÇÃO:** não criar `LICENSE` nem declarar o repositório "licenciado sob AGPLv3" antes de o titular decidir a licença e conferir compatibilidade das bibliotecas e direitos dos contribuidores.

## Regra do projeto oficial (independente da licença)

1. Todas as alterações **incorporadas ao MultAgent oficial** devem gerar commit público com autor, mensagem e diff.
2. Alterações propostas entram por Pull Request, vinculadas a issue/descritivo de mudança.
3. CI valida formatação, lint, testes, segurança, documentação e pacotes.
4. Pelo menos um revisor autorizado aprova antes do merge; branch `main` protegida contra push direto/force-push quando configurável.
5. Mudanças que alterem API/configuração ou CLI exigem atualização do `org/README.md`, dos manuais e de notas de versão.
6. Atualizações significativas requerem release tag semântica, changelog público e artefatos reconstruíveis a partir da tag.
7. Publicar resultados e limites reais dos testes; não declarar que executou testes não realizados.
8. Não exigir de usuários finais abrir PR para usar, adaptar ou atualizar configurações locais do software.

Essas são **políticas a implementar em GitHub Rulesets, workflows e documentação de contribuição** — ter este arquivo não ativa automaticamente proteções na conta.

## O que é modificação de código vs configuração pessoal?

- **Código-fonte:** alterações de arquitetura, handlers, adapters, integrações, UI ou scripts de build. Ao contribuir com o repositório oficial, passam pelo fluxo público.
- **Configuração do usuário:** chaves DeepSeek/Grok, perfis de funcionários, prompts próprios, tarefas, bancos locais e segredos. **Não devem ser enviados ao GitHub.**
- **Fork:** desenvolvedor pode criar sua própria versão respeitando a licença; abrir PR upstream é voluntário.

## Componentes externos e licença

Avaliar as licenças de Python, FastAPI, React, libs do vault, bibliotecas JS/TS, SDKs e ferramentas MCP. Incorporar notices e cumprir atribuições. As políticas de uso das APIs DeepSeek e xAI são **distintas da licença open-source do MultAgent**; chave e consumo continuam sendo de responsabilidade do usuário.

## Documentos adicionais planejados (não publicados ainda)

- Arquivo `LICENSE` com texto integral da licença escolhida.
- `CONTRIBUTING.md` com estilo, commits, PRs e comportamento.
- `SECURITY.md` para vulnerabilidades sem publicá-las antecipadamente.
- `CODE_OF_CONDUCT.md` e `.github/CODEOWNERS`.
- `.github/workflows/*.yml` para checks e releases.
- `CHANGELOG.md` e `NOTICE`/atribuições conforme dependências.

**Relacionado:** [Releases](03-releases-e-estrutura.md) · [Instalação CLI](01-instalacao-cli.md) · [Mapa mestre](../README.md).

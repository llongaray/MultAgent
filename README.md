# MultAgent

**Arquitetura multiagente modular**, em português brasileiro, com documentação de APIs oficiais DeepSeek e Grok/xAI, além de propostas independentes e híbridas. Nesta fase o repositório contém documentação técnica e desenho de software; **a aplicação MultiAgent ainda não foi implementada**.

## Comece por aqui

| Seção | Conteúdo |
|---|---|
| **[Arquitetura multiagente](docs/arquitetura/README.md)** | Componentes, modos DeepSeek Only / Grok Only / Hybrid, router, contratos e roadmap |
| **[DeepSeek API](docs/deepseek/README.md)** | Modelos, preços, endpoints, tools, MCP via orquestrador e exemplos em 10 linguagens |
| **[Grok / xAI API](docs/grok/README.md)** | Modelos, custos, Responses API, Search, MCP remoto, Python e JS/TS |

## Três modalidades

- **[Somente DeepSeek](docs/arquitetura/02-somente-deepseek.md)** — agentes com DeepSeek e ferramentas gerenciadas pelo backend.
- **[Somente Grok](docs/arquitetura/03-somente-grok.md)** — agentes com xAI Responses, tools geridas e MCP remoto opcional.
- **[Híbrido DeepSeek + Grok](docs/arquitetura/04-hibrido.md)** — router seleciona provedor por custo, capacidade, privacidade e qualidade.

### Documentos centrais

[Topologia](docs/arquitetura/01-visao-componentes.md) · [Roteamento e custo](docs/arquitetura/05-roteamento-e-custos.md) · [Contratos/adapters](docs/arquitetura/06-contratos-e-adapters.md) · [Configuração YAML](docs/arquitetura/08-configuracao-e-perfis.md) · [Roadmap](docs/arquitetura/07-plano-de-implementacao.md)

### Regra de segurança

Cada provedor tem sua própria chave e faturamento. Chaves **nunca** devem ser incluídas no repositório; fallback entre provedores depende de permissão explícita. Ferramentas MCP externas não são automaticamente confiáveis.

> **Revisão da documentação: 18/10/2026.** Modelos, preços, aliases e funcionalidades podem mudar. Consulte [DeepSeek oficial](https://api-docs.deepseek.com/) e [xAI oficial](https://docs.x.ai/developers). Exemplos didáticos não foram testados com credenciais autenticadas.

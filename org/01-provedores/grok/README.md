> **Navegação:** [← Mapa mestre](../../README.md) · [↑ Grok/xAI](README.md) · [Arquiteturas](../../02-arquiteturas/README.md) · [Outro provedor](../deepseek/README.md)

# API oficial do Grok (xAI) — documentação técnica

> Revisão: **18/10/2026**. Conteúdo em português elaborado para o **MultAgent**. Esta documentação é independente, não é afiliada à xAI e não substitui as [referências oficiais](https://docs.x.ai/developers). **Exemplos não executados com uma chave real**.

## Guia de leitura

1. [Modelos, versões, custos e recomendação](01-modelos-e-custos.md).
2. [Primeiros passos: conta, chave, modelo, cURL](02-primeiros-passos.md).
3. [REST/Responses API: referências, schemas e estado](03-referencia-api.md).
4. [Ferramentas: Function Calling, Web/X Search e MCP remoto](04-ferramentas-mcp.md).
5. [Python: integração com SDK OpenAI e xAI](05-python.md).
6. [JavaScript/TypeScript: Node.js e Vercel AI SDK](06-javascript-typescript.md).
7. [Segurança, operação, cache, custos e troubleshooting](07-operacao-seguranca.md).
8. [Fontes oficiais e procedimento de atualização](08-fontes.md).

## Regras práticas

- Plataforma oficial: [console.x.ai](https://console.x.ai/); API: `https://api.x.ai/v1`.
- Modelos para avaliar no MultAgent: `grok-build-0.1` (código), `grok-4.20-0309-reasoning` e `grok-4.20-0309-non-reasoning` (custo/capacidade), `grok-4.20-multi-agent-0309` (pesquisa gerenciada) e `grok-4.7` (qualidade/código).
- A família `grok-4.7` usa preferencialmente **Responses API**. Chat Completions é interface legada/depreciada para novos recursos avançados.
- Nem todo modelo citado é necessariamente autorizado para toda conta; confirme com `GET /v1/models` e o console.
- API de produção é **paga por uso**; assinatura do Grok no site/app X **não** é chave API.
- Proteja `XAI_API_KEY` apenas no backend; não use chave em navegador, repositório ou app distribuído.
- Grok oferece **MCP remoto nativo** na Responses API (sujeito à política de rede, confiança e autenticação de cada servidor).
- Existem diferenças significativas em estado conversacional, armazenamento, custos e ferramentas em relação à DeepSeek. Consulte o [índice da arquitetura conjunta](../../02-arquiteturas/README.md).

## Fontes iniciais

- [Guia principal](https://docs.x.ai/developers/quickstart)
- [Modelos](https://docs.x.ai/developers/models)
- [Preços](https://docs.x.ai/developers/pricing)
- [REST e autenticação](https://docs.x.ai/developers/rest-api-reference/inference)
- [Release Notes](https://docs.x.ai/developers/release-notes)


---

**Continuar:** [Mapa mestre](../../README.md) · [Grok/xAI](README.md) · [Comparação de provedores](../../00-fundamentos/03-por-que-deepseek-e-grok.md) · [Arquiteturas](../../02-arquiteturas/README.md).

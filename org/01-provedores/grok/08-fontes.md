> **Navegação:** [← Mapa mestre](../../README.md) · [↑ Grok/xAI](README.md) · [Arquiteturas](../../02-arquiteturas/README.md) · [Outro provedor](../deepseek/README.md)

# Fontes, termos e manutenção da documentação Grok/xAI

> Revisado em 18/10/2026. Resumos são autorais e não representam transcrição integral da documentação do fabricante. Não executamos consultas autenticadas à conta de API do repositório.

## Fontes oficiais primárias

| Tema | URL |
|---|---|
| Documentação inicial | https://docs.x.ai/developers |
| Guia de cadastro | https://docs.x.ai/developers/quickstart |
| Console/API key | https://console.x.ai/ |
| Modelos | https://docs.x.ai/developers/models |
| Preços | https://docs.x.ai/developers/pricing |
| Histórico de alterações | https://docs.x.ai/developers/release-notes |
| Grok 4.7 | https://docs.x.ai/developers/grok-4-7 |
| Grok 4.20 | https://docs.x.ai/developers/models/grok-4.20 |
| Grok Multi-Agent | https://docs.x.ai/developers/models/grok-4.20-multi-agent-0309 |
| Grok Build 0.1 | https://docs.x.ai/developers/models/grok-code-fast-1 |
| REST geral | https://docs.x.ai/developers/rest-api-reference/inference |
| Lista de modelos | https://docs.x.ai/developers/rest-api-reference/inference/models |
| Responses | https://docs.x.ai/developers/rest-api-reference/inference/responses |
| Function Calling | https://docs.x.ai/developers/tools/function-calling |
| Remote MCP | https://docs.x.ai/developers/tools/remote-mcp |
| Web Search | https://docs.x.ai/developers/tools/web-search |
| X Search | https://docs.x.ai/developers/tools/x-search |
| Custo efetivo da request | https://docs.x.ai/developers/cost-tracking |
| Cache | https://docs.x.ai/developers/advanced-api-usage/prompt-caching |
| Regiões | https://docs.x.ai/developers/advanced-api-usage/regions |
| Melhores práticas de texto | https://docs.x.ai/developers/model-capabilities/text/best-practices |

## Procedimento de revisão

1. Conferir `GET https://api.x.ai/v1/models` com sua chave de testes e comparar com os IDs referidos.
2. Abrir a página de preços e os cards dos modelos; revisar variações de contexto longo, cache, região e ferramentas.
3. Checar notas de versões/deprecações e recursos exclusivos da Responses API.
4. Rodar testes de contrato para Grok Only e Hybrid em conta com custo limitado.
5. Atualizar data e resultados medidos em PR, com fonte.
6. Validar separadamente termos, direitos, uso comercial e LGPD antes de implantar dados reais.
7. Não supor que subscrição do chatbot dá uso da API: credenciais e faturamento independentes.

## Escopo e limitações

Estes guias cobrem **integração textual, raciocínio, ferramentas e multimodal de entrada relevantes para o MultAgent**. Geração de áudio, imagem e vídeo, bem como management APIs, possuem interfaces e tabelas próprias no fabricante; não são implementadas aqui. Consulte as páginas oficiais quando essas capacidades fizerem parte do produto.


---

**Continuar:** [Mapa mestre](../../README.md) · [Grok/xAI](README.md) · [Comparação DeepSeek/Grok](../../00-fundamentos/03-por-que-deepseek-e-grok.md) · [Arquiteturas](../../02-arquiteturas/README.md).

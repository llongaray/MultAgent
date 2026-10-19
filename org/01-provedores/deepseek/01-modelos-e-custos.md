> **Navegação:** [← Mapa mestre](../../README.md) · [↑ DeepSeek](README.md) · [Arquiteturas](../../02-arquiteturas/README.md) · [Grok](../grok/README.md)

# Modelos, capacidades, preços e descoberta

> Revisado em **18/10/2026**. Fonte: [Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing/) e [GET /models](https://api-docs.deepseek.com/api/list-models/). Tarifas e versões variam com o tempo.

## Modelos da API hospedada

| ID a enviar no campo `model` | Versão na data da revisão | Texto | Imagem de entrada | Contexto | Saída máxima |
|---|---|---|---|---:|---:|
| `deepseek-flash` | DeepSeek-V4.1-Flash-1017 | sim | sim | 1.048.576 tokens | 393.216 tokens |
| `deepseek-v4-pro` | DeepSeek-V4-Pro-0813 | sim | não | 1.048.576 tokens | 393.216 tokens |

Ambos oferecem **thinking** e **non-thinking**, JSON Output, Tool Calls, Responses API, Anthropic API, prefix completion e FIM (beta; non-thinking). A saída é textual; suporte a receber imagens não significa gerar imagens. O limite de contexto compreende **entrada + saída**.

**Aliases legados** `deepseek-v4-flash` e `deepseek-v4-flash-vision-exp` podem ser aceitos, mas são direcionados à versão Flash atual. `deepseek-chat` e `deepseek-reasoner` pertencem a gerações anteriores e **não devem ser usados em código novo**. Modelos publicados com pesos abertos no Hugging Face **não estão necessariamente** expostos na API oficial.

## Consulta dinâmica obrigatória

```bash
curl -sS https://api.deepseek.com/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

O retorno inclui `data[]` com `id`, `name`, `context_window`, `max_output_tokens`, `input_modalities`, `output_modalities`, `effort.supported_levels`, `effort.default_level` e `api_capabilities`. Em sistemas reais, configure os modelos pelo ID retornado e mantenha um fallback seguro; não deduza que novos nomes suportam todos os recursos.

## Preços por 1 milhão de tokens (USD)

| Cobrança | Flash fora do pico | Flash no pico | Pro fora do pico | Pro no pico |
|---|---:|---:|---:|---:|
| Entrada com cache HIT | 0,003 | 0,006 | 0,022 | 0,044 |
| Entrada sem cache (MISS) | 0,15 | 0,30 | 0,66 | 1,32 |
| Saída | 0,60 | 1,20 | 1,98 | 3,96 |

**Pico:** segunda a sexta-feira, 01:00–04:00 e 06:00–10:00 UTC, exceto feriados públicos chineses. Demais horários são fora do pico. Preços são cobrados pelo consumo, não por requisição de texto.

**Custo estimado** = (tokens de entrada HIT × taxa HIT + tokens de entrada MISS × taxa MISS + tokens de saída × taxa saída) / 1.000.000. Use métricas `usage` da resposta para custo real; pensamento e tools podem afetar a contabilização.

Exemplo fora do pico, Flash: 10.000 tokens de entrada sem cache + 2.000 tokens de saída = **US$ 0,0027**.

## Search & Fetch (cobrança separada)

`POST /v1/tools/search` e `POST /v1/tools/fetch` custam, na tabela oficial da data de revisão, **US$ 0,75 por mil chamadas bem-sucedidas com resultado** cada um. Possuem limites próprios de 5 QPS por API. Consulte [Search & Fetch](https://api-docs.deepseek.com/guides/search/) para regras específicas de faturamento.

## Concorrência hospedada

`deepseek-flash`: **2.500** conexões simultâneas por conta. `deepseek-v4-pro`: **500**. Isso **não** representa requisições por segundo nem garantia de latência. As chaves da mesma conta compartilham quotas. Excesso pode devolver HTTP 429. Fonte: [Rate Limit & Isolation](https://api-docs.deepseek.com/quick_start/rate_limit/).

## Escolha rápida para o MultAgent

Use Flash por padrão em extração, chat e tarefas frequentes; teste Pro em planejamento complexo e decisões que exijam maior qualidade. Sempre faça benchmark com seus próprios casos, orçamento e políticas de dados. Confira os IDs via `/models` antes de implantar mudanças.


---

**Continuar explorando:** [Mapa mestre](../../README.md) · [DeepSeek](README.md) · [Grok/xAI](../grok/README.md) · [Arquitetura multiagente](../../02-arquiteturas/README.md).

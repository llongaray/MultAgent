> **Navegação:** [← Mapa mestre](../../README.md) · [↑ Grok/xAI](README.md) · [Arquiteturas](../../02-arquiteturas/README.md) · [Outro provedor](../deepseek/README.md)

# Referência REST — Grok (xAI)

## Base, autenticação e endpoints essenciais

Base de inferência: `https://api.x.ai/v1`. Header: `Authorization: Bearer $XAI_API_KEY`. Conteúdo JSON com `Content-Type: application/json`.

| Método | Endpoint | Objetivo |
|---|---|---|
| GET | `/v1/models` | Listar IDs acessíveis e metadados |
| GET | `/v1/models/{model_id}` | Consultar detalhes, aliases e preços |
| POST | `/v1/responses` | Chat, raciocínio, tools, inputs multimodais |
| GET | `/v1/responses/{response_id}` | Recuperar resposta armazenada |
| DELETE | `/v1/responses/{response_id}` | Excluir resposta armazenada |
| POST | `/v1/chat/completions` | Interface compatível/legada de Chat |
| Demais | Arquivos, collections, mídia, batch | Consulte referência especializada |

A **Responses API é preferida para aplicações novas**. Chat Completions é legado para raciocínio continuado, pois não preserva integralmente o estado criptografado entre turnos. [Referência REST](https://docs.x.ai/developers/rest-api-reference/inference), [Responses](https://docs.x.ai/developers/rest-api-reference/inference/responses).

## Requisição típica em Responses

```json
{
  "model": "grok-4.7",
  "input": [{"role":"user","content":"Proponha uma arquitetura em uma frase."}],
  "reasoning": {"effort":"low"},
  "max_output_tokens": 500,
  "store": false,
  "tools": []
}
```

Campos essenciais:
- `model` e `input` são o núcleo; valide que o modelo aceita a modalidade.
- `reasoning` pode configurar esforço em modelos compatíveis (Grok 4.7: low/medium/high/xhigh).
- `tools` lista funções, ferramentas do servidor e MCP remoto autorizados.
- `tool_choice` e `parallel_tool_calls` controlam chamadas de ferramentas nas combinações aceitas.
- `store` controla armazenamento da resposta no provedor; `previous_response_id` habilita continuidade em conversas armazenadas.
- `prompt_cache_key` fixa roteamento para favorecer cache.
- `max_output_tokens` ajuda a controlar custo e latência.
- `stream` emite eventos SSE; processe `response.output_text.delta` e eventos terminais, conforme contrato.
- Campos não suportados em Responses (como `presence_penalty` e `frequency_penalty`) não devem ser assumidos.
- Use `usage.cost_in_usd_ticks` quando disponível: 1 USD = 10^10 ticks.

## Estado e retenção

**Diferente do DeepSeek**, a Responses API da xAI **suporta `previous_response_id`** para conversas armazenadas. O guia informa armazenamento das respostas por **30 dias**, seguido de exclusão. Se usar `store: false`, não dependa da recuperação por ID: reenvie histórico no cliente. Retenção, ZDR e processamento regional exigem política explícita e avaliação de conformidade.

## Raciocínio criptografado

No `grok-4.7`, o retorno de Responses contém itens `reasoning.encrypted_content`. Para continuidade **stateless** é importante reenviar esses itens sem alteração, quando a API exigir; para continuidade armazenada pode-se utilizar `previous_response_id`. Não tente decriptar ou interpretar o conteúdo. Consulte [Best Practices](https://docs.x.ai/developers/model-capabilities/text/best-practices).

## Chat Completions (compatibilidade)

```bash
curl --fail-with-body -sS https://api.x.ai/v1/chat/completions \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"grok-4.7","messages":[{"role":"user","content":"Olá"}],"max_tokens":128}'
```

Use apenas para compatibilidade com código existente que depende de formato Chat. Para novos agentes/ferramentas e raciocínio, prefira Responses.

## Imagens e output estruturado

Os modelos que aceitam imagens podem receber `input_image` conforme contrato da Responses API; confira tamanho/formato por modelo (Grok 4.7: JPEG/PNG; limite geral de 20 MiB por imagem na documentação). JSON Schema/structured outputs precisam de validação pelo consumidor. Geração de imagens/vídeos não é a mesma API que entrada visual em texto.

## Ferramentas nativas

`web_search`, `x_search`, `code_interpreter` e `mcp` possuem schemas próprios. Veja [Ferramentas e MCP](04-ferramentas-mcp.md); **não** intercambie com os objetos `tools` do DeepSeek sem traduzir.

**Fontes:** [Responses](https://docs.x.ai/developers/rest-api-reference/inference/responses), [Models](https://docs.x.ai/developers/rest-api-reference/inference/models), [Best Practices](https://docs.x.ai/developers/model-capabilities/text/best-practices).


---

**Continuar:** [Mapa mestre](../../README.md) · [Grok/xAI](README.md) · [Comparação de provedores](../../00-fundamentos/03-por-que-deepseek-e-grok.md) · [Arquiteturas](../../02-arquiteturas/README.md).

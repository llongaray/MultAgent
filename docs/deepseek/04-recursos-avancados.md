# Recursos avançados, limitações e operação

## Thinking / reasoning

Os dois modelos hospedados permitem `reasoning_effort`: `none` (desliga thinking), `low`, `high` e `max`. Padrão documentado dos níveis de thinking: `high`. Também é possível enviar `thinking: {"type":"enabled"}` ou `{"type":"disabled"}`. Em SDK OpenAI que não expõe propriedades específicas DeepSeek, use `extra_body`; veja [Python](linguagens/python.md). A configuração do esforço pode mudar custos, tempo e resposta; compare nos seus workloads.

```json
{"model":"deepseek-flash","messages":[{"role":"user","content":"Calcule 17*19."}],"reasoning_effort":"low"}
```

## Vision — somente Flash

Suporta imagens JPEG, PNG, GIF e WebP; texto + imagem em `messages[].content`. Exemplo com URL pública:
```json
{
  "model":"deepseek-flash",
  "messages":[{"role":"user","content":[
    {"type":"text","text":"Descreva esta imagem."},
    {"type":"image_url","image_url":{"url":"https://example.com/foto.png","detail":"low"}}
  ]}]
}
```

`detail`: `low` (redução a 512×512), `high`, `original` ou `auto`. Formas de entrada: URL, base64 `data:` ou arquivo pela Files API. Não use Vision no `deepseek-v4-pro`.

Limites oficiais na data de revisão: **32 MiB** por imagem inline, **64 MiB** para imagem via `file_id`, corpo de requisição **48 MiB** e quantidade total de imagens condicionada aos limites do guia. Confira [Vision](https://api-docs.deepseek.com/guides/vision/) antes de enviar lotes.

## Files API

```bash
curl -sS https://api.deepseek.com/files \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -F 'purpose=user_data' \
  -F 'file=@imagem.png'
```

`purpose` deve ser `user_data`; upload máximo 64 MiB, máximo de 25 GiB e 10.000 arquivos por usuário na data verificada. Expiração opcional de 1 hora a 30 dias; **sem expiração configurada, o arquivo permanece armazenado** até exclusão conforme as políticas aplicáveis. Nunca envie dados sigilosos sem finalidade, autorização e política de retenção. [Guia Files](https://api-docs.deepseek.com/guides/files_api/).

## JSON estruturado

Use `response_format: {"type":"json_object"}` e peça explicitamente **JSON** no prompt, com exemplo do esquema esperado. O modo favorece JSON sintaticamente válido, mas **valide campos e tipos** em sua aplicação; respostas vazias e truncadas são possíveis.

```json
{
  "model":"deepseek-flash",
  "messages":[{"role":"user","content":"Retorne JSON com a propriedade status igual a ok."}],
  "response_format":{"type":"json_object"},
  "max_tokens":150
}
```

## Streaming (SSE)

Enviar `"stream": true` para Chat Completions. Resposta como `text/event-stream`, com linhas `data: {...}` e marcador `data: [DONE]`. Agregue `choices[0].delta.content`, inclusive argumentos de `tool_calls` por `index`; trate keep-alives SSE que começam com `:`. Nunca interprete um único chunk como JSON final. Cancelamento e desconexão precisam de suporte no cliente. [Streaming no Chat API](https://api-docs.deepseek.com/api/create-chat-completion/).

## Cache de contexto

Cache de prefixos é gerenciado pela plataforma, sem salvar memória de conversa. O uso/custo dos tokens de entrada com `cache hit` e `cache miss` pode ser diferente; observe os campos de `usage` e os preços oficiais. Não dependa de acertos de cache em cada request. [Context caching](https://api-docs.deepseek.com/guides/kv_cache/).

## Tool Calling

No Chat Completions, funções são descritas em JSON Schema com `tools:[{"type":"function","function":{...}}]`. Quando `finish_reason="tool_calls"`, a aplicação precisa executar cada função, validar os argumentos, adicionar mensagem `tool` e fazer nova chamada. A API **não** executa seu banco, shell, HTTP, MCP ou filesystem. Consulte [Multiagentes/MCP](05-multiagentes-mcp.md).

## Limites, retries e confiabilidade

- Simultaneidade por conta: Flash 2.500; Pro 500; exceder pode resultar em 429.
- Search/Fetch: 5 requisições por segundo por endpoint, por conta; Fetch tem limite adicional por domínio.
- Timeout de inferência: a plataforma pode enviar keep-alives; conexão pode ser encerrada se a inferência não começar em 10 minutos.
- Configure timeout HTTP conforme SLA do produto; retry **limitado** com backoff exponencial/jitter para 429/408/5xx. Evite repetir operações com efeito colateral e registrar prompt sensível.
- Não confunda concorrência com throughput. Implemente semáforos, fila por tenant e orçamento.
- Trate também `finish_reason=length`, `content_filter` e `insufficient_system_resource`.

## Segurança e governança

Credenciais em Secret Manager, TLS obrigatório, autorização por usuário/tenant, observabilidade sem PII em logs, criptografia em repouso, retenção mínima, checagem de licenças e conformidade com LGPD. Conteúdo externo e resultados web são não confiáveis: proteja contra prompt injection e validação fraca de ferramentas.

**Fontes:** [Thinking](https://api-docs.deepseek.com/guides/thinking_mode/), [Vision](https://api-docs.deepseek.com/guides/vision/), [Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/), [JSON](https://api-docs.deepseek.com/guides/json_mode/), [Limites](https://api-docs.deepseek.com/quick_start/rate_limit/).

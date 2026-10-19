> **Navegação:** [← Mapa mestre](../../README.md) · [↑ DeepSeek](README.md) · [Arquiteturas](../../02-arquiteturas/README.md) · [Grok](../grok/README.md)

# Referência REST — URLs, parâmetros e formatos

**Base oficial OpenAI-compatível:** `https://api.deepseek.com`. Suporte a `/v1` depende do protocolo/cliente; use os paths listados aqui. Header principal: `Authorization: Bearer $DEEPSEEK_API_KEY`. Para JSON: `Content-Type: application/json`.

## Mapa de endpoints

| Método | Caminho | Função |
|---|---|---|
| GET | `/models` | Modelos disponíveis e metadados |
| POST | `/chat/completions` | Conversação, imagens, JSON, thinking, funções |
| POST | `/responses` | Responses API; contexto controlado pelo cliente |
| GET | `/user/balance` | Saldo e moeda |
| POST | `/completions` | FIM beta; usar base `/beta` |
| POST | `/files` | Upload `multipart/form-data` de imagem |
| GET | `/files` | Lista paginada de imagens |
| GET | `/files/{file_id}` | Metadados de um arquivo |
| DELETE | `/files/{file_id}` | Remove arquivo |
| POST | `/v1/tools/search` | Busca web (API independente) |
| POST | `/v1/tools/fetch` | Extrai página web (API independente) |

Referências oficiais: [Chat](https://api-docs.deepseek.com/api/create-chat-completion/), [Responses](https://api-docs.deepseek.com/api/create-response/), [Modelos](https://api-docs.deepseek.com/api/list-models/), [Saldo](https://api-docs.deepseek.com/api/get-user-balance/), [Files](https://api-docs.deepseek.com/guides/files_api/), [Search](https://api-docs.deepseek.com/guides/search/).

## Chat Completions (`POST /chat/completions`)

Payload básico:
```json
{
  "model": "deepseek-flash",
  "messages": [
    {"role":"system","content":"Seja objetivo."},
    {"role":"user","content":"Olá"}
  ],
  "reasoning_effort":"low",
  "stream":false,
  "max_tokens":256
}
```

Campos usuais: `model` (obrigatório), `messages` (obrigatório), `stream`, `max_tokens`, `thinking: {"type":"enabled"|"disabled"}`, `reasoning_effort: "none"|"low"|"high"|"max"`, `temperature`, `top_p`, `stop`, `response_format`, `tools` e `tool_choice`. Alguns parâmetros variam por modelo e modo; consulte schema para valores/ranges e combinações. `tool_choice="required"` e escolha forçada de ferramenta podem retornar 400 no modo thinking: desative-o nesses casos.

Formato ilustrativo de resposta (campos omitidos):
```json
{
  "id":"...",
  "model":"deepseek-flash",
  "choices":[
    {"finish_reason":"stop","message":{"role":"assistant","content":"Olá!"}}
  ],
  "usage":{"prompt_tokens":12,"completion_tokens":4,"total_tokens":16}
}
```

Verifique sempre `choices`, `finish_reason` (`stop`, `length`, `tool_calls`, `content_filter` e erros de recursos), `message.content` e `message.tool_calls`. Em modo thinking pode existir `message.reasoning_content`; evite registrar/mostrar raciocínio privado nos logs.

## Responses API (`POST /responses`)

```json
{"model":"deepseek-flash","input":"Resuma DNS em uma frase.","max_output_tokens":128}
```

A Responses API é **stateless**: não permite continuidade via `previous_response_id` ou `conversation`. Reenvie o histórico e resultados de ferramentas a cada turno. Suporta `input` textual ou itens, `instructions`, `tools` (funções; busca web integrada nas condições documentadas para V4 Pro), `reasoning` e `text.format`; campos de OpenAI como `store`, `background` e `metadata` não implementam armazenamento ou trabalho em segundo plano na DeepSeek. Ferramentas MCP declaradas nessa API **não são executadas automaticamente**. [Guia de compatibilidade](https://api-docs.deepseek.com/guides/responses_api/).

## Lista de modelos

`GET /models` devolve `{"object":"list","data":[...]}`. Leia `data[i].id` e capacidades; não codifique um catálogo estático para sempre.

## Saldo

```bash
curl -sS https://api.deepseek.com/user/balance \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

Retorno: `is_available` e `balance_infos[]` (`currency`, `total_balance`, `granted_balance` e `topped_up_balance`), geralmente como strings decimais.

## Search & Fetch

Busca:
```bash
curl -sS https://api.deepseek.com/v1/tools/search \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"documentação REST DeepSeek","count":5,"need_content":false}'
```

Extração:
```bash
curl -sS https://api.deepseek.com/v1/tools/fetch \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

`search` retorna `results[]` (URL, título, resumo e metadados); `fetch` retorna `title` e `content` em Markdown. Ambos são **serviços cobrados e limitados separadamente**. Nunca permita URLs arbitrárias de usuários serem buscadas automaticamente sem avaliar políticas de SSRF, segurança e privacidade.

## Files API

`POST /files` usa multipart com `file` (imagem JPEG/PNG/GIF/WebP) e `purpose=user_data`. Limite por upload: 64 MiB. Retorna `file-api-...`, utilizável em `content:[{"type":"file","file_id":"..."}]` no Chat Flash. [Manual de imagens e arquivos](04-recursos-avancados.md).

## FIM beta

Base `https://api.deepseek.com/beta`, `POST /completions` com `model` e `prompt`; opcionalmente `suffix` para completar um trecho. Recurso beta e restrito a non-thinking. [Referência FIM](https://api-docs.deepseek.com/api/create-completion/).

## Protocolo Anthropic

Base `https://api.deepseek.com/anthropic` para SDK Anthropic. Os nomes e campos podem ser mapeados; `mcp_servers` é ignorado no protocolo, e a implementação não é 100% equivalente à Anthropic. [Detalhes oficiais](https://api-docs.deepseek.com/guides/anthropic_api/).


---

**Continuar explorando:** [Mapa mestre](../../README.md) · [DeepSeek](README.md) · [Grok/xAI](../grok/README.md) · [Arquitetura multiagente](../../02-arquiteturas/README.md).

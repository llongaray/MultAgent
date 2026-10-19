> **Navegação:** [← Mapa mestre](../../README.md) · [↑ DeepSeek](README.md) · [Arquiteturas](../../02-arquiteturas/README.md) · [Grok](../grok/README.md)

# Protocolo Anthropic-compatível na DeepSeek

> Fonte: [Using the Anthropic API](https://api-docs.deepseek.com/guides/anthropic_api/). Este protocolo é **alternativo** ao OpenAI/Chat e não indica que os modelos são Claude.

## Quando utilizar

A DeepSeek expõe uma API compatível com o ecossistema Anthropic em `https://api.deepseek.com/anthropic`. É útil em ferramentas que exigem formato de mensagens Anthropic (SDK, clientes de coding assistant e frameworks de agentes). Prefira o ID real `deepseek-flash` ou `deepseek-v4-pro`.

## Exemplo Python (Anthropic SDK)

```bash
python -m pip install --upgrade anthropic
```

```python
import os
from anthropic import Anthropic

client = Anthropic(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/anthropic",
)
message = client.messages.create(
    model="deepseek-flash",
    max_tokens=300,
    system="Responda em português brasileiro.",
    messages=[{"role":"user","content":"Explique APIs compatíveis."}],
)
for block in message.content:
    if block.type == "text":
        print(block.text)
```

## Exemplo cURL

No cliente HTTP puro, use a rota e versão conforme o protocolo Anthropic:
```bash
curl --fail-with-body -sS https://api.deepseek.com/anthropic/v1/messages \
  -H "x-api-key: $DEEPSEEK_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-flash","max_tokens":200,"messages":[{"role":"user","content":"Olá"}]}'
```

## Mapeamento de nomes legados de Claude

O gateway mapeia nomes iniciados em `claude-opus` para `deepseek-v4-pro` e os iniciados em `claude-sonnet`/`claude-haiku` para `deepseek-flash`. Isso **não** muda o provedor, modelo de fato usado, licença nem custo cobrado. O melhor é definir explicitamente o ID DeepSeek.

## Limitações reais do gateway

- Campos como `mcp_servers`, `service_tier` e `container` são ignorados.
- `tools` e `tool_choice` funcionam conforme tabela de compatibilidade, mas a execução da ferramenta continua sendo responsabilidade da aplicação.
- `max_tokens`, `system`, `stream`, `temperature` e `stop_sequences` são suportados; outros campos variam por modelo.
- `metadata.user_id` suporta isolamento por usuário técnico (não envie dados pessoais).
- `citations`, blocos `document` e diversos tipos de conteúdo Anthropic não são suportados.
- Para imagens do Files API, alguns paths Anthropic exigem `anthropic-beta: files-api-2025-04-14`.
- Ao migrar um framework, compare schema de respostas, thinking e streaming, não apenas baseURL.

## Acesso a arquivos no formato Anthropic

Endpoints sob `/anthropic/v1/files` exigem header beta `anthropic-beta: files-api-2025-04-14`. As estruturas de paginação e metadados diferem da versão OpenAI. Veja [Files API](https://api-docs.deepseek.com/guides/files_api/).

## Aplicação ao MultAgent

Use um adaptador por protocolo, mantendo no domínio interno tipos neutros (`Message`, `ToolCall`, `ToolResult`). Nunca misture formatos Anthropic e OpenAI no mesmo payload. Teste ferramentas e conteúdo multimodal com cada versão de SDK.

**Fontes:** [Anthropic API](https://api-docs.deepseek.com/guides/anthropic_api/), [Models](https://api-docs.deepseek.com/quick_start/pricing/).


---

**Continue:** [Mapa mestre](../../README.md) · [DeepSeek](README.md) · [Grok/xAI](../grok/README.md) · [Arquitetura multiagente](../../02-arquiteturas/README.md).

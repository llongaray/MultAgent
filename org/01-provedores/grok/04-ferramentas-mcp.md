> **Navegação:** [← Mapa mestre](../../README.md) · [↑ Grok/xAI](README.md) · [Arquiteturas](../../02-arquiteturas/README.md) · [Outro provedor](../deepseek/README.md)

# Ferramentas Grok, Function Calling e MCP remoto

## Ferramentas disponíveis na Responses API

| Tipo | Execução | Observação |
|---|---|---|
| `function` | **Cliente/orquestrador** | modelo solicita; seu backend valida/executa |
| `web_search` | **Servidor xAI** | busca web com cobrança por invocação |
| `x_search` | **Servidor xAI** | consulta posts/perfis X com cobrança por itens recuperados |
| `code_interpreter` / `code_execution` | **Servidor xAI** | sandbox hospedado; custos e política próprios |
| `mcp` | **Servidor xAI ↔ servidor remoto** | xAI conecta ao servidor MCP HTTPS configurado |
| `file_search`/collections | **Servidor xAI** | RAG e armazenamento podem gerar despesas próprias |

**Atenção:** MCP remoto da xAI **não é o mesmo** que conectar o modelo diretamente a um MCP local `localhost`. O provedor precisa acessar a URL remotamente. Se for MCP privado/interno, prefira cliente MCP dentro do orquestrador ou uma ponte autenticada com política clara.

## 1. Function Calling: a aplicação executa

```json
{
  "model": "grok-4.20-0309-non-reasoning",
  "input": [{"role":"user","content":"Qual o estoque de ABC?"}],
  "tools": [{
    "type": "function",
    "name": "consultar_estoque",
    "description": "Consulta estoque para SKU do tenant autorizado.",
    "parameters": {
      "type": "object",
      "properties":{"sku":{"type":"string"}},
      "required":["sku"],
      "additionalProperties":false
    }
  }]
}
```

Quando retornar item `type="function_call"` em `output`, decode `arguments`, valide JSON Schema, permissões e tenant, execute função local e continue com um `{"type":"function_call_output","call_id":"...","output":"..."}` em nova solicitação, opcionalmente com `previous_response_id`. Nunca permita execução arbitrária de SQL, shell ou HTTP pedida pelo modelo.

## 2. Remote MCP nativo

```json
{
  "model": "grok-4.7",
  "input": "Descreva os recursos públicos deste repositório.",
  "tools": [{
    "type": "mcp",
    "server_label": "deepwiki",
    "server_url": "https://mcp.deepwiki.com/mcp"
  }]
}
```

A xAI gerencia a conexão de MCP **remoto**. Parâmetros `require_approval` e `connector_id` do protocolo OpenAI Responses **não são suportados pela xAI**; implemente consentimento e autorização fora dessa opção. **Não** exponha servidores MCP internos sem TLS, autenticação, limitações de escopo e separação de ferramentas de escrita/leitura.

## 3. Web Search e X Search

```json
{
  "model":"grok-4.7",
  "input":"Compare notícias técnicas recentes com fontes.",
  "tools":[{"type":"web_search"},{"type":"x_search"}]
}
```

Ferramentas geridas podem executar múltiplas buscas. Defina limites de turnos/fetch, exija citações e acompanhe `usage.server_side_tool_usage_details`. X Search é cobrada por posts/perfis recuperados conforme tabela atual; buscar o mesmo post mais de uma vez pode cobrar novamente.

## 4. Auditoria de ferramentas

- Permitir explicitamente apenas as ferramentas exigidas pela tarefa.
- Validar argumentos, resultados, tipos e autorização por tenant.
- Impor timeout, orçamento e máximo de iterações para ferramentas cliente e servidor.
- Sanitizar conteúdo vindo de páginas e MCP para reduzir prompt injection.
- Não presumir que o servidor devolverá o conteúdo bruto de cada chamada interna; utilize métricas e citações de resultados.
- Se precisar de supervisão humana para ferramentas sensíveis, intercepte no seu orquestrador.

**Documentação oficial:** [Function Calling](https://docs.x.ai/developers/tools/function-calling), [Remote MCP](https://docs.x.ai/developers/tools/remote-mcp), [Web Search](https://docs.x.ai/developers/tools/web-search), [X Search](https://docs.x.ai/developers/tools/x-search), [Tool Usage](https://docs.x.ai/developers/tools/tool-usage-details).


---

**Continuar:** [Mapa mestre](../../README.md) · [Grok/xAI](README.md) · [Comparação DeepSeek/Grok](../../00-fundamentos/03-por-que-deepseek-e-grok.md) · [Arquiteturas](../../02-arquiteturas/README.md).

# Integração com Multiagentes, MCP e ferramentas

## Visão proposta para o MultAgent

```text
Interface HTTP / CLI
        |
    Orquestrador (Python FastAPI ou Node)
        |
   Planejador/Router -- roteamento por custo e capacidade
    |       |
 Flash      Pro    <-- DeepSeek API
    |       |
  Executor validado de ferramentas
   |        |         |
  MCP      SQL       Search/Fetch
   |
 Logs estruturados + memória de aplicação + budget + auditoria
```

A API da DeepSeek fornece **inferência de modelo**. Agentes, planejamento multi-turno, persistência, MCP client/server e autorização ficam na sua aplicação. Flash para volume e visão; Pro para tarefas complexas, sempre medindo resultados.

## Ciclo de Function Calling

1. Declare funções permitidas e seus parâmetros com JSON Schema.
2. Envie `messages` e `tools` ao Chat Completions.
3. Se o modelo devolver `tool_calls`, examine cada `function.name` e `function.arguments`.
4. Verifique **allowlist, schema, autorização e orçamento** antes de chamar qualquer ação.
5. Execute a função no seu processo ou em MCP com timeout, isolamento e logs auditáveis.
6. Acrescente a mensagem de `assistant` contendo `tool_calls` e, para cada chamada, uma mensagem `role: "tool"` com `tool_call_id` e resultado serializado.
7. Faça outra chamada, até resposta final ou limite de iterações.

### Exemplo de descrição da ferramenta

```json
{
  "type":"function",
  "function":{
    "name":"consultar_estoque",
    "description":"Consulta estoque de um SKU autorizado.",
    "parameters":{
      "type":"object",
      "properties":{"sku":{"type":"string"}},
      "required":["sku"],
      "additionalProperties":false
    }
  }
}
```

> Uma chamada de função **não autoriza** automaticamente a execução: valide, limite e exija confirmação para ações destrutivas, financeiras ou que publiquem dados.

## Pseudocódigo confiável

```text
histórico = [system, user]
para passo = 1..MAX_STEPS:
    resultado = chamar_deepseek(histórico, tools=catálogo_permitido)
    mensagem = resultado.choices[0].message
    adicionar mensagem de assistant ao histórico
    se não houver tool_calls:
        retornar mensagem.content
    para chamada em mensagem.tool_calls:
        argumentos = JSON.parse(chamada.function.arguments)
        validar_schema_e_permissões(argumentos, chamada.function.name)
        saída = executar_com_timeout_e_limite(chamada.function.name, argumentos)
        adicionar {role:tool, tool_call_id:chamada.id, content:JSON(saída)}
falhar_com_limite_de_passos
```

Código Python do ciclo: [linguagens/python.md](linguagens/python.md#exemplo-com-function-calling). Código JS básico: [JavaScript](linguagens/javascript-typescript.md).

## MCP — o que faz e o que não faz

**Model Context Protocol** é um protocolo para conectar agentes a ferramentas/recursos externos. O DeepSeek Chat API suporta `function tools`; **não é um cliente MCP autônomo**. No protocolo Anthropic-compatível, `mcp_servers` é ignorado; na Responses API, tipos MCP nativos não são executados como um serviço de MCP pela DeepSeek. Crie um **cliente MCP no orquestrador**, que:
- descubra ferramentas do servidor MCP autorizado;
- adapte `inputSchema` para JSON Schema de uma `function`;
- envie catálogo ao modelo, respeitando escopo por usuário;
- valide chamadas, encaminhe ao servidor MCP e normalize resultados;
- mantenha autenticação, consentimento e auditoria fora do modelo.

Não exponha diretamente um servidor MCP administrativo na internet sem autenticação, TLS, controle de origem, credenciais rotativas e isolamento.

## Memória de conversas e agentes

Chat e Responses exigem que a aplicação reconstrua contexto; `previous_response_id` não persiste estado na DeepSeek. Salve apenas dados necessários e com consentimento. Use resumos e RAG (PostgreSQL com índice vetorial, se aplicável), expirando dados conforme política. A persistência e a indexação são **da sua aplicação**, não uma garantia da API.

## Operação multi-tenant

Use tenant_id interno, autorização por ferramenta, quotas por tenant, budget em USD por execução, registros de `model` / `usage` / `finish_reason` / latência e mecanismo circuit breaker. `user_id` da API pode auxiliar isolamento/scheduling, mas **não deve conter informações pessoais** e não substitui a autorização no backend.

## Ferramentas de busca

Você pode integrar `POST /v1/tools/search` e `POST /v1/tools/fetch` separadamente. A busca web na Responses API é suportada sob condições específicas para V4 Pro, enquanto o serviço independente Search & Fetch possui autenticação e cobrança próprias. Não presuma disponibilidade de browsing nativo em todo modelo.

## Checklist de segurança de ferramentas

- Somente nomes de ferramentas explicitamente permitidos; nunca executar comandos ou SQL arbitrários gerados pelo modelo.
- Validar JSON Schema, tipos, tamanhos, IDs e recursos específicos por tenant.
- Exigir confirmação humana em operações irreversíveis.
- Impor limite de passos, tempo, tokens, simultaneidade e custo.
- Sanitizar dados externos contra prompt injection.
- Medir resultados de agentes e manter trilha auditável.

**Fontes:** [Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/), [Responses](https://api-docs.deepseek.com/guides/responses_api/), [Anthropic](https://api-docs.deepseek.com/guides/anthropic_api/), [Rate Limit](https://api-docs.deepseek.com/quick_start/rate_limit/).

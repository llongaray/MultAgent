> **Navegação:** [← Mapa mestre](../README.md) · [↑ Arquiteturas](README.md) · [DeepSeek](../01-provedores/deepseek/README.md) · [Grok/xAI](../01-provedores/grok/README.md)

# Contratos neutros, interfaces Provider e ferramentas

> Especificação de software **proposta**, não SDK pronto.

## Regra de ouro

**NÃO** transmitir o objeto de request/resposta de um provider ao outro. Normalize no domínio e converta via adapters separados. DeepSeek tem Chat Completions stateless; Grok deve usar Responses API com opções explícitas de retenção.

## Estrutura sugerida de pastas (implementação futura)

```text
multagent/
  app/
    api/
    core/
      domain/          # Task, AgentResult, ToolCall, Usage
      orchestrator/
      router/
      policies/
      budget/
      storage/
    providers/
      base.py
      deepseek.py
      grok.py
      registry.py
    tools/
      gateway.py
      mcp_client.py
      validation.py
    agents/
      planner.py
      researcher.py
      coder.py
      reviewer.py
    observability/
  tests/
    unit/
    contract/
    integration/
    e2e/
  config/
    model_catalog.example.yaml
    agent_profiles.example.yaml
```

## Contrato canônico de solicitação

```json
{
  "run_id":"UUID",
  "tenant_id":"tenant_anonimo",
  "mode":"hybrid",
  "allowed_providers":["deepseek","grok"],
  "task":{"role":"coder","instruction":"Revisar um código Python"},
  "input":{"text":"Código disponível como artefato autorizado"},
  "restrictions":{
    "sensitivity":"internal",
    "allow_external_tools":false,
    "max_cost_usd":0.10,
    "max_steps":6
  }
}
```

## Contrato canônico de resultado

```json
{
  "run_id":"UUID",
  "task_id":"task-01",
  "status":"completed",
  "provider":"grok",
  "model_id":"grok-4.20-0309-reasoning",
  "text":"Revisão concluída",
  "artifacts":[],
  "tool_requests":[],
  "usage":{
    "input_tokens":1200,
    "cached_input_tokens":0,
    "output_tokens":400,
    "cost_usd":0.0025,
    "cost_kind":"actual"
  },
  "warnings":[]
}
```

Não inclua tokens secretos ou raciocínio privado nestes contratos. Exemplo de custo é ilustrativo.

## Interface Python proposta

```python
from dataclasses import dataclass
from typing import Any, Literal, Protocol

@dataclass(frozen=True)
class AgentTask:
    role: str
    instruction: str
    context: dict[str, Any]
    max_output_tokens: int

@dataclass(frozen=True)
class AgentResult:
    provider: Literal["deepseek","grok"]
    model_id: str
    text: str
    input_tokens: int
    output_tokens: int
    cost_usd: float | None  # pode ser estimado
    cost_kind: Literal["actual","estimated","unknown"]

class ModelProvider(Protocol):
    async def list_models(self) -> list[str]: ...
    async def generate(self, task: AgentTask, *,
                       model_id: str) -> AgentResult: ...
```

Os adapters devem implementar validação e conversão dos contratos e erros de provider. Eventual streaming e funções/multimodal exigirão interfaces adicionais, não cast forçado.

## Tools / MCP

`ToolSpec`: `name`, `description`, `parameters_schema`, `tenant_scope`, `side_effect`, `approval_required`. `ToolCall`: `id`, `name`, `arguments`. `ToolResult`: `id`, `ok`, `content`, `duration_ms`.

No DeepSeek: enviar `tools` com objeto `{"type":"function","function":{...}}`; receber `message.tool_calls`; devolver `role:"tool"` e `tool_call_id`.

No Grok Responses: enviar `tools` com `{"type":"function","name":...}`; receber `output[].type="function_call"`; devolver `type:"function_call_output"` com `call_id`. Grok também aceita `{"type":"mcp","server_label":...,"server_url":...}`, apenas para servidores autorizados. Interface neutra garante implementação coerente.

## Regras fundamentais

- Idempotência por `run_id + task_id + call_id` para operações de escrita.
- Validar argumentos com JSON Schema e política de acesso.
- Retentativa de geração é diferente de retentativa de executar ferramenta.
- Persistir a versão exata de `router_policy` e `model_catalog` por run.
- Se houver dados confidenciais, negar cruzamento de provider não autorizado.
- Resultado de LLM é dado não confiável até validação determinística.

## Integração com histórico

Use armazenamento da aplicação para estado canônico. Para Grok, armazenamento opcional com `previous_response_id` é uma otimização da plataforma, não única fonte de verdade. Para DeepSeek, reconstruir histórico de chat. Não misturar raciocínio criptografado de Grok em prompts de outro modelo.

Ver também [visão geral](01-visao-componentes.md), [roteador](05-roteamento-e-custos.md) e [segurança do Grok](../01-provedores/grok/07-operacao-seguranca.md).


---

**Leituras relacionadas:** [Mapa mestre](../README.md) · [Fundamentos](../00-fundamentos/README.md) · [Modelos DeepSeek](../01-provedores/deepseek/README.md) · [Modelos Grok](../01-provedores/grok/README.md).

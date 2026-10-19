# Grok + Python — passo a passo

> Python 3.10+ recomendado; exemplos de backend que não expõem segredo. Fonte: [Quickstart](https://docs.x.ai/developers/quickstart).

## Instalação

```bash
python -m venv .venv
# Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade openai xai-sdk
```

Configurar `XAI_API_KEY` no ambiente. O SDK OpenAI-compatível é útil para a camada multi-provedor. A biblioteca `xai-sdk` nativa fornece interface própria; os exemplos seguintes usam SDK OpenAI.

## Exemplo A: consultar lista da conta + gerar resposta

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["XAI_API_KEY"],
    base_url="https://api.x.ai/v1",
    timeout=90.0,
    max_retries=2,
)
print([m.id for m in client.models.list().data])

r = client.responses.create(
    model="grok-4.20-0309-non-reasoning",
    input="Explique em pt-BR o conceito de orquestrador de agentes.",
    max_output_tokens=280,
    store=False,
)
print(r.output_text)
print(r.usage)
```

Caso seu token não tenha acesso ao modelo, substitua por um `id` retornado pela listagem, com orçamento e testes.

## Exemplo B: Grok 4.7 com Web Search

```python
r = client.responses.create(
    model="grok-4.7",
    input="Encontre a URL da documentação oficial xAI e cite a fonte.",
    tools=[{"type":"web_search"}],
    max_output_tokens=450,
    store=False,
)
print(r.output_text)
```

Web Search é cobrada separadamente; além de custo de tokens, observe ``usage`` no retorno.

## Exemplo C: function calling (função local simulada)

```python
import json

tools = [{
    "type": "function",
    "name": "consultar_estoque",
    "description": "Consulta estoque simulado de um SKU.",
    "parameters": {
        "type": "object",
        "properties": {"sku": {"type":"string"}},
        "required": ["sku"],
        "additionalProperties": False
    }
}]
first = client.responses.create(
    model="grok-4.20-0309-non-reasoning",
    input="Consulte o estoque do SKU ABC.",
    tools=tools,
)
outputs = []
for item in first.output:
    if item.type != "function_call":
        continue
    if item.name != "consultar_estoque":
        raise ValueError("Função não autorizada")
    args = json.loads(item.arguments)
    sku = args.get("sku")
    if not isinstance(sku, str) or len(sku) > 40:
        raise ValueError("SKU inválido")
    result = {"sku": sku, "quantidade": 12}  # simulação
    outputs.append({
        "type": "function_call_output",
        "call_id": item.call_id,
        "output": json.dumps(result)
    })
if outputs:
    final = client.responses.create(
        model="grok-4.20-0309-non-reasoning",
        previous_response_id=first.id,
        input=outputs,
        tools=tools,
    )
    print(final.output_text)
else:
    print(first.output_text)
```

Se `store=False`, **não dependa de `previous_response_id`**; envie histórico e resultados manualmente. No exemplo acima a primeira chamada usa o padrão de armazenamento para demonstrar continuação. Em produção defina retenção explicitamente e inclua limites de execução.

## Exemplo D: MCP remoto

```python
r = client.responses.create(
    model="grok-4.7",
    input="Quais ferramentas públicas este servidor disponibiliza?",
    tools=[{"type":"mcp",
            "server_url":"https://mcp.deepwiki.com/mcp",
            "server_label":"deepwiki"}],
    store=False,
)
print(r.output_text)
```

Este servidor é apenas demonstração de endereço público; disponibilidade e políticas podem mudar. **Nunca envie credenciais de outros serviços dentro do prompt.**

## Opcional: SDK nativo

```python
import os
from xai_sdk import Client
from xai_sdk.chat import user

native = Client(api_key=os.environ["XAI_API_KEY"])
chat = native.chat.create(model="grok-4.7")
chat.append(user("Responda em pt-BR: o que é um supervisor agent?"))
print(chat.sample().content)
```

Mais detalhes: [Responses REST](03-referencia-api.md), [MCP](04-ferramentas-mcp.md), [Caching](07-operacao-seguranca.md).

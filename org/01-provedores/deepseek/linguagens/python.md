> **Navegação:** [← Mapa mestre](../../../README.md) · [↑ DeepSeek](../README.md) · [Arquiteturas](../../../02-arquiteturas/README.md) · [Grok](../../grok/README.md)

# DeepSeek API com Python

> Requer Python 3.10+ recomendado, acesso à API oficial e a chave `DEEPSEEK_API_KEY` no ambiente. [Índice](../README.md).

## 1. Instalação

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install --upgrade openai
```

Configure `DEEPSEEK_API_KEY` conforme [primeiros passos](../02-primeiros-passos.md). O SDK `openai` é cliente compatível, **não** um serviço de inferência da OpenAI quando `base_url` aponta para DeepSeek.

## 2. Chat e modelos disponíveis

Arquivo `main.py`:
```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
    timeout=90.0,
    max_retries=2,
)

for model in client.models.list().data:
    print(model.id, getattr(model, "context_window", None))

result = client.chat.completions.create(
    model="deepseek-flash",
    messages=[
        {"role": "system", "content": "Responda sempre em pt-BR."},
        {"role": "user", "content": "O que é isolamento multi-tenant?"},
    ],
    reasoning_effort="low",
    max_tokens=300,
)
print(result.choices[0].message.content)
print("Uso:", result.usage)
```

Execute `python main.py`. Nunca imprima a chave.

## 3. Streaming da resposta

```python
stream = client.chat.completions.create(
    model="deepseek-flash",
    messages=[{"role":"user","content":"Explique o ciclo de um agente."}],
    reasoning_effort="low",
    stream=True,
)
for chunk in stream:
    if chunk.choices:
        text = chunk.choices[0].delta.content
        if text:
            print(text, end="", flush=True)
print()
```

O SDK interpreta SSE. Em implementações HTTP diretas, trate `data:`, `[DONE]` e keep-alive.

## 4. JSON estruturado

```python
import json

reply = client.chat.completions.create(
    model="deepseek-flash",
    messages=[{"role":"user","content":
       'Responda somente JSON no formato {"status": "ok", "total": 3}.'}],
    response_format={"type":"json_object"},
    max_tokens=160,
)
raw = reply.choices[0].message.content
data = json.loads(raw or "{}")
assert isinstance(data, dict) and data.get("status") == "ok"
print(data)
```

Valide esquema e trate `JSONDecodeError`, strings vazias e respostas truncadas.

## 5. Vision: analisar imagem por URL

```python
vision = client.chat.completions.create(
    model="deepseek-flash",
    messages=[{"role":"user","content":[
        {"type":"text","text":"Descreva a imagem de forma curta."},
        {"type":"image_url","image_url":{
            "url":"https://example.com/image.png", "detail":"low"}},
    ]}],
    max_tokens=200,
)
print(vision.choices[0].message.content)
```

Substitua pela URL pública de uma imagem real. Esse exemplo não funcionará com imagem fictícia e **não** deve ser usado com `deepseek-v4-pro`. Veja [Vision](https://api-docs.deepseek.com/guides/vision/).

## 6. Exemplo com Function Calling

A função abaixo é **local e simulada**. Demonstra a integração; jamais execute ferramentas não autorizadas automaticamente.

```python
import json
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com", timeout=90)
tools = [{"type":"function","function":{
    "name":"consultar_estoque",
    "description":"Consulta estoque do SKU no catálogo simulado.",
    "parameters":{"type":"object","properties":{"sku":{"type":"string"}},
                  "required":["sku"],"additionalProperties":False}
}}]
messages = [
    {"role":"system","content":"Use ferramentas apenas para consultas."},
    {"role":"user","content":"Quantas unidades do SKU ABC há no estoque?"}
]
response = client.chat.completions.create(
    model="deepseek-flash", messages=messages, tools=tools,
    tool_choice="auto", extra_body={"thinking":{"type":"disabled"}},
    max_tokens=400,
)
msg = response.choices[0].message
messages.append(msg.model_dump(exclude_none=True))
for call in msg.tool_calls or []:
    if call.function.name != "consultar_estoque":
        raise ValueError("Ferramenta não autorizada")
    args = json.loads(call.function.arguments)
    sku = args.get("sku")
    if not isinstance(sku, str) or len(sku) > 40:
        raise ValueError("SKU inválido")
    # Em produção: consultar serviço autorizado no tenant corrente.
    result = {"sku":sku,"quantidade":5}
    messages.append({
        "role":"tool", "tool_call_id":call.id,
        "content":json.dumps(result,ensure_ascii=False),
    })
if msg.tool_calls:
    final = client.chat.completions.create(
        model="deepseek-flash",messages=messages,max_tokens=300)
    print(final.choices[0].message.content)
else:
    print(msg.content)
```

Para produção, adicione validação JSON Schema, timeout por ferramenta, limite de etapas, semáforo de concorrência e autorizações por tenant.

## 7. Pesquisa web como API independente

```bash
python -m pip install requests
```
```python
import os, requests
r = requests.post(
    "https://api.deepseek.com/v1/tools/search",
    headers={"Authorization":"Bearer "+os.environ["DEEPSEEK_API_KEY"]},
    json={"query":"site:docs.python.org asyncio","count":3},
    timeout=30,
)
r.raise_for_status()
for item in r.json().get("results", []):
    print(item["title"], item["url"])
```

Cobrança por chamada de busca: [modelo de custos](../01-modelos-e-custos.md). Fonte: [DeepSeek Quick Start](https://api-docs.deepseek.com/quick_start/faq), [Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/).


---

**Continue:** [Mapa mestre](../../../README.md) · [DeepSeek](../README.md) · [Grok/xAI](../../grok/README.md) · [Arquitetura multiagente](../../../02-arquiteturas/README.md).

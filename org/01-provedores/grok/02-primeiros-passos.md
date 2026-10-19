> **Navegação:** [← Mapa mestre](../../README.md) · [↑ Grok/xAI](README.md) · [Arquiteturas](../../02-arquiteturas/README.md) · [Outro provedor](../deepseek/README.md)

# Primeiros passos na API Grok / xAI

## 1. Cadastro e cobrança

1. Acesse [console.x.ai](https://console.x.ai/), crie/accesse a sua conta e equipe.
2. Configure faturamento/créditos e leia os termos de uso aplicáveis.
3. Crie uma API key própria na área de chaves; não compartilhe credenciais.
4. Configure limite de orçamento no seu backend e, quando disponível, no console.
5. Lembre-se: **assinatura de Grok/X não fornece automaticamente créditos da API**.

## 2. Variável de ambiente

Linux/macOS:

```bash
export XAI_API_KEY="COLE_SUA_CHAVE_AQUI"
```

PowerShell:

```powershell
$env:XAI_API_KEY = "COLE_SUA_CHAVE_AQUI"
```

Nunca faça commit da chave. Acrescente `.env`, `.env.*` ao `.gitignore` exceto exemplo sem credenciais `.env.example`.

## 3. Consultar os modelos da conta

```bash
curl --fail-with-body -sS https://api.x.ai/v1/models \
  -H "Authorization: Bearer $XAI_API_KEY"
```

Consulte um ID específico com `GET /v1/models/{model_id}`. A API retorna IDs e dados de preços, mas não se deve presumir que o console tem todos os modelos citados nos docs. Verifique elegibilidade.

## 4. Primeira resposta (Responses API)

```bash
curl --fail-with-body -sS https://api.x.ai/v1/responses \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-4.20-0309-non-reasoning",
    "input": "Responda em pt-BR: o que é um agente de IA?",
    "max_output_tokens": 250,
    "store": false
  }'
```

Se a conta não tiver o 4.20, substitua pelo ID listado por `GET /v1/models` (por exemplo `grok-4.7`). O exemplo usa `store: false` para evitar persistência opcional; cheque as funções que precisam de estado retido pelo servidor.

## 5. Como ler a resposta

A resposta da Responses API inclui `id`, `status`, `output`, `usage` e, quando aplicável, custos. O texto pode aparecer em itens `message` com `content[].type="output_text"`. Prefira `response.output_text` em SDKs compatíveis; o array pode conter raciocínio criptografado e chamadas de ferramentas.

## 6. Habilitar web search (opcional e cobrado)

```json
{
  "model": "grok-4.7",
  "input": "Encontre a documentação oficial do protocolo MCP.",
  "tools": [{"type":"web_search"}]
}
```

O modelo sem ferramenta de busca **não possui atualização automática sobre fatos atuais**. Avalie custo adicional e as fontes retornadas.

## 7. Tutoriais

[Python](05-python.md) · [JS/TS](06-javascript-typescript.md) · [referência REST](03-referencia-api.md) · [diagnóstico](07-operacao-seguranca.md).

**Fontes:** [Quickstart](https://docs.x.ai/developers/quickstart) e [Models REST](https://docs.x.ai/developers/rest-api-reference/inference/models).


---

**Continuar:** [Mapa mestre](../../README.md) · [Grok/xAI](README.md) · [Comparação de provedores](../../00-fundamentos/03-por-que-deepseek-e-grok.md) · [Arquiteturas](../../02-arquiteturas/README.md).

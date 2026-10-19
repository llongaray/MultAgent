> **Navegação:** [← Mapa mestre](../../README.md) · [↑ Grok/xAI](README.md) · [Arquiteturas](../../02-arquiteturas/README.md) · [Outro provedor](../deepseek/README.md)

# Grok + JavaScript / TypeScript — Node.js

> Não use `XAI_API_KEY` em frontend, `NEXT_PUBLIC_*` nem em código distribuído ao usuário. [Documentação](https://docs.x.ai/developers/quickstart).

## 1. Preparação

```bash
mkdir grok-node && cd grok-node
npm init -y
npm pkg set type=module
npm install openai
# Configure XAI_API_KEY no ambiente do servidor.
```

## 2. Node.js + OpenAI Responses SDK compatível

```javascript
// main.mjs
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.XAI_API_KEY,
  baseURL: "https://api.x.ai/v1",
  timeout: 90000,
  maxRetries: 2,
});

const models = await client.models.list();
console.log("Modelos disponíveis:", models.data.map(x => x.id));

const reply = await client.responses.create({
  model: "grok-4.20-0309-non-reasoning",
  input: "Responda em português: explique um sistema multiagente.",
  max_output_tokens: 320,
  store: false,
});
console.log(reply.output_text);
console.log(reply.usage);
```

Execute `node main.mjs`. Se a conta não tiver este modelo, substitua pelo `id` retornado.

## 3. Ferramentas nativas e MCP remoto

```javascript
const result = await client.responses.create({
  model: "grok-4.7",
  input: "Quais são as capacidades deste MCP público?",
  tools: [
    { type: "mcp",
      server_label: "deepwiki",
      server_url: "https://mcp.deepwiki.com/mcp" },
  ],
  store: false,
});
console.log(result.output_text);
```

Para TypeScript, tipos do SDK OpenAI podem não incluir extensões específicas da xAI. Use `extra_body` no Python ou um wrapper tipado/local validado no TypeScript em vez de ignorar verificações globais.

## 4. Vercel AI SDK (opcional)

```bash
npm install ai @ai-sdk/xai zod
```

```javascript
import { xai } from "@ai-sdk/xai";
import { generateText } from "ai";

const { text } = await generateText({
  model: xai.responses("grok-4.7"),
  prompt: "Identifique riscos de uma arquitetura multi-tenant.",
});
console.log(text);
```

## 5. TypeScript + roteamento de tarefas

```typescript
type Perfil = "rapido" | "raciocinio" | "codigo" | "premium";
const grokModels: Record<Perfil,string> = {
  rapido: "grok-4.20-0309-non-reasoning",
  raciocinio: "grok-4.20-0309-reasoning",
  codigo: "grok-build-0.1",
  premium: "grok-4.7",
};

function escolherModelo(perfil: Perfil): string {
  return grokModels[perfil];
}
```

Os perfis são **política de produto**, não decisão declarada oficialmente pelo fabricante. Consulte `/models` no startup, aplique fallback só quando a aplicação o permitir, e registre model/version usado para auditoria.

## 6. Regras de produção

Backend: validar identidade/tenant, quota por usuário, prompts e autorização de ferramentas; aplicar timeouts/retries e persistir uso e custo. SSE e raciocínio criptografado exigem parser/continuidade apropriados; consulte [REST](03-referencia-api.md).

**Fontes:** [Quickstart](https://docs.x.ai/developers/quickstart), [Responses](https://docs.x.ai/developers/rest-api-reference/inference/responses), [Models](https://docs.x.ai/developers/models).


---

**Continuar:** [Mapa mestre](../../README.md) · [Grok/xAI](README.md) · [Comparação DeepSeek/Grok](../../00-fundamentos/03-por-que-deepseek-e-grok.md) · [Arquiteturas](../../02-arquiteturas/README.md).

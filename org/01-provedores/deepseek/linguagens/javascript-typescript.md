> **Navegação:** [← Mapa mestre](../../../README.md) · [↑ DeepSeek](../README.md) · [Arquiteturas](../../../02-arquiteturas/README.md) · [Grok](../../grok/README.md)

# DeepSeek API com JavaScript e TypeScript (Node.js)

> Node.js 20+ recomendado. A chave deve existir no **backend**, nunca em React/Vite, Next.js Client Component ou navegador. [Índice](../README.md).

## 1. Inicialização

```bash
mkdir deepseek-node && cd deepseek-node
npm init -y
npm pkg set type=module
npm install openai
# Exporte DEEPSEEK_API_KEY fora do código.
```

## 2. Exemplo JavaScript (SDK OpenAI compatível)

Salve em `main.mjs`:
```javascript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.DEEPSEEK_API_KEY,
  baseURL: "https://api.deepseek.com",
  timeout: 90000,
  maxRetries: 2,
});

// Descobre modelos sem manter catálogo estático:
const models = await client.models.list();
console.log("Modelos:", models.data.map(m => m.id));

const response = await client.chat.completions.create({
  model: "deepseek-flash",
  messages: [
    { role: "system", content: "Responda em português." },
    { role: "user", content: "Explique filas assíncronas em duas frases." },
  ],
  reasoning_effort: "low",
  max_tokens: 300,
});

console.log(response.choices[0]?.message?.content ?? "(sem texto)");
console.log(response.usage);
```

Execute `node main.mjs`.

## 3. Streaming

```javascript
const stream = await client.chat.completions.create({
  model: "deepseek-flash",
  messages: [{role:"user",content:"Explique SSE brevemente."}],
  reasoning_effort:"low",
  stream:true,
});
for await (const part of stream) {
  process.stdout.write(part.choices[0]?.delta?.content ?? "");
}
process.stdout.write("\n");
```

## 4. JSON com validação

```javascript
const result = await client.chat.completions.create({
  model:"deepseek-flash",
  messages:[{role:"user",content:
    'Retorne somente JSON como {"sucesso":true,"quantidade":3}.'}],
  response_format:{type:"json_object"},
  max_tokens:150,
});
const raw = result.choices[0]?.message?.content;
if (!raw) throw new Error("Resposta vazia");
const data = JSON.parse(raw);
if (data.sucesso !== true || typeof data.quantidade !== "number")
  throw new Error("JSON inválido para a aplicação");
console.log(data);
```

## 5. Function Calling — exemplo do retorno de tool

```javascript
const tools = [{type:"function",function:{
  name:"get_status",
  description:"Consulta status de um pedido autorizado.",
  parameters:{type:"object",properties:{id:{type:"string"}},
              required:["id"],additionalProperties:false}
}}];
const messages = [{role:"user",content:"Qual o status do pedido 123?"}];

const first = await client.chat.completions.create({
  model:"deepseek-flash", messages, tools, tool_choice:"auto",
  thinking:{type:"disabled"}, max_tokens:350,
});
const assistant = first.choices[0].message;
messages.push(assistant);

for (const call of assistant.tool_calls ?? []) {
  if (call.function.name !== "get_status") throw new Error("Proibida");
  const args = JSON.parse(call.function.arguments);
  if (!/^[A-Za-z0-9-]{1,40}$/.test(args.id ?? ""))
    throw new Error("ID inválido");
  const output = {id:args.id,status:"em_preparacao"}; // simulação
  messages.push({role:"tool",tool_call_id:call.id,
                 content:JSON.stringify(output)});
}
if (assistant.tool_calls?.length) {
  const second = await client.chat.completions.create({
    model:"deepseek-flash",messages,max_tokens:250
  });
  console.log(second.choices[0]?.message?.content);
} else {
  console.log(assistant.content);
}
```

## 6. TypeScript

```bash
npm install -D typescript tsx @types/node
```
```typescript
import OpenAI from "openai";
const deepseek = new OpenAI({
  baseURL:"https://api.deepseek.com",
  apiKey:process.env.DEEPSEEK_API_KEY,
});
async function perguntar(pergunta: string): Promise<string> {
  const res = await deepseek.chat.completions.create({
    model:"deepseek-flash",
    messages:[{role:"user",content:pergunta}],
    max_tokens:300,
  });
  return res.choices[0]?.message.content ?? "";
}
console.log(await perguntar("O que é tipagem estática?"));
```

Salve `main.ts` e execute `npx tsx main.ts`.

## 7. Next.js ou Express

Crie uma rota **server-side** que obtém a chave de `process.env.DEEPSEEK_API_KEY`, valida usuário, taxa, tamanho do prompt e orçamento; nunca envie a chave ao frontend. Não habilite `NEXT_PUBLIC_` para segredos. Para apps multi-tenant, associe logs e autorização ao tenant autenticado.

**Fonte:** [Quick Start oficial](https://api-docs.deepseek.com/quick_start/faq), [Chat API](https://api-docs.deepseek.com/api/create-chat-completion/).


---

**Continue:** [Mapa mestre](../../../README.md) · [DeepSeek](../README.md) · [Grok/xAI](../../grok/README.md) · [Arquitetura multiagente](../../../02-arquiteturas/README.md).

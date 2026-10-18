# DeepSeek API com Bash e cURL

> Ideal para smoke tests e automação de servidores Linux. Requer `curl` e, para filtrar JSON, `jq`. [Índice](../README.md).

## 1. Dependências e segredo

Debian/Ubuntu:
```bash
sudo apt update
sudo apt install -y curl jq
export DEEPSEEK_API_KEY='SUA_CHAVE_AQUI'
```

Evite colocar chaves em scripts versionados ou argumentos visíveis de processos. Em CI, utilize segredo protegido da plataforma.

## 2. Chat completo com extração do texto

Salve `deepseek.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail
test -n "$DEEPSEEK_API_KEY" || { echo "Configure DEEPSEEK_API_KEY" >&2; exit 1; }

request='{
  "model":"deepseek-flash",
  "messages":[
    {"role":"system","content":"Responda em português."},
    {"role":"user","content":"Explique infraestrutura como código em uma frase."}
  ],
  "max_tokens":200,
  "stream":false
}'

curl --fail-with-body --silent --show-error \
  --max-time 90 \
  https://api.deepseek.com/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  --data "$request" | jq -er '.choices[0].message.content'
```

Execute `chmod +x deepseek.sh && ./deepseek.sh`.

## 3. Listar modelos

```bash
curl --fail-with-body -sS https://api.deepseek.com/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" | jq -r '.data[].id'
```

## 4. Saldo

```bash
curl --fail-with-body -sS https://api.deepseek.com/user/balance \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" | jq .
```

## 5. Streaming (ver SSE bruto)

```bash
curl -N -sS https://api.deepseek.com/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-flash","messages":[{"role":"user","content":"Olá"}],"stream":true}'
```

SSE devolve `data: {...}`, comentários keep-alive e `data: [DONE]`. Para tratar tools ou gerar UI, implemente um parser SSE real; não basta `grep` em produção.

## 6. Search & Fetch

```bash
curl --fail-with-body -sS https://api.deepseek.com/v1/tools/search \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  --data '{"query":"DeepSeek API documentation","count":3}' | jq '.results'
```

Buscas são **cobradas separadamente**. Consulte [Search & Fetch](https://api-docs.deepseek.com/guides/search/).

**Fonte:** [Quick Start](https://api-docs.deepseek.com/quick_start/faq).

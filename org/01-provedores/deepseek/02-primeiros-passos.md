> **Navegação:** [← Mapa mestre](../../README.md) · [↑ DeepSeek](README.md) · [Arquiteturas](../../02-arquiteturas/README.md) · [Grok](../grok/README.md)

# Primeiros passos — conta, credencial e primeira requisição

## 1. Acesso legal à API oficial

1. Acesse [DeepSeek Platform](https://platform.deepseek.com/) e faça login/registro.
2. Consulte os [termos da API](https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html), política de privacidade e regras locais aplicáveis.
3. Configure saldo/faturamento conforme solicitado pelo portal; as chamadas podem consumir créditos.
4. No portal, crie uma **API key** e guarde-a em um cofre de segredos. A chave pode ter permissões e regras conforme a conta.
5. **Não confunda** login no chat web da DeepSeek com saldo e acesso autenticado da API.

## 2. Variável de ambiente

Linux/macOS (sessão atual):
```bash
export DEEPSEEK_API_KEY='SUA_CHAVE_AQUI'
```

PowerShell (sessão atual):
```powershell
$env:DEEPSEEK_API_KEY = 'SUA_CHAVE_AQUI'
```

Em produção, injete a chave pelo ambiente da aplicação, Secret Manager ou Docker secrets. Não a grave no código, histórico de shell, console de navegador ou GitHub. Adicione `.env` ao `.gitignore`.

## 3. Verificar catálogo de modelos

```bash
curl -sS https://api.deepseek.com/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

Se o retorno não contiver `deepseek-flash`, consulte as permissões e disponibilidade da conta. Nunca invente IDs.

## 4. Enviar sua primeira mensagem — cURL (Linux/macOS)

```bash
curl --fail-with-body -sS https://api.deepseek.com/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-flash",
    "messages": [
      {"role":"system","content":"Responda em português do Brasil."},
      {"role":"user","content":"Explique o que é uma API REST em uma frase."}
    ],
    "reasoning_effort": "low",
    "max_tokens": 160,
    "stream": false
  }'
```

No Windows/PowerShell, `curl` pode ter diferenças conforme versão/shell. Considere `Invoke-RestMethod` ou o exemplo [Python](linguagens/python.md).

**Resposta típica**: JSON com `id`, `model`, `choices[0].message.content` e `usage`. Não dependa de conteúdo textual idêntico a exemplos, pois a geração é probabilística.

## 5. Programação

Escolha uma linguagem no [índice de integrações](README.md#exemplos-por-linguagem). Para prototipagem, recomendamos [Python](linguagens/python.md) ou [Node.js](linguagens/javascript-typescript.md).

## 6. Erros comuns

| Status | Significado / ação |
|---|---|
| 400 | Corrigir modelo, parâmetros, tamanho, JSON ou formato da mensagem. |
| 401 | Chave ausente, revogada ou inválida: conferir credencial. |
| 402 | Saldo insuficiente: verificar billing. |
| 422 | Parâmetros incompatíveis: rever schema quando ocorrer. |
| 429 | Limite ou saturação: reduzir taxa e aplicar backoff com jitter. |
| 5xx/504 | Falha transitória: retry limitado; observar idempotência e custo. |

Não repita solicitações que resultam em erro 4xx (exceto 429) sem corrigir o problema. A [referência oficial de erros](https://api-docs.deepseek.com/quick_start/error_codes/) prevalece.

## 7. Validação antes de ir para produção

Teste autenticação, modelo, timeouts de rede, resposta vazia, `finish_reason`, cobrança, concorrência e revogação de chaves. Restrinja as chamadas ao **servidor**, não diretamente a páginas JS que exponham o segredo.

Próximo: [Referência REST](03-referencia-rest.md). Fonte: [Your First API Call](https://api-docs.deepseek.com/quick_start/faq).

---

**Continuar explorando:** [Mapa mestre](../../README.md) · [DeepSeek](README.md) · [Grok/xAI](../grok/README.md) · [Arquitetura multiagente](../../02-arquiteturas/README.md).

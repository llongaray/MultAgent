# Produção, diagnóstico, qualidade e custo

> Este guia consolida boas práticas de engenharia e os limites oficiais. [Índice](README.md).

## Arquitetura de produção

```text
Aplicativo cliente (sem chave)
       |
API backend com autenticação / quota por tenant
       |
orquestrador + logs + controle de orçamento
       |
fila assíncrona + limites de simultaneidade
       |
DeepSeek API oficial (Flash ou Pro)
       |
validação/guardrails + persistência mínima
```

## Falhas comuns e solução

| Sintoma | Diagnóstico recomendado |
|---|---|
| 401 | Credencial inválida/ausente; renovar e testar `GET /models`. |
| 402 | Saldo insuficiente; consultar `GET /user/balance`. |
| 400 | Modelo inexistente, contexto/saída excedidos, parâmetro não suportado, payload multimodal errado ou `tool_choice` incompatível com thinking. |
| 429 | Concorrência da conta, QPS de Search/Fetch ou limite por domínio de Fetch. |
| 403 | Acesso rejeitado/política de segurança; revise operação e permissões. |
| 404 Fetch | Conteúdo web não recuperável, URL indisponível ou bloqueada. |
| 5xx/504 | Falha temporária de fornecedor/downstream; retry limitado. |
| Resposta sem texto | Possível `tool_calls`, `content_filter`, resposta vazia ou erro; trate `finish_reason`. |
| JSON inválido | Forçar `json_object`, pedir JSON no prompt, aumentar `max_tokens` e validar. |
| Streaming travado | Tratar comentários SSE `: keep-alive` e chunks parciais; timeouts adequados. |

## Retry seguro

Use retries apenas para falhas transitórias (408, 429, 500, 502, 503, 504), com no máximo 2–3 tentativas, backoff exponencial e jitter, respeitando `Retry-After` quando retornado. Para operações de ferramenta, **não** reexecute efeitos colaterais sem idempotência. Em caso de incerteza sobre a primeira execução, primeiro consulte o estado.

## Controle de custos

1. Limite `max_tokens` por tipo de tarefa.
2. Faça roteamento Flash/Pro por complexidade.
3. Leia `usage` por request e persista custo estimado por tenant.
4. Leve em conta hit/miss de cache e horário de pico no preço.
5. Imponha teto mensal, diário e por execução, com circuit breaker.
6. Search/Fetch é cobrado por chamada com resultado; defina limites próprios.

## Segurança

- Credenciais exclusivamente no backend/Secret Manager; usar HTTPS.
- Nunca colocar chave em frontend, repositório, analytics ou logs.
- Sanitizar/validar resultados de ferramenta, JSON e imagens de terceiros.
- Não enviar dados pessoais/sensíveis sem base legal e política adequada.
- Adotar allowlist de ferramentas, TTL de sessão, ACL por tenant e aprovação humana para efeitos financeiros/destrutivos.
- Não expor ferramentas locais/MCP diretamente na internet sem autenticação e segmentação.

## Testes necessários

- Smoke: `GET /models`; chat Flash; chat Pro se permitido.
- Contratos: IDs, `finish_reason`, `tool_calls`, `usage` e campos nulos.
- Erros: simular 400/401/402/429/5xx sem vazar credenciais.
- Streaming: chunks fragmentados, keepalive e fechamento.
- Concorrência: load test com limites controlados, **não** indiscriminado contra serviço pago.
- E2E multiagentes: ferramentas autorizadas, dados pertencentes ao tenant, limite de 3–8 iterações e budget.
- Regressão: quando sair novo modelo, comparar qualidade e custo em dataset de prompts.

## Plano de atualização

Verifique semanalmente [changelog](https://api-docs.deepseek.com/updates/), [preços](https://api-docs.deepseek.com/quick_start/pricing/) e `GET /models`. Não trate nomes, preços e limites de 18/10/2026 como permanentes.

**Referências:** [Rate Limit](https://api-docs.deepseek.com/quick_start/rate_limit/), [Errors](https://api-docs.deepseek.com/quick_start/error_codes/), [Search](https://api-docs.deepseek.com/guides/search/), [JSON](https://api-docs.deepseek.com/guides/json_mode/).

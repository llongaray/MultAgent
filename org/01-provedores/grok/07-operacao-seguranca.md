> **Navegação:** [← Mapa mestre](../../README.md) · [↑ Grok/xAI](README.md) · [Arquiteturas](../../02-arquiteturas/README.md) · [Outro provedor](../deepseek/README.md)

# Produção: segurança, custo, cache, retenção e erros

## 1. Guardrails mínimos

- Proteger `XAI_API_KEY` com Secret Manager/env em backend; proibir secret em repo, browser, app móvel ou logs.
- Restringir cada ferramenta e MCP por **tenant, perfil e escopo**; confirmação humana para escritas e ações irreversíveis.
- Evitar passar informação pessoal/sensível desnecessária a provedores, MCPs remotos ou pesquisas.
- Configurar timeout, retries limitados (429/5xx), fila, circuit breaker e orçamento por tarefa/tenant.
- Tratar instruções de conteúdo web, X e MCP como **dados não confiáveis** para prevenir prompt injection.

## 2. Cache e conversas

Caching é automático, mas não garantido. Para Responses API use `prompt_cache_key` estável por sessão; não altere prefixos de conversa. Acompanhe `usage.input_tokens_details.cached_tokens`.

```json
{
  "model":"grok-4.7",
  "input":"Explique cache KV brevemente.",
  "prompt_cache_key":"sessao-uuid-aleatorio"
}
```

Para Grok 4.7 multi-turno, preserve o item de **reasoning criptografado** (sem leitura) na continuação stateless ou use `previous_response_id` nas respostas armazenadas. Evite Chat Completions em novos sistemas de raciocínio.

## 3. Retenção e residência

Documentação da Responses API: respostas armazenadas ficam disponíveis por **30 dias**. Use `store:false` quando seu caso não exigir histórico gerido pelo provedor. A conta pode ter configurações específicas (inclusive Zero Data Retention); confirme a configuração contratual e de equipe antes de processar dados sensíveis. Endpoint US é restrito a determinados modelos e **não garante sozinho** residência de todas as ferramentas e arquivos; preço de tokens +10%.

## 4. Cobrança precisa

Cada resposta pode informar `usage.cost_in_usd_ticks`: USD = ticks / 10.000.000.000. Inclui os componentes de custo reportados da solicitação, inclusive ferramentas geridas segundo a documentação. Acompanhe também contadores de ferramentas e cache; não estime orçamento apenas por volume de tokens.

## 5. Erros comuns

| Evento | Reação |
|---|---|
| HTTP 401 | Chave inexistente/revogada: renovar e limitar acesso. |
| HTTP 400/422 | Conferir schema, `reasoning`, `tools` e ID do modelo. |
| HTTP 404 no modelo | Conferir `GET /models` da conta e endpoint/região. |
| HTTP 429 | Reduzir taxa, respeitar `Retry-After` e usar backoff com jitter. |
| HTTP 5xx | Retentar no máximo 2-3 vezes, com circuit breaker. |
| `output_text` vazio | Verificar `output` para function calls/erros/response incompleta. |
| Conta com custo alto | Inspecionar contextos >200k, web/X search, ferramentas, storage e caching. |

## 6. Auditoria multicloud

Registre `provider`, `model_id`, `tenant_id`, duração, tokens, cache, custo efetivo, resultado da ferramenta, erro, request_id e confirmação. Não salve dados pessoais de mensagens por padrão. Para comparar com DeepSeek (que não compartilha necessariamente campo de custo pronto), mantenha uma estimativa versionada e sinalize como estimativa.

**Fontes:** [Caching](https://docs.x.ai/developers/advanced-api-usage/prompt-caching), [Cost Tracking](https://docs.x.ai/developers/cost-tracking), [Regions](https://docs.x.ai/developers/advanced-api-usage/regions), [Responses](https://docs.x.ai/developers/rest-api-reference/inference/responses).


---

**Continuar:** [Mapa mestre](../../README.md) · [Grok/xAI](README.md) · [Comparação DeepSeek/Grok](../../00-fundamentos/03-por-que-deepseek-e-grok.md) · [Arquiteturas](../../02-arquiteturas/README.md).

> **Navegação:** [← Mapa mestre](../README.md) · [↑ Arquiteturas](README.md) · [DeepSeek](../01-provedores/deepseek/README.md) · [Grok/xAI](../01-provedores/grok/README.md)

# Política de roteamento, seleção de modelos, orçamento e fallback

## Objetivos do router

- Minimizar custo **sujeito a qualidade, SLA, capacidades e privacidade**.
- Evitar cross-provider sem consentimento.
- Ser explicável: motivo e versão da política por chamada.
- Oferecer fallback seguro somente a modelos que atendam **as mesmas restrições**.
- Executar benchmarks reais de qualidade antes de atribuir pesos ao roteador.

## Política determinística inicial

```text
select(task, mode, allowed_providers, tenant_policy, budget):
  providers = intersecao(mode.providers, allowed_providers, tenant_policy)
  candidates = catálogo_disponível_online_de_cada_provider
  candidates = filter(candidates, modalidade + ferramentas + contexto + regras_dados)
  candidates = filter(candidates, limite_de_custo_est e teto_de_latencia)
  ordenar: preferência_do_papel, qualidade_em_benchmark, custo_total_previsto
  escolher primeiro elegível
  executar e registrar decisão
```

Prefira regras determinísticas antes de pedir que um LLM roteie chamadas, pois roteador que consulta outro modelo também tem latência/custo. Para tarefas complexas, um supervisor pode sugerir categorias, mas nunca relaxar restrições de políticas.

## Custos: preços de referência em contexto curto

| Provedor/modelo | Entrada 1M | Saída 1M | Exemplo 10k entrada + 2k saída |
|---|---:|---:|---:|
| DeepSeek Flash fora do pico | $0,15 | $0,60 | **$0,00270** |
| DeepSeek Pro fora do pico | $0,66 | $1,98 | **$0,01056** |
| Grok Build 0.1 | $1,00 | $2,00 | **$0,01400** |
| Grok 4.20 | $1,25 | $2,50 | **$0,01750** |
| Grok 4.7 | $2,00 | $6,00 | **$0,03200** |

Todas as quantias são USD e **hipóteses de cálculo, não faturamento de execução real**. Não incluem caches, pico DeepSeek, long-context xAI (≥200k), tools, armazenamento, prioridades e regionais. Para Grok, preferência por `usage.cost_in_usd_ticks/1e10`. Para DeepSeek, usar tabela de preços versionada + composição de `usage`.

## Estrutura `ModelCandidate`

```json
{
  "provider":"deepseek",
  "model":"deepseek-flash",
  "supports":{"tools":true,"vision":true,"web":false,"mcp_native":false},
  "allowed_modes":["deepseek_only","hybrid"],
  "max_context_tokens":1048576,
  "capability_verified_at":"2026-10-18T00:00:00Z"
}
```

Os metadados acima são somente exemplo; o sistema deve reconciliar `/models` e docs oficiais. Evitar armazenar grandes listas permanentes sem atualização.

## Orçamento por run/tenant

Orçamento configurável: `hard_limit_usd`, `soft_limit_usd`, `max_steps`, `max_parallel_agents`, `max_tool_calls`, `max_output_tokens`, `timeout_seconds`. Antes de chamada, reservar estimativa; após resposta, liquidar com custo real/estimado e ajustar saldo. Concorrência deve fazer reservas atômicas no DB para não furar o limite.

## Fallback: matriz

| Situação | Política |
|---|---|
| `deepseek_only` e 429 | retry/backoff ou fila; **jamais Grok** |
| `grok_only` e falha xAI | fila/erro; **jamais DeepSeek** |
| `hybrid` e DeepSeek sem serviço | Grok elegível **somente** se autorizado e dentro do budget |
| `hybrid` e modelo sem vision | escolher outro candidato com vision |
| Tool call com side effects parcialmente executados | consultar status/idempotência; nunca duplicar cegamente |
| Prompt contém dados restritos a um provedor | fallback para outro **proibido** |
| Provedor indisponível mas custo alternativo excede teto | falhar ou pedir nova aprovação |

## Benchmark de qualidade

Monte um conjunto de 30–100 tarefas representativas, respostas esperadas, validadores e custo/latência. Pontue por categoria: extração, JSON, planejamento, codificação, uso seguro de ferramenta, aderência à política. Só promova o modelo mais caro quando houver evidência de qualidade suficiente.

**Fontes:** [DeepSeek preços](https://api-docs.deepseek.com/quick_start/pricing/), [xAI preços](https://docs.x.ai/developers/pricing), [custo real xAI](https://docs.x.ai/developers/cost-tracking).


---

**Leituras relacionadas:** [Mapa mestre](../README.md) · [Fundamentos](../00-fundamentos/README.md) · [Modelos DeepSeek](../01-provedores/deepseek/README.md) · [Modelos Grok](../01-provedores/grok/README.md).

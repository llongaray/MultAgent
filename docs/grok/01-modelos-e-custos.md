# Modelos Grok e custo-benefício para multiagentes

> Tabela baseada em [xAI Models](https://docs.x.ai/developers/models), [Pricing](https://docs.x.ai/developers/pricing) e nos cards específicos, consultados em **18/10/2026**. Valores em USD por **1 milhão de tokens**, para prompts com **menos de 200 mil tokens**, sem cache. Para informações efetivamente acessíveis na conta, use `GET /v1/models`.

## Modelos de texto / raciocínio relevantes

| Modelo (ID exato) | Contexto | Entrada | Entrada em cache | Saída | Papel ideal |
|---|---:|---:|---:|---:|---|
| `grok-build-0.1` | 256k | $1,00 | $0,20 | $2,00 | Agente programador/código, legado `grok-code-fast-1` como alias |
| `grok-4.20-0309-non-reasoning` | 1M | $1,25 | $0,20 | $2,50 | Regras, classificação e funções rápidas |
| `grok-4.20-0309-reasoning` | 1M | $1,25 | $0,20 | $2,50 | Planejamento, análise e revisão |
| `grok-4.20-multi-agent-0309` | 1M | $1,25 | $0,20 | $2,50 | Pesquisa profunda com agentes internos da xAI |
| `grok-4.3` | 1M | $1,25 | $0,20 | $2,50 | Alternativa de modelo de texto |
| `grok-4.6` | 500k | $2,00 | $0,50 | $6,00 | Alternativa de alto desempenho |
| `grok-4.7` | 500k | $2,00 | $0,50 | $6,00 | Modelo de ponta para código e raciocínio |

**Observações:**
- Grok 4.7 aceita **texto e imagens como entrada**, retorna texto, suporta níveis `low`/`medium`/`high`/`xhigh` em `reasoning_effort` e tem corte de conhecimento de maio/2026. Seu uso preferencial é Responses API.
- `grok-4.20-multi-agent-0309` é um **modelo/serviço com colaboração interna gerenciada pelo provedor**. Não equivale ao sistema MultAgent próprio: não substitui nossos agentes, contratos, armazenamento e ferramentas.
- A xAI também oferece geração de imagens/vídeos e APIs de voz, mas são produtos com modelos, endpoints e unidades de cobrança distintos. Consulte o painel oficial antes de integrar essas modalidades.
- A variante **Grok 4.7 Fast (Cursor/Grok Build)** **não está disponível na API xAI pública**; não use um ID inventado para chamá-la.
- `grok-4.1-fast` e outros nomes históricos podem estar indisponíveis; nunca projete produção sobre nomes legados sem confirmação em `/models`.

## Contexto longo: custo dobra

Para os modelos da tabela com tabela de contexto longo, **quando o prompt atinge 200k tokens**, o valor muda para **o dobro** das taxas de entrada, cache e saída (ex.: Grok 4.7: entrada $4,00, cache $1,00, saída $12,00). O novo patamar é aplicado aos tokens da requisição, não apenas à fração acima do limite. No sistema, compactar o histórico antes do limiar.

## Outros custos

- Web Search: **$5 / 1.000 chamadas** da ferramenta, além dos tokens.
- X Search: a partir de setembro/2026, **$5 / 1.000 publicações obtidas** e **$10 / 1.000 perfis obtidos**; não confundir com antiga tarifa por chamadas.
- Code Execution: **$5 / 1.000 chamadas**.
- Collections Search: **$2,50 / 1.000 chamadas**; armazenamento de arquivos/collections tem preço próprio.
- Remote MCP: sem tarifa fixa de invocação na tabela consultada; **tokens e serviços terceiros podem ser cobrados**.
- Endpoint regional `https://us.api.x.ai/v1`: preço de tokens **+10%**, com catálogo de modelos específico.
- Processamento prioritário pode custar o dobro, segundo a configuração. Batch pode oferecer desconto para modelos elegíveis.

## Fórmula e exemplos financeiros

```text
custo_tokens_usd =
  input_nao_cache / 1_000_000 * preço_input
+ input_cache / 1_000_000 * preço_cache
+ output / 1_000_000 * preço_output
custo_total = custo_tokens_usd + ferramentas + armazenamento + prioridades
```

Exemplo (sem cache, contexto curto, 10.000 tokens entrada + 2.000 saída):

| Modelo | Exemplo de custo por tarefa |
|---|---:|
| Grok Build 0.1 | $0,0140 |
| Grok 4.20 (reasoning ou non-reasoning) | $0,0175 |
| Grok 4.7 | $0,0320 |

**Não é benchmark de qualidade ou latência**. Maior preço não garante melhor resposta no seu dataset. Grok pode devolver `usage.cost_in_usd_ticks`, onde 1 USD = 10.000.000.000 ticks; use essa métrica como gasto efetivamente contabilizado, quando disponível.

## Seleção recomendada

- **Mais barato entre esses Grok:** Build 0.1 (especializado em engenharia).
- **Melhor equilíbrio geral Grok:** 4.20 non-reasoning para tarefas simples e 4.20 reasoning para raciocínio.
- **Escalonamento premium:** 4.7 somente em tarefas de criticidade/complexidade justificadas por testes.
- **Pesquisa sofisticada:** avaliar 4.20 Multi-Agent como serviço especializado, monitorando loops e custo total.

**Links oficiais:** [Build 0.1](https://docs.x.ai/developers/models/grok-code-fast-1), [4.20](https://docs.x.ai/developers/models/grok-4.20), [4.20 Multi-Agent](https://docs.x.ai/developers/models/grok-4.20-multi-agent-0309), [4.7](https://docs.x.ai/developers/models/grok-4.7), [Pricing](https://docs.x.ai/developers/pricing).

> **Navegação:** [← Mapa mestre](../README.md) · [↑ Arquiteturas](README.md) · [DeepSeek](../01-provedores/deepseek/README.md) · [Grok/xAI](../01-provedores/grok/README.md)

# Exemplo de configuração e perfis de agentes

> Configuração **ilustrativa, não interpretada por código existente**. Nunca guarde chaves no YAML. Use variáveis `DEEPSEEK_API_KEY` e `XAI_API_KEY` no servidor.

## YAML de modos/modelos

```yaml
multagent:
  mode: hybrid  # deepseek_only | grok_only | hybrid
  allowed_providers: [deepseek, grok]
  defaults:
    privacy: standard
    max_cost_usd_per_run: 0.25
    max_steps: 8
    max_parallel_agents: 3
    max_tool_calls: 5
    cross_provider_fallback: false
  providers:
    deepseek:
      enabled: true
      base_url: https://api.deepseek.com
      api_key_env: DEEPSEEK_API_KEY
      models:
        routine: deepseek-flash
        reasoning: deepseek-v4-pro
    grok:
      enabled: true
      base_url: https://api.x.ai/v1
      api_key_env: XAI_API_KEY
      store_responses: false
      models:
        routine: grok-4.20-0309-non-reasoning
        reasoning: grok-4.20-0309-reasoning
        coding: grok-build-0.1
        premium: grok-4.7
        deep_research: grok-4.20-multi-agent-0309
  tools:
    mcp_local_enabled: false
    grok_remote_mcp_enabled: false
    web_search_enabled: false
    require_approval_for_writes: true
```

Para mudar de modo, altere `mode` e, se aplicável, `allowed_providers`. O backend deve validar que todos os provedores selecionados pertencem ao modo; se divergirem, falhar no startup em vez de ignorar.

## Perfis de agentes

```yaml
agents:
  supervisor:
    objective: "Dividir e coordenar tarefas conforme orçamento."
    preferred_capability: reasoning
    tools: []
  researcher:
    objective: "Encontrar e organizar evidências verificáveis."
    preferred_capability: routine
    tools: [search]
  coder:
    objective: "Gerar e refatorar código com testes."
    preferred_capability: coding
    tools: [read_repository]
  reviewer:
    objective: "Avaliar correção, segurança e testes."
    preferred_capability: reasoning
    tools: [read_repository, run_tests]
  summarizer:
    objective: "Consolidar resultados em pt-BR."
    preferred_capability: routine
    tools: []
```

Perfis têm permissões explícitas. Por padrão, `read_repository` e `run_tests` são permissões controladas pelo Tool Gateway e **não** dão acesso irrestrito a shell, internet ou arquivos.

## Exemplos de escolha

| Modo | Papel | Modelo típico |
|---|---|---|
| `deepseek_only` | supervisor/worker | DeepSeek Flash (escala para Pro) |
| `grok_only` | planner/reviewer | Grok 4.20 Reasoning |
| `grok_only` | coder | Grok Build 0.1 |
| `hybrid` | classificação em massa | DeepSeek Flash |
| `hybrid` | revisão crítica de código | Grok 4.20 Reasoning |
| `hybrid` | busca X com consentimento | Grok com x_search |

## Condições para ativar MCP remoto

1. Whitelist de domínios/URLs e autenticação.
2. Dados enviados são permitidos para aquele servidor.
3. Auditar ferramentas publicadas pelo MCP e restringir escrita.
4. Prever timeout, custo, isolamento, logs e revogação.
5. Testar aprovação humana independentemente da opção `require_approval`, que não é suportada na integração remota xAI.

Leia [contratos](06-contratos-e-adapters.md) e [política](05-roteamento-e-custos.md) antes de implementar estas configurações.


---

**Leituras relacionadas:** [Mapa mestre](../README.md) · [Fundamentos](../00-fundamentos/README.md) · [Modelos DeepSeek](../01-provedores/deepseek/README.md) · [Modelos Grok](../01-provedores/grok/README.md).

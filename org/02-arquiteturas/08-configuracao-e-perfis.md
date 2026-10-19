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

**Na distribuição Desktop, essa configuração será feita pela janela PySide6/Qt; na edição Server, pelo painel React autenticado**. Os dados e perfis são persistidos pelo mesmo serviço de domínio no SQLite inicial (e PostgreSQL opcional para Server); o YAML aqui é somente modelo para desenvolvimento, provisionamento ou diagnóstico. O usuário terá abas **Integrações** (cadastrar/excluir/testar chaves DeepSeek e/ou Grok), **Configurações** (escolher `deepseek_only`, `grok_only` ou `hybrid`) e **Funcionários** (criar agentes, escolher provedor/modelo, ferramentas e permissões). A chave fica em vault do sistema; SQLite armazena apenas um identificador seguro da credencial. Alterações de modo devem suspender agentes com provedor desabilitado, sem trocá-los automaticamente; fallback exige aprovação/política explícita. O backend valida que os provedores atribuídos aos agentes estão habilitados no modo global.

**Aplicação:** `multagent` abre GUI Desktop sem navegador/porta HTTP. `multagent-server init` define porta/bind e `multagent-server start` publica o painel do Server com autenticação. Consulte [editions](../04-distribuicao/04-edicoes-desktop-server.md) e [instalação](../04-distribuicao/01-instalacao-cli.md).

## Recursos e políticas por funcionário

Além do modelo de IA, cada funcionário terá **papel**, `supervisor_id`, `team_id`, `workspace_ids`, `allowed_tools` e `PermissionGrant` persistidos e validados pelo backend. O usuário poderá selecionar repositório Git local/remoto, host SSH, app instalado ou integração MCP por agente, com modo de autonomia e políticas de aprovação independentes do modelo. Um agente subordinado jamais herda permissão ilimitada do supervisor. Veja [hierarquia](10-hierarquia-processos-e-politicas.md), [acesso à máquina](11-acesso-maquina-e-isolamento.md) e [integrações](../05-integracoes/README.md).

### Exemplo de grants por agente (apenas contrato ilustrativo)

```yaml
employee:
  name: "Dev Backend"
  role: coder
  supervisor_id: team-lead-01
  provider: grok
  model: grok-build-0.1
  autonomy: execute_scoped
  grants:
    - resource: repo-local-001
      permissions: [repo.read, repo.patch]
      branch_pattern: feature/*
    - resource: tools-tests-001
      permissions: [process.run]
      commands: [pytest]
  requires_approval: [repo.commit, repo.push, os.privileged.request]
```

Não incluir chaves, tokens ou senha de administrador neste contrato.

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

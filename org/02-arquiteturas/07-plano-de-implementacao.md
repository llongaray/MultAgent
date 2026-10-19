> **Navegação:** [← Mapa mestre](../README.md) · [↑ Arquiteturas](README.md) · [DeepSeek](../01-provedores/deepseek/README.md) · [Grok/xAI](../01-provedores/grok/README.md)

# Roadmap de implementação do MultAgent

> **Não executado nesta etapa**: somente planejamento documental. Cada fase exige testes e aprovação antes de funcionalidades destrutivas, armazenamento de dados pessoais ou uso pago.

## Fase 0 — Documentação e governança

- [x] Documentação DeepSeek independente.
- [x] Documentação Grok independente.
- [x] Projeto lógico dos modos `deepseek_only`, `grok_only` e `hybrid`.
- [ ] Aprovar stack, requisitos, categorias de dados e responsabilidades do produto.
- [ ] Confirmar chaves e acesso real aos modelos (sem salvar chaves neste repo).

**Aceite:** docs navegáveis, links funcionando e matriz de modos compreensível.

## Fase 1 — Núcleo executável (sem tools externas)

- [ ] FastAPI com `POST /runs` e `GET /runs/{id}`.
- [ ] Schemas Pydantic, estados de run e banco local SQLite ou PostgreSQL.
- [ ] DeepSeekAdapter e GrokAdapter para texto (interface `ModelProvider`).
- [ ] Configuração de modelo e modo via ambiente/YAML validado.
- [ ] Router determinístico, timeout, retry e quotas simples.
- [ ] Testes unitários com providers mockados.

**Aceite:** um prompt simples opera em DeepSeek Only, Grok Only ou Hybrid, sem violar a lista de provedores.

## Fase 2 — Orquestração multiagente

- [ ] Scheduler de subtarefas com DAG/dependências e máximo de profundidade.
- [ ] Planner, Executor, Reviewer e Summarizer com contratos estáveis.
- [ ] Paralelismo seguro, cancelamento e orçamentos atômicos.
- [ ] Traces por run/task e métricas de uso custo real/estimado.
- [ ] Benchmark mínimo de qualidade por perfil.

**Aceite:** no mínimo três agentes colaboram em tarefa de teste, com resposta consolidada auditável.

## Fase 3 — Ferramentas e MCP

- [ ] Tool Gateway com allowlist/schema/tenant/approval.
- [ ] Cliente MCP local e testes contra MCP fictício.
- [ ] Grok MCP remoto opt-in; validar URLs, credenciais, políticas e riscos.
- [ ] DeepSeek Function Calling com loop de execução controlado.
- [ ] Web Search opcional, logs de uso e limite de chamadas.
- [ ] Testes contra prompt injection e duplicidade de efeitos colaterais.

**Aceite:** chamadas autorizadas são executadas uma única vez; proibidas bloqueadas e registradas.

## Fase 4 — Segurança e produção

- [ ] Postgres, fila Redis se necessário, Docker Compose, health endpoints.
- [ ] OTel/logs estruturados, alertas, dashboards de tokens/custos/erros.
- [ ] Secret Manager, SAST/dependências, auditoria de dados e backups.
- [ ] Multi-tenant: autorização, isolamento e política de retenção.
- [ ] Testes de stress, retry 429/5xx, graceful degradation, kill switch.
- [ ] Processo de release/revisão de modelos, preços e termos.

**Aceite:** falhas de um provider não violam privacidade, limites de orçamento nem a política de modo.

## Critérios de qualidade

| Métrica | Alvo inicial sugerido |
|---|---|
| Cobertura de unitários do router/adapters | ≥80% |
| Cross-provider acidental | 0 |
| Execuções não autorizadas de tools | 0 |
| Runs que excedem budget sem aprovação | 0 |
| Cobrança exibida sem sinalizar estimativa | 0 |
| Contratos quebrados por upgrade de modelo | 0 detectado em testes de regressão |
| Testes E2E | 3 cenários completos de modo + edge cases |

Os alvos são **propostas**, e o throughput/latência real dependem de chave, rede e carga.

## Próximas decisões pendentes

Antes de iniciar código: confirmar público-alvo/serviço, quais agentes serão oferecidos, limites de custo por tenant, política de dados e se a operação será apenas local ou também VPS. Sem isso, o MVP pode implementar recursos desnecessários.


---

**Leituras relacionadas:** [Mapa mestre](../README.md) · [Fundamentos](../00-fundamentos/README.md) · [Modelos DeepSeek](../01-provedores/deepseek/README.md) · [Modelos Grok](../01-provedores/grok/README.md).

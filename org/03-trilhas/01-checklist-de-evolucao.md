# Checklist de evolução do MultAgent

**[← Mapa Mestre](../README.md)** · **[↑ Trilhas](README.md)** · [Roadmap detalhado](../02-arquiteturas/07-plano-de-implementacao.md)

Este documento permite acompanhar o projeto e identificar quando passar de documentação para software. A marcação abaixo diferencia o que está documentado do que ainda depende de implementação.

## Documentação e organização

- [x] Fundamentos de LLM, multiagentes, MCP e RAG.
- [x] Documentação DeepSeek segregada.
- [x] Documentação Grok/xAI segregada.
- [x] Desenhos Only DeepSeek, Only Grok e Hybrid.
- [x] Mapa mestre com acesso por tópico, links cruzados e navegação.
- [ ] Verificação de todas as APIs/modelos com chaves de teste e créditos controlados.

## MVP funcional

- [ ] API FastAPI para criar/consultar runs.
- [ ] Provider Adapter DeepSeek e Grok.
- [ ] Catálogo dinâmico de modelos e router determinístico.
- [ ] Papéis supervisor, executor e reviewer.
- [ ] Persistência de estado e orçamento por run.
- [ ] Testes reais e simulados dos três modos.

## Integração de ferramentas

- [ ] Tool Gateway com schema, autenticação e idempotência.
- [ ] MCP local controlado por backend.
- [ ] MCP remoto xAI com políticas de escopo.
- [ ] Busca web e acesso X autorizados pelo usuário/tenant.
- [ ] Testes de ataques de prompt injection e ferramentas destrutivas.

## Operação

- [ ] Docker/infra.
- [ ] Segredos fora de GitHub e do frontend.
- [ ] Métricas de tokens e custo por provider/tenant.
- [ ] Timeout, retry, circuit breaker, quotas, backup e LGPD.
- [ ] Revisão periódica de modelos, termos e tarifas.

A marcação de documentação indica **arquivos publicados**, não validação de runtime, compilação ou operação em produção.

**[← Voltar ao Mapa Mestre](../README.md)**

# Checklist de evolução do MultAgent

**[← Mapa Mestre](../README.md)** · **[↑ Trilhas](README.md)** · [Roadmap detalhado](../02-arquiteturas/07-plano-de-implementacao.md)

Este documento permite acompanhar o projeto e identificar quando passar de documentação para software. A marcação abaixo diferencia o que está documentado do que ainda depende de implementação.

## Documentação e organização

- [x] Fundamentos de LLM, multiagentes, MCP e RAG.
- [x] Documentação DeepSeek segregada.
- [x] Documentação Grok/xAI segregada.
- [x] Desenhos Only DeepSeek, Only Grok e Hybrid.
- [x] Documentada missão de agentes hierárquicos com acesso por recurso para trabalho real.
- [x] Documentado catálogo de MCP/plugins/skills, Git/SSH e política de elevação por broker.
- [x] Mapa mestre com acesso por tópico, links cruzados e navegação.
- [x] Criadas as pastas técnicas `src/multagent/`, `frontend-server/`, `scripts/`, `tests/`, `config/`, `examples/`, `assets/` e `.github/` com README por diretório.
- [x] Publicado o [mapa físico do projeto](../06-desenvolvimento/01-mapa-de-pastas.md), sem criar código-fonte funcional.
- [x] Especificação de duas edições instaláveis por comando: Desktop GUI Qt e Server headless com FastAPI/React; política de releases.
- [ ] Escolher e publicar licença legal definitiva (AGPLv3 em avaliação).
- [ ] Verificação de todas as APIs/modelos com chaves de teste e créditos controlados.

## Instalação e distribuição CLI

- [ ] Implementar **core Python único** e duas aplicações: GUI Desktop **PySide6/Qt** (`multagent`) e serviço Server **FastAPI + React** (`multagent-server`).
- [ ] Criar script instalador Linux e instalador PowerShell com verificação de integridade.
- [ ] Compilar **artefatos Desktop e Server independentes** para Windows/Linux, publicando releases verificáveis por edição e plataforma.
- [ ] Implementar `multagent` para abrir janela sem HTTP/navegador, com `logs`, `update`, `doctor` e atalhos.
- [ ] Implementar `multagent-server init` (porta/bind configuráveis), `start`, `status`, `logs`, `update`, `doctor` e serviço opcional (systemd/Windows Service).
- [ ] Testar execução sem Python/Node/Docker previamente instalados.
- [ ] Configurar vault de tokens em ambas as edições; **Desktop sem porta**, Server com bind seguro/TLS/autenticação e escolha explícita de exposição da rede.
- [ ] Configurar CI/PRs, branch protegida e releases auditáveis.

## MVP funcional

- [ ] GUI Qt nativa para criar/consultar runs no Desktop e API FastAPI autenticada para criar/consultar runs no Server.
- [ ] Provider Adapter DeepSeek e Grok.
- [ ] Catálogo dinâmico de modelos e router determinístico.
- [ ] Papéis supervisor, executor e reviewer.
- [ ] Persistência de estado e orçamento por run.
- [ ] Testes reais e simulados dos três modos.

## Hierarquia, repositórios e plugins

- [ ] Gravar equipes, funcionários, supervisor_id, workflows e grants.
- [ ] Workspaces Git locais isolados, patches, testes e revisões.
- [ ] GitHub, GitLab, Bitbucket e SSH com autorização de escopo mínimo.
- [ ] Catálogo online de MCP, plugins e skills, versões fixas e instalação revisada.
- [ ] OAuth quando disponível no provedor, com tokens no vault e revogação.
- [ ] Automação de aplicativos locais por API/acessibilidade e privilégios exclusivos via broker.

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

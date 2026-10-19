# 05 · Caminho de desenvolvimento: propósito até autonomia no sistema operacional

> [← Mapa Mestre](../README.md) · [↑ Integrações](README.md) · [Roadmap técnico geral](../02-arquiteturas/07-plano-de-implementacao.md)

**Status: planejamento.** Quando iniciarmos código, cada módulo será entregue via [PR separado, priorizado P0 → P1 → P2...](../06-desenvolvimento/05-fluxo-de-prs-e-prioridades.md). Esta sequência separa entregar valor do usuário cedo de habilitar acesso de alto risco antes de existir isolamento/controle de permissões.

## Marco 0 — Definir e testar os contratos do produto

- [x] Documentar missão, pessoas/agentes, hierarquia, repositórios, catálogo e política de privilégios.
- [x] Reservar as pastas dos módulos e publicar README documental para cada uma, com [árvore física](../06-desenvolvimento/01-mapa-de-pastas.md).
- [ ] Formalizar schemas `Agent`, `Team`, `Workspace`, `Workflow`, `PermissionGrant`, `IntegrationInstance` e `AuditEvent`.
- [ ] Definir licença open-source final e compatibilidade de Qt, plugins e dependências.
- [ ] Criar matriz de suporte Windows 10/11 / Ubuntu / Debian / edições Server.
- [ ] Especificar ameaças: prompt injection, tool injection, supply chain, exfiltração, plugins com código arbitrário.

**Aceite:** modelo de domínio e interfaces/API aprovados; nenhum acesso administrativo automático.

## Marco 1 — MultAgent Desktop/Server + agentes configuráveis (MVP)

- [ ] Core Python, config, SQLite, vault; adapters DeepSeek/Grok.
- [ ] Desktop PySide6 nativo com Integrações, Configurações, Funcionários, Processos e Execuções.
- [ ] Server FastAPI + React para operação headless com bind/porta e autenticação.
- [ ] Criação de agentes, papéis, relação supervisor-filho, provedor/modelo, orçamento e persistência.
- [ ] Run simples de dois agentes em sequência, registros e validação.
- [ ] Scripts de instalação e releases assinadas para Windows/Linux.

**Aceite:** usuário instala e executa GUI ou servidor; cria equipe e executa tarefa **sem ferramentas de acesso ao PC**.

## Marco 2 — Workspaces de código e permissões

- [ ] Resource Manager com grant por agente/diretório.
- [ ] Abrir repo local Git, criar worktree, ler arquivos, propor patch, testar em sandbox e ver diff.
- [ ] Agendamento DAG, supervisor, coder, testador/revisor e parada de workflow.
- [ ] Aprovação humana para gravação fora da worktree, commit/push/merge e publicação.
- [ ] Testes para impedir path traversal/symlink escape, corrida de escrita e leitura de segredos.

**Aceite:** equipe gera correção revisável em repositório permitido e **não** acessa outro workspace.

## Marco 3 — Git remoto e SSH

- [ ] Integração GitHub App/repo-scoped com login e permissões granulares.
- [ ] Conectores GitLab, Bitbucket/SSH com autenticação e grants.
- [ ] Pull request/merge request via política, webhooks/triggers quando seguros.
- [ ] Host SSH com host-key verification, conta remota limitada, comandos aprovados e logs.
- [ ] Testes de tokens expirados, revogação e acesso negado.

**Aceite:** operar apenas repositório/host autorizados, produzir branch/PR verificáveis sem push silencioso.

## Marco 4 — Catálogo público de MCP/skills/plugins

- [ ] Fonte de metadados MCP Registry e pesquisa dentro da GUI/painel Server.
- [ ] Manifestos, trust score **baseado em evidência**, permissões, versões fixadas.
- [ ] OAuth/PKCE conforme provedor; Device Flow quando suportado, vault e revogação.
- [ ] Conectar MCP remoto de leitura, depois MCP local em sandbox.
- [ ] Instalação/revisão de plugins/skills de repositórios Git com quarentena e isolamento.
- [ ] Testes de supply-chain, schema de ferramentas, prompt injection e exfiltração.

**Aceite:** instalar integração autorizada sem executar hooks arbitrários ou ganhar privilégios extras.

## Marco 5 — Controle autônomo de aplicativos e PC

- [ ] Adapters por OS: Windows UI Automation, Linux AT-SPI/Wayland/X11 onde possível.
- [ ] Permissões por aplicativo/janela, isolamento e monitoramento de ações.
- [ ] Integração com APIs oficiais de apps e MCPs confiáveis antes de GUI automation frágil.
- [ ] Sessões gráficas, foco, cancelamento, captura com proteção de dados e limitações headless.
- [ ] **Broker de privilégios** separado por OS para ações administrativas específicas e aprovadas, sem executar o orquestrador inteiro como root/Admin.
- [ ] Testes adversariais, pen-test do broker, confirmação de alto risco, rollback e botão de emergência.

**Aceite:** operar um app autorizado sem controlar outros apps e realizar ação privilegiada apenas após consentimento autenticado e auditado.

## Marco 6 — Ecossistema e estabilidade

- [ ] CI/CD, política de PR público, assinaturas de release/updates, canais estável/beta.
- [ ] Observabilidade de agentes, custos, latência, erros e ferramentas.
- [ ] Segurança de extensões, sandbox, gerência de versões e compatibilidade de skills.
- [ ] Documentação de desenvolvedores, SDK de plugins, exemplos e galeria comunitária.
- [ ] Suporte a ambientes multi-tenant no Server, quotas e backups.

## Por que a ordem importa?

Não é seguro implementar primeiro `sudo` permanente, shell arbitrário ou instalação automática de plugin externo sem política, consentimento, isolamento e auditoria. O objetivo é autonomia **efetiva**, com recursos reais e retorno verificável, não liberdade irrestrita ao modelo para agir fora dos interesses do usuário.

**Relacionados:** [Hierarquia](../02-arquiteturas/10-hierarquia-processos-e-politicas.md) · [Acesso ao SO](../02-arquiteturas/11-acesso-maquina-e-isolamento.md) · [Git/SSH](01-git-repositorios-ssh.md) · [Catálogo](02-catalogo-mcp-plugins-skills.md).

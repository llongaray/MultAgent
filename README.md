# MultAgent

**Missão:** permitir que qualquer usuário configure **funcionários de IA hierárquicos** para executar trabalhos reais no computador/servidor, repositórios Git, aplicativos e ferramentas externas, com acesso e autonomia definidos por pessoa/agente. Projeto multiagente open-source em planejamento, com **duas edições independentes**: Desktop com janela gráfica PySide6/Qt e Server headless com FastAPI + painel React. O motor Python compartilha **DeepSeek**, **Grok/xAI** ou **ambos**. [Ler o objetivo completo](org/00-fundamentos/05-proposito-e-casos-de-uso.md).

## Documentação

### **[Abrir o Mapa Mestre — org/README.md](org/README.md)**

Este é o **ponto de entrada da documentação**: apresenta os conceitos de IA/LLM, tokens, agentes, MCP e RAG; contém o organograma clicável da organização e orienta a leitura de todos os guias.

| Quero entender... | Acesse |
|---|---|
| Missão e casos de uso do projeto | [Propósito do MultAgent](org/00-fundamentos/05-proposito-e-casos-de-uso.md) |
| Fundamentos de IA e LLM | [00 · Fundamentos](org/00-fundamentos/README.md) |
| API da DeepSeek, custos e código | [01 · DeepSeek](org/01-provedores/deepseek/README.md) |
| API do Grok/xAI, custos e ferramentas | [01 · Grok](org/01-provedores/grok/README.md) |
| DeepSeek Only, Grok Only e Hybrid | [02 · Arquiteturas](org/02-arquiteturas/README.md) |
| Como estudar e implementar | [03 · Trilhas](org/03-trilhas/README.md) |
| Estrutura real das pastas e documentação dos módulos | [06 · Desenvolvimento](org/06-desenvolvimento/README.md) · [Mapa físico](org/06-desenvolvimento/01-mapa-de-pastas.md) |
| Desktop nativo, Server, instalação e releases | [04 · Distribuição e governança](org/04-distribuicao/README.md) |
| Diferença entre os executáveis Desktop e Server | [Edições Desktop/Server](org/04-distribuicao/04-edicoes-desktop-server.md) |
| GitHub, GitLab, Bitbucket, SSH, apps, MCPs, plugins e skills | [05 · Integrações e catálogo](org/05-integracoes/README.md) |
| Hierarquia, delegação e permissões por agente | [Arquitetura de hierarquia](org/02-arquiteturas/10-hierarquia-processos-e-politicas.md) |
| Comparativo dos provedores | [Por que DeepSeek e Grok?](org/00-fundamentos/03-por-que-deepseek-e-grok.md) |

> **Diretriz de distribuição:** Windows 10/11 e Ubuntu/Debian Desktop usam um **executável nativo PySide6** que abre uma janela **sem web, navegador ou porta HTTP** (`multagent`). Uma edição **Server separada** roda em Windows/Linux Server sem GUI e, após configurar a porta, serve a interface React pela API FastAPI (`multagent-server`). Ambos serão instalados por script do GitHub; **ainda não há binários ou scripts executáveis publicados**. [Detalhes](org/04-distribuicao/04-edicoes-desktop-server.md) · [Instalação](org/04-distribuicao/01-instalacao-cli.md) · [Governança](org/04-distribuicao/02-licenca-e-contribuicoes.md).

**Segurança:** a instalação e determinadas ferramentas podem pedir privilégios administrativos, mas a interface, os modelos e a execução normal dos agentes **não** funcionarão continuamente como root/Administrador. Um broker privilegiado separado e auditado atenderá ações elevadas especificamente autorizadas. [Modelo de acesso à máquina](org/02-arquiteturas/11-acesso-maquina-e-isolamento.md).

**A documentação central fica em `org/`.** As pastas de desenvolvimento criadas em `src/`, `frontend-server/`, `tests/`, `scripts/`, `config/`, `examples/`, `assets/` e `.github/` também possuem `README.md` próprios para orientar futuras implementações. [Consultar a árvore completa](org/06-desenvolvimento/01-mapa-de-pastas.md).

> **Status:** documentação e desenho de arquitetura; **o software multiagente ainda não foi implementado**. Revisão: 19/10/2026. Consulte documentação oficial [DeepSeek](https://api-docs.deepseek.com/) e [xAI/Grok](https://docs.x.ai/developers) para versões, preços e condições de API.

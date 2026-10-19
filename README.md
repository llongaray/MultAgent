# MultAgent

Plataforma multiagente open-source em planejamento, com **duas edições independentes**: Desktop com janela gráfica PySide6/Qt e Server headless com API FastAPI + painel web React. Ambas compartilham o motor Python e os provedores **DeepSeek**, **Grok/xAI** ou **ambos**.

## Documentação

### **[Abrir o Mapa Mestre — org/README.md](org/README.md)**

Este é o **ponto de entrada da documentação**: apresenta os conceitos de IA/LLM, tokens, agentes, MCP e RAG; contém o organograma clicável da organização e orienta a leitura de todos os guias.

| Quero entender... | Acesse |
|---|---|
| Fundamentos de IA e LLM | [00 · Fundamentos](org/00-fundamentos/README.md) |
| API da DeepSeek, custos e código | [01 · DeepSeek](org/01-provedores/deepseek/README.md) |
| API do Grok/xAI, custos e ferramentas | [01 · Grok](org/01-provedores/grok/README.md) |
| DeepSeek Only, Grok Only e Hybrid | [02 · Arquiteturas](org/02-arquiteturas/README.md) |
| Como estudar e implementar | [03 · Trilhas](org/03-trilhas/README.md) |
| Desktop nativo, Server, instalação e releases | [04 · Distribuição e governança](org/04-distribuicao/README.md) |
| Diferença entre os executáveis Desktop e Server | [Edições Desktop/Server](org/04-distribuicao/04-edicoes-desktop-server.md) |
| Comparativo dos provedores | [Por que DeepSeek e Grok?](org/00-fundamentos/03-por-que-deepseek-e-grok.md) |

> **Diretriz de distribuição:** Windows 10/11 e Ubuntu/Debian Desktop usam um **executável nativo PySide6** que abre uma janela **sem web, navegador ou porta HTTP** (`multagent`). Uma edição **Server separada** roda em Windows/Linux Server sem GUI e, após configurar a porta, serve a interface React pela API FastAPI (`multagent-server`). Ambos serão instalados por script do GitHub; **ainda não há binários ou scripts executáveis publicados**. [Detalhes](org/04-distribuicao/04-edicoes-desktop-server.md) · [Instalação](org/04-distribuicao/01-instalacao-cli.md) · [Governança](org/04-distribuicao/02-licenca-e-contribuicoes.md).

**A documentação técnica reside em `org/`**, organizada hierarquicamente, com retorno ao mapa mestre em todas as páginas.

> **Status:** documentação e desenho de arquitetura; **o software multiagente ainda não foi implementado**. Revisão: 18/10/2026. Consulte documentação oficial [DeepSeek](https://api-docs.deepseek.com/) e [xAI/Grok](https://docs.x.ai/developers) para versões, preços e condições de API.

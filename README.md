# MultAgent

Plataforma multiagente em planejamento, com suporte arquitetural para **DeepSeek**, **Grok/xAI** e um modo **híbrido** que distribui tarefas conforme custo, recursos, privacidade e qualidade.

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
| Instalação pelo terminal, execução local, open-source e releases | [04 · Distribuição e governança](org/04-distribuicao/README.md) |
| Comparativo dos provedores | [Por que DeepSeek e Grok?](org/00-fundamentos/03-por-que-deepseek-e-grok.md) |

> **Diretriz de distribuição:** aplicação gratuita para instalação local, com Python + FastAPI + React/TypeScript + SQLite, sem Tauri obrigatório. A CLI planejada será `multagent start`; **ainda não existe instalador ou comando executável publicado**. [Leia o desenho de instalação](org/04-distribuicao/01-instalacao-cli.md) e a [política de contribuição/licença](org/04-distribuicao/02-licenca-e-contribuicoes.md).

**A documentação técnica reside em `org/`**, organizada hierarquicamente, com retorno ao mapa mestre em todas as páginas.

> **Status:** documentação e desenho de arquitetura; **o software multiagente ainda não foi implementado**. Revisão: 18/10/2026. Consulte documentação oficial [DeepSeek](https://api-docs.deepseek.com/) e [xAI/Grok](https://docs.x.ai/developers) para versões, preços e condições de API.

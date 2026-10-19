> **Navegação:** [← Mapa mestre](../README.md) · [↑ Arquiteturas](README.md) · [Fundamentos](../00-fundamentos/README.md) · [Provedores](../01-provedores/deepseek/README.md)

# MultAgent — arquitetura multiagente com DeepSeek e Grok

> **Proposta técnica v0.1 · 18/10/2026.** Nesta etapa foram criados **documentos de arquitetura**, não um serviço implantado. Os detalhes são decisões de projeto sugeridas, não funcionalidades já implementadas.

## Três modos, uma base de código

| Modo | Provedores permitidos | Quando usar |
|---|---|---|
| `deepseek_only` | DeepSeek | Custo mínimo, compatibilidade MCP via backend, sem dependência xAI |
| `grok_only` | xAI/Grok | Ferramentas hospedadas, MCP remoto xAI e recursos de raciocínio |
| `hybrid` | DeepSeek + xAI | Roteamento por perfil, custo, desempenho, políticas e fallback |

## Leituras da arquitetura

1. [Topologia e componentes compartilhados](01-visao-componentes.md).
2. [Modo DeepSeek Only](02-somente-deepseek.md).
3. [Modo Grok Only](03-somente-grok.md).
4. [Modo Hybrid: Grok + DeepSeek](04-hibrido.md).
5. [Router: seleção de modelo, orçamentos, custos e fallback](05-roteamento-e-custos.md).
6. [Contratos de interfaces, formatos de mensagem, tools e MCP](06-contratos-e-adapters.md).
7. [Etapas de implementação, testes e critérios de aceite](07-plano-de-implementacao.md).
8. [Exemplos de configuração, papéis de agentes e políticas](08-configuracao-e-perfis.md).
9. [Distribuição Windows/Linux, CLI e instalação pelo terminal](../04-distribuicao/README.md).

## Documentação específica dos provedores

- [Documentação DeepSeek](../01-provedores/deepseek/README.md): Chat/Responses stateless, preços, métodos, Python/JS/Go/C/Ruby e outras linguagens, integração de ferramentas pelo backend.
- [Documentação Grok](../01-provedores/grok/README.md): Responses (inclusive estado opcional), ferramentas xAI, MCP remoto, modelos/custos e integrações Python/JS.

## Princípios que precisam ser mantidos

1. **Orquestração própria.** Os modelos não se comunicam diretamente entre si; o backend converte resultados em contratos padronizados.
2. **Configuração controlada.** `mode` delimita quais provedores podem ser utilizados; não há encaminhamento oculto.
3. **Privacidade por padrão.** Dados confidenciais não transitam para outro provedor sem permissão e base legal adequadas.
4. **Ferramentas com segurança.** O modelo sugere função; o executor aplica autorização, aprovação humana e validação.
5. **Observabilidade e custos.** Toda execução registra modo, provedores/modelos, uso, tempo e motivo de roteamento (sem divulgar prompts).
6. **Resiliência.** Timeout, retry limitado, circuit breaker e redução de escopo são previstos sem duplicar operações com efeito colateral.
7. **Modelos substituíveis.** Descoberta por catálogo de cada conta; nomes/tarifas são versionados com revisões.
8. **Sem dependência de SaaS obrigatória além da API escolhida.** PostgreSQL/Redis/MCP podem rodar em máquina local ou VPS.

## Stack e distribuição base do MVP

- **Backend/orquestrador:** Python 3.12+ e FastAPI, empacotados para Windows/Linux.
- **Interface:** React + TypeScript/Vite, compilada e servida pelo backend local no navegador.
- **Persistência:** SQLite por padrão (instalação única), com PostgreSQL como evolução opcional para servidor/multiusuário.
- **CLI:** entrypoint `multagent` com `start`, `status`, `stop` (modo background), `update`, `doctor`; **ainda não implementados**.
- **Execução:** processo foreground inicialmente; workers assíncronos controlados; execução em background/auto-start é recurso opt-in posterior.
- **MCP:** cliente local controlado pelo backend; proxy remoto autenticado apenas quando permitido.
- **Observabilidade:** logs JSON, custo por provider e métricas de falhas.
- **Distribuição:** releases públicas verificáveis por SO/arquitetura, instalação via shell/PowerShell, sem exigir Python/Node/Docker no caminho do usuário final; Docker opcional para desenvolvimento/servidor.
- **Tauri:** não faz parte do MVP; poderá ser interface alternativa no futuro.

Veja [instalação e execução](../04-distribuicao/01-instalacao-cli.md) e [governança open-source](../04-distribuicao/02-licenca-e-contribuicoes.md).

O desenho é **incremental**: primeiro prova de conceito sem ferramentas destrutivas, depois multiagentes e, por último, ferramentas externas e escala.


---

**Continuar:** [Mapa mestre](../README.md) · [Arquiteturas](README.md) · [Comparação DeepSeek/Grok](../00-fundamentos/03-por-que-deepseek-e-grok.md) · [Arquiteturas](README.md).

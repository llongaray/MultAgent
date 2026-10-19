# 03 · Por que avaliar DeepSeek e Grok no MultAgent?

**[← Mapa Mestre](../README.md)** · **[↑ Fundamentos](README.md)** · [Anterior: multiagente](02-o-que-e-multiagente.md) · [Próximo: glossário](04-glossario.md)

## Objetivo da escolha

A motivação não é criar uma disputa entre marcas, mas reduzir dependência de um único serviço e combinar **baixo custo unitário** com **ferramentas avançadas**. DeepSeek e Grok são candidatos pertinentes ao escopo atual, **não necessariamente as duas alternativas mais baratas ou melhores do mercado**. Uma avaliação definitiva exigiria considerar outros provedores e rodar benchmarks no workload do projeto.

## DeepSeek: forte candidato para volume

A API documentada possui modelos Flash/Pro, contexto amplo, geração de código, JSON estruturado e Function Calling; o Flash tem tarifa de tokens bastante competitiva em tarefas repetitivas. A aplicação deve executar e autorizar funções externas e integrar MCP pelo seu cliente/gateway. A tarifa varia conforme cache e janela de pico. Como a interface é stateless, cabe ao backend persistir o histórico.

**Aprofundar:** [DeepSeek API](../01-provedores/deepseek/README.md) · [Preços DeepSeek](../01-provedores/deepseek/01-modelos-e-custos.md).

## Grok/xAI: candidato para ferramentas geridas

A xAI oferece Responses API, modelos para programação/raciocínio e ferramentas hospedadas, como busca na web/X, execução controlada e MCP remoto em servidores aprovados. Isso reduz o trabalho de integrar determinadas ferramentas, mas cria dependências de execução externa, custos adicionais e requisitos explícitos de segurança/retensão. Contextos ≥200 mil tokens podem ter tarifas maiores.

**Aprofundar:** [Grok API](../01-provedores/grok/README.md) · [Preços Grok](../01-provedores/grok/01-modelos-e-custos.md).

## Comparação para decisão arquitetural

| Critério | DeepSeek | Grok | Decisão inicial |
|---|---|---|---|
| Classificação em massa | vantagem de preço no Flash | pode executar com 4.20 NR | medir custo por acerto |
| Revisão de arquitetura | Pro/Flash | 4.20 Reasoning/4.7 | benchmark com casos difíceis |
| Desenvolvimento de código | Flash/Pro | Grok Build/4.7 | comparar testes verdes por dólar |
| Pesquisa na internet | Search/Fetch cobradas separadamente | Web/X Search na Responses | considerar fontes e custos de tools |
| Acesso MCP privado | backend próprio | gateway próprio, evitando MCP remoto exposto | preferir gateway interno |
| MCP remoto público | gateway próprio | suporte nativo sob política | permitir apenas servidores confiáveis |
| Portabilidade | adapter dedicado | adapter dedicado | contratos canônicos no sistema |

## Três estratégias válidas

1. **Somente DeepSeek**: simplicidade operacional e orçamento inicial mínimo.
2. **Somente Grok**: ferramentas geridas e serviço xAI, sem depender de DeepSeek.
3. **Híbrido**: router escolhe por tarefa e usa revisão cruzada sob condições; não significa usar ambos em toda chamada.

**Regra de ouro:** o usuário/tenant decide quais provedores podem receber seus dados. Fallback **não** pode contornar uma restrição de privacidade. A resposta de um provedor não deve conter tokens secretos, raciocínio interno ou dados sensíveis enviados ao outro.

## Critérios de aceite antes de chamar algo de "melhor"

Comparar qualidade por tarefa, testes determinísticos, latência P50/P95, custo por execução, disponibilidade, compliance, limites de ferramentas e custo de engenharia. Atualizar catálogo via `/models` e usar as tarifas vigentes.

**Leituras relacionadas:** [Modos e implementação](../02-arquiteturas/README.md) · [Router e custos](../02-arquiteturas/05-roteamento-e-custos.md).

**[← Voltar ao Mapa Mestre](../README.md)**

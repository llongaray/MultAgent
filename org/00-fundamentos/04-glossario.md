# 04 · Glossário de IA e do projeto MultAgent

**[← Mapa Mestre](../README.md)** · **[↑ Fundamentos](README.md)**

| Termo | Significado resumido |
|---|---|
| IA | Campo de sistemas capazes de realizar tarefas cognitivas/perceptivas. |
| IA generativa | Modelos que produzem conteúdo, não apenas classificam. |
| LLM | Large Language Model: modelo de linguagem de grande porte. |
| Token | Unidade de entrada/saída de um modelo; não equivale necessariamente a palavra. |
| Context window | Limite de tokens processados por operação. |
| Prompt | Instruções e dados entregues ao modelo. |
| Inferência | Execução do modelo para gerar uma resposta. |
| Modelo de raciocínio | Variante/modo que utiliza recursos adicionais para tarefas complexas. |
| Hallucination / alucinação | Saída incorreta com aparência de fato. |
| Agent | Unidade de software com objetivo, modelo e ferramentas/regras. |
| Multiagentes | Coordenação de múltiplos agentes com papéis definidos. |
| Supervisor / Orquestrador | Coordenador de estados, ordem, ferramentas e resultados. |
| Router | Selecionador de modelo/provedor segundo políticas e capacidade. |
| Provider | Empresa/serviço que oferece modelos e APIs. |
| Adapter | Camada que traduz API específica para contrato comum. |
| Function Calling | Modelo gera pedido estruturado de execução de função. |
| Tool Gateway | Componente que autoriza, valida e executa ferramentas. |
| MCP | Model Context Protocol, protocolo de integração com ferramentas e recursos. |
| RAG | Retrieval-Augmented Generation: busca documental e contexto adicional. |
| Embedding | Representação numérica vetorial usada, por exemplo, para busca semântica. |
| Cache HIT/MISS | Reaproveitamento ou recomputação de prefixos/contextos. |
| JSON Schema | Contrato formal de dados e argumentos. |
| SSE | Server-Sent Events, resposta HTTP incremental em streaming. |
| Tenant | Cliente ou organização isolada em sistema multi-tenant. |
| ACL | Access Control List: permissões sobre ações e recursos. |
| Idempotência | Repetir uma operação não causa efeitos adicionais indevidos. |
| Budget | Teto de tokens/dinheiro/tempo/chamadas por execução. |
| Fallback | Modelo/provedor alternativo sob restrições explícitas. |
| Hallucination mitigation | Validação, fontes, RAG e testes para reduzir erros. |
| Stateless | API não mantém automaticamente estado conversacional entre requests. |
| Zero Data Retention | Regime de processamento com regras especiais de retenção conforme contrato. |

**Aprofundar:** [LLM](01-o-que-e-llm.md) · [Multiagentes](02-o-que-e-multiagente.md) · [Modelo híbrido](../02-arquiteturas/04-hibrido.md).

**[← Voltar ao Mapa Mestre](../README.md)**

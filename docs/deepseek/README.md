# DeepSeek API — documentação para desenvolvedores

> **Revisão: 18/10/2026** · Idioma: pt-BR · Documentação independente para o projeto [MultAgent](../../README.md). Conferir alterações na [documentação oficial](https://api-docs.deepseek.com/). Os exemplos não foram executados com credenciais reais.

## Como estudar (passo a passo)

1. [Modelos, capacidades, preços e descoberta](01-modelos-e-custos.md)
2. [Criar conta, API key e primeira chamada](02-primeiros-passos.md)
3. [Referência REST: endpoints, payloads e respostas](03-referencia-rest.md)
4. [Recursos avançados: thinking, visão, JSON, streaming e arquivos](04-recursos-avancados.md)
5. [Multiagentes, Tool Calling, RAG, MCP e segurança](05-multiagentes-mcp.md)
6. [Fontes oficiais, atualização e regras de uso](06-fontes-e-manutencao.md)

## Exemplos por linguagem

| Linguagem | Arquivo | Forma de integração |
|---|---|---|
| Python | [python.md](linguagens/python.md) | SDK OpenAI + requests |
| JavaScript / TypeScript | [javascript-typescript.md](linguagens/javascript-typescript.md) | SDK OpenAI para Node |
| Go | [go.md](linguagens/go.md) | net/http padrão |
| C | [c.md](linguagens/c.md) | libcurl |
| Ruby | [ruby.md](linguagens/ruby.md) | Net::HTTP padrão |
| Java | [java.md](linguagens/java.md) | HttpClient (JDK 11+) |
| C# / .NET | [csharp.md](linguagens/csharp.md) | HttpClient e System.Text.Json |
| PHP | [php.md](linguagens/php.md) | extensão cURL |
| Rust | [rust.md](linguagens/rust.md) | reqwest + serde_json |
| Bash | [bash.md](linguagens/bash.md) | cURL + jq |

## Convenções

- API oficial: `https://api.deepseek.com`; credencial no header `Authorization: Bearer ...`.
- Modelos hospedados atualmente documentados: `deepseek-flash` e `deepseek-v4-pro`.
- Todos os exemplos usam `DEEPSEEK_API_KEY` via ambiente; **nunca** publique chaves, logs sensíveis nem arquivos `.env` no GitHub.
- O cliente pode usar protocolo OpenAI-compatível ou, para integrações específicas, Anthropic-compatível. Compatibilidade **não** significa paridade integral.
- Ferramentas externas, MCP e memória de agentes exigem código no seu orquestrador.
- Exemplos são integrações ilustrativas: requerem rede, saldo e chave válida para operar.

## Checklist de implementação

- [ ] Criar e proteger chave; configurar faturamento.
- [ ] Executar `GET /models` para confirmar acesso.
- [ ] Executar um chat pequeno com `deepseek-flash`.
- [ ] Registrar `usage`, latência, status e identificador da requisição.
- [ ] Implementar timeouts, filas, retries controlados e limites por usuário.
- [ ] Tratar conteúdo gerado como não confiável, especialmente argumentos de ferramentas.
- [ ] Conferir custo, limites, licenças e termos antes de produção.

**Fontes principais:** [Visão geral oficial](https://api-docs.deepseek.com/), [Modelos e preços](https://api-docs.deepseek.com/quick_start/pricing/), [Changelog](https://api-docs.deepseek.com/updates/).
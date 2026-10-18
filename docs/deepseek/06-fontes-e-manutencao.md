# Fontes oficiais, legalidade e plano de manutenção

**Data de conferência:** 18 de outubro de 2026. Este repositório contém documentação original, resumida e ilustrada — **não** uma cópia integral da documentação de terceiros e **não** substitui o contrato, os termos ou a referência oficial.

## Referências primárias

| Assunto | URL |
|---|---|
| Portal de desenvolvedores | https://api-docs.deepseek.com/ |
| Console/API keys | https://platform.deepseek.com/ |
| Primeira chamada | https://api-docs.deepseek.com/quick_start/faq |
| Modelos e preços | https://api-docs.deepseek.com/quick_start/pricing/ |
| Histórico de mudanças | https://api-docs.deepseek.com/updates/ |
| Modelos REST | https://api-docs.deepseek.com/api/list-models/ |
| Chat | https://api-docs.deepseek.com/api/create-chat-completion/ |
| Responses API | https://api-docs.deepseek.com/guides/responses_api/ |
| Anthropic compatibilidade | https://api-docs.deepseek.com/guides/anthropic_api/ |
| Thinking | https://api-docs.deepseek.com/guides/thinking_mode/ |
| Vision | https://api-docs.deepseek.com/guides/vision/ |
| JSON | https://api-docs.deepseek.com/guides/json_mode/ |
| Tool Calling | https://api-docs.deepseek.com/guides/tool_calls/ |
| FIM | https://api-docs.deepseek.com/api/create-completion/ |
| Context caching | https://api-docs.deepseek.com/guides/kv_cache/ |
| Files API | https://api-docs.deepseek.com/guides/files_api/ |
| Search & Fetch | https://api-docs.deepseek.com/guides/search/ |
| Rate Limits | https://api-docs.deepseek.com/quick_start/rate_limit/ |
| Erros | https://api-docs.deepseek.com/quick_start/error_codes/ |
| Saldo | https://api-docs.deepseek.com/api/get-user-balance/ |
| Termos plataforma | https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html |
| Modelos de pesos abertos | https://huggingface.co/deepseek-ai |

## API oficial versus terceiros e modelos locais

- **Oficial e hospedado:** crie conta e chave na plataforma DeepSeek e use `api.deepseek.com`.
- **Provedores externos:** podem oferecer outros modelos, nomes e preços; possuem termos e políticas próprios. Não são sinônimo da API oficial.
- **Pesos abertos:** consulte o card e a licença **de cada repositório** de modelo antes de hospedar localmente ou comercializar. Um modelo aberto não significa acesso gratuito à infraestrutura oficial.
- **Legalidade:** respeite termos, licenças, privacidade, LGPD, propriedade intelectual e legislação aplicável. Não use credenciais compartilhadas indevidamente, scraping protegido ou serviços não autorizados.

## Como manter estas páginas atualizadas

1. Antes de cada release, consultar `GET /models` autenticado e comparar IDs/capacidades.
2. Revisar [Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing/) e atualizar versões, custos e janelas de pico.
3. Revisar [Change Log](https://api-docs.deepseek.com/updates/) para breaking changes.
4. Confirmar cada endpoint, parâmetro, resposta e status nas páginas de referência.
5. Executar smoke tests por linguagem com chave de testes e limite de orçamento.
6. Revisar os exemplos para evitar segredos no histórico do Git e dependências vulneráveis.
7. Registrar data da revisão e link oficial ao lado da alteração.
8. Se uma API estiver em beta/experimental, manter aviso e testes separados.

## Limitações do material

Os trechos aqui descritos refletem as fontes consultadas, não uma chamada autenticada contra a conta do usuário. A compatibilidade de SDKs e compiladores depende de versões instaladas, SO e dependências. Exemplos mínimos não incluem todo o tratamento necessário a aplicações de produção. Nunca informe preços ou limites como permanentes.

Próximo passo de engenharia sugerido: criar testes automatizados para `/models`, `/chat/completions`, `/responses`, tools e medição de custo, **opt-in** e protegidos por segredo no CI.

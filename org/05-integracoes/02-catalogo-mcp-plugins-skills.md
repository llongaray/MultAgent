# 02 · Catálogo público MCP, plugins e skills

> [← Mapa Mestre](../README.md) · [↑ Integrações](README.md) · [OAuth e confiança](03-oauth-tokens-seguranca.md)

## O que queremos construir?

Um **catálogo pesquisável com Internet** para descobrir e conectar ferramentas que ampliem as capacidades dos funcionários de IA. O usuário poderá procurar "GitHub", "Google Drive", "navegador", "arquivo local", "designer" etc., comparar permissões, ver origem/licença, instalar/autorizar e habilitar a integração para agentes específicos.

## Tipos de extensão (não confundir)

| Tipo | Função | Execução / risco |
|---|---|---|
| **MCP remoto** | integra tools/resources/prompts de serviço remoto | chamadas de rede, OAuth/tokens e potencial transferência de dados |
| **MCP local** | processo servidor local que expõe ferramentas | pode executar código no PC — revisão e sandbox necessárias |
| **Plugin** | adaptador/programa da plataforma que estende integração | pode executar código nativo ou Python, requer review |
| **Skill** | instruções, prompts, recursos ou procedimentos para LLM seguir | texto também pode conter prompt injection; se possuir scripts executáveis, tratar como plugin |

O termo "plugin" é nomenclatura do MultAgent; não assumir formato universal. Skills de repositório público também **não são confiáveis por origem**.

## Fontes de catálogo

1. [Registro oficial MCP](https://registry.modelcontextprotocol.io/) como fonte de descoberta de metadados de servidores. **Estar listado não significa que o software foi auditado**.
2. GitHub/GitLab/Bitbucket: repositórios públicos, tags/commit SHA imutável e manifestos compatíveis.
3. Catálogos de terceiros opcionais: integrar somente com termos, licenças e API compatíveis; classificar origem e confiança.
4. Repositório ou diretório fornecido pelo usuário: tratar como fonte não revisada até análise.

A [API oficial do registro](https://registry.modelcontextprotocol.io/docs) permite consultar registros e metadados; a proposta é consumir dados, não executar instalações oferecidas indiscriminadamente.

## Manifesto MultAgent (especificação inicial)

```yaml
api_version: multagent.ext/v1
id: community.example.reader
kind: mcp_remote  # mcp_remote | mcp_local | plugin | skill
name: Example Reader
version: 1.0.0
source:
  registry: https://registry.modelcontextprotocol.io
  repository: https://github.com/ORG/REPO
  ref: 8b57c13...  # commit completo ou tag validada
runtime:
  transport: streamable_http
  endpoint: https://example.org/mcp
auth:
  type: oauth2  # oauth2 | token | ssh | none
permissions:
  - resources.read
  - tools.list
trust:
  verified_by_multagent: false
  requires_user_review: true
  source_digest: sha256:EXEMPLO
```

Esse formato é **proposta de contrato própria do produto**; servidores MCP de terceiros não vão automaticamente fornecer esse YAML. O app usará tradutores do schema oficial e exibirá informação ausente como "não verificada", sem inventar reputação.

## Fluxo instalação/conexão

1. Pesquisar, filtrar por categoria/SO/transporte, examinar publicador, projeto, histórico e permissões declaradas.
2. Abrir detalhe, URL oficial, licença, versão, dependências e se acessa arquivos/contas/rede.
3. Selecionar versão/commit fixado, baixar código **sem executar automaticamente** e conferir integridade.
4. Resolver dependências numa sandbox/ambiente isolado e gerar resumo do que será instalado.
5. Se houver OAuth compatível, abrir autorização do serviço; do contrário pedir configuração de token ou modo anônimo.
6. Criar `IntegrationInstance` ligada ao usuário/tenant, **inicialmente desativada**; testar `list_tools` sem permissões de escrita.
7. Usuário habilita ferramentas por agente e workspace; os parâmetros serão validados e operações sensíveis exigem confirmação.
8. Registrar versão, hashes, origem, consentimento; permitir desabilitar/desinstalar e revogar credenciais.

**Instalar não implica confiar**: evitar executar `npm install`/`pip install` com post-install ou scripts arbitrários fora de isolamento; pacotes de linguagem podem executar código durante a instalação. A instalação de MCP local deve passar por revisão, privilégios mínimos e allowlist de execução.

## Segurança operacional

- Usar allowlists de ferramentas por integração. Nunca enviar vault, conteúdo de outros repositórios ou ambiente completo à extensão.
- Evitar aceitar redirects HTTP inesperados ou SSRF em URLs externas; validar DNS/IP privado, transport TLS e origem em uso remoto.
- Não carregar automaticamente prompts de skill como instrução de sistema superior; marcar como conteúdo externo.
- Egress/network, filesystem e subprocessos de extensões locais em sandbox; permitir negar ferramentas de escrita.
- Atualizações de extensão exigem revisão das diferenças de permissões, código e publisher; evitar atualização silenciosa executável.
- Contador de invocações, custos e logs com origem para ferramenta, inclusive as chamadas server-side quando visíveis.

## Roadmap do catálogo

- **MVP 1:** listar e conectar MCP remoto HTTPS conhecido manualmente; vínculo por agente, schema de tools e logs.
- **MVP 2:** pesquisa pelo Registro oficial MCP; ficha/manifesto e consentimento; OAuth2 suportado.
- **MVP 3:** instalar MCP local com sandbox, fixar versão e desinstalar.
- **MVP 4:** plugins e skills públicos a partir de repositórios Git, com scanner, revisão de dependências e políticas de atualização.

**Documentação externa:** [MCP Registry](https://registry.modelcontextprotocol.io/), [MCP client registration/OAuth](https://blog.modelcontextprotocol.io/posts/client_registration/).

**Relacionado:** [OAuth e Vault](03-oauth-tokens-seguranca.md) · [Acesso máquina](../02-arquiteturas/11-acesso-maquina-e-isolamento.md) · [Mapa Mestre](../README.md).

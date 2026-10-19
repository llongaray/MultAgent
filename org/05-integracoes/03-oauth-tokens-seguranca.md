# 03 · OAuth, tokens, vault, autenticação e política de confiança

> [← Mapa Mestre](../README.md) · [↑ Integrações](README.md) · [Catálogo MCP](02-catalogo-mcp-plugins-skills.md) · [Acesso ao PC](../02-arquiteturas/11-acesso-maquina-e-isolamento.md)

## Objetivo

Oferecer uma experiência "Conectar" no painel de Integrações, permitindo ao usuário vincular um serviço por OAuth sempre que o **serviço e a integração suportarem isso**, sem precisar copiar credenciais manualmente. Quando OAuth não estiver disponível, oferecer fluxo de chave/API token limitado, SSH ou configuração de credencial definida pelo conector.

**OAuth não é universal:** não se pode instalar um MCP arbitrário nem obter OAuth de um repositório só por existir um catálogo público. É necessário um servidor de autorização compatível, escopos definidos, redirect URI/registro de cliente e consentimento explícito.

## Desktop sem interface web

A GUI PySide6 abre o **navegador do sistema exclusivamente para a página de autenticação externa**, se necessário, mas **não vira um aplicativo web**. Quando o provedor suportar, usar fluxo Authorization Code + PKCE com retorno por URI registrada no OS ou por callback loopback temporário (exceção estritamente limitada à operação OAuth, sem servir interface HTTP). Para conectores compatíveis, o **Device Authorization Grant** evita callback; ver disponibilidade no provedor. Definir state/nonce quando aplicável, validar redirect/audience e proteger contra CSRF e token injection.

## Server

A versão Server usa callback HTTPS na origem administrativa autorizada, integra OAuth/PKCE conforme requisitos do provedor, valida sessão e usuário, autentica papéis/tenant e armazena tokens em vault do servidor. Se o servidor não tiver URL pública/certificado, prover alternativa oficialmente suportada em vez de abrir listener temporário inseguro. Autorização de um usuário não disponibiliza seus recursos aos demais tenants.

## Fluxo de conexão

1. Selecionar provedor e integração na UI.
2. Mostrar identidade/publicador, scopes exatos, recursos requisitados, dados transferidos e risco de execução.
3. Iniciar fluxo OAuth nativo do provedor com parâmetros/PKCE; usuário autentica **diretamente** com o serviço.
4. Validar estado, token, audience, scopes, expiração e titular/organização; exibir repositórios/recursos acessíveis.
5. Guardar access/refresh token no **cofre protegido**, sem enviar à IA.
6. Vincular integração a `IntegrationInstance`, grants por agente/tenant/recurso e data de validade.
7. Renovar somente dentro da política, detectar revogação e desabilitar funções ao perder a autorização.
8. Permitir botão **Desconectar e revogar**, com remoção local e revogação remota quando API permitir.

## Camadas de permissão diferentes

| Camada | Controle |
|---|---|
| Conta do provedor | OAuth scopes, token e acesso real concedido à aplicação |
| Permissões do workspace | repositórios, branches, diretórios, hosts e apps autorizados |
| Permissões da integração | ferramentas MCP/plugin específicas: leitura/escrita/execução |
| Permissões por agente | interseção de grants, papel, equipe e autonomia |
| Sistema operacional | permissões da identidade que executa o worker/sandbox |
| Elevação administrativa | broker separado com aprovação e prazo delimitados |

**Negar por padrão**, inclusive em conflitos de política. A GUI deve mostrar **permissão solicitada** versus **permissão efetiva**; uma credencial com privilégio elevado não deve ser liberada para qualquer agente automaticamente.

## Segurança do catálogo e das conexões

- Validar TLS e URLs de callback; redirecionamento inseguro ou a outro domínio exige reprovação.
- Verificar integridade de package/commit/manifesto e não executar hook `postinstall` automaticamente com privilégios.
- Extensões listadas no MCP Registry **não são necessariamente auditadas nem confiáveis**; catálogo é fonte de descoberta.
- Skills que tenham instruções hostis ou código externo são dados não confiáveis; **não** herdam permissões de sistema.
- Impedir exfiltração por ferramenta: validação dos dados enviados, política de egress, isolamento de credenciais e auditoria.
- Suportar refresh/revogação de token com cuidado para não sobrescrever sessão de outra integração.
- Não incluir segredo em logs, prompts, traces, exceções ou arquivo de exportação; oferecer mascaramento na interface.

## Fontes oficiais de referência

- [MCP Registry](https://registry.modelcontextprotocol.io/) e sua [API](https://registry.modelcontextprotocol.io/docs).
- [MCP: evolução do registro de clientes e OAuth](https://blog.modelcontextprotocol.io/posts/client_registration/) — autorização OAuth, mecanismos e desafios de clientes distribuídos.
- [GitHub Apps e OAuth: permissões granulares](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps).
- [Bitbucket Cloud REST e autenticação](https://developer.atlassian.com/cloud/bitbucket/rest/).
- [GitLab OAuth Provider](https://docs.gitlab.com/integration/oauth_provider/).

**Navegação:** [Catálogo](02-catalogo-mcp-plugins-skills.md) · [Git e SSH](01-git-repositorios-ssh.md) · [Roadmap](05-caminho-de-implementacao.md).

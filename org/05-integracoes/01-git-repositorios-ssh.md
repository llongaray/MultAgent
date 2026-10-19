# 01 · Git local, GitHub, GitLab, Bitbucket e SSH

> [← Mapa Mestre](../README.md) · [↑ Integrações](README.md) · [Permissões](../02-arquiteturas/11-acesso-maquina-e-isolamento.md)

## Escopo

Permitir que cada funcionário opere um ou mais repositórios **especificamente selecionados**, locais ou remotos, por um adaptador de Git e conectores de API. Cada projeto é um `Workspace` persistente, com URL/origem, path, branch, credencial e grants vinculados. O agente **não** herda todos os repositórios do usuário por padrão.

## Fontes de repositório

| Fonte | Métodos planejados | Observações |
|---|---|---|
| Pasta local Git | `git status`, logs, worktrees, commits, diffs e testes | validar caminho e permissões |
| GitHub | Git HTTPS/SSH + GitHub App quando adequado | instalação por repositórios selecionados; permissões granulares |
| GitLab | Git HTTPS/SSH + OAuth/API conforme instance | suportar GitLab.com e self-managed com URLs explicitamente confiáveis |
| Bitbucket Cloud | Git HTTPS/SSH + OAuth/Access Token/API | tokens restritos ao repo/projeto quando possível |
| Git remoto genérico | URL Git HTTPS/SSH fornecida pelo usuário | funcionalidades PR/issues não garantidas |
| Máquina remota SSH | host, user, chave no vault/agent, pasta autorizada | execução/arquivos com conta de pouca permissão |

## Como configurar um workspace

1. Escolher **Novo recurso → Repositório local / GitHub / GitLab / Bitbucket / Git URL / SSH**.
2. Local: selecionar diretório pelo picker nativo. Remoto: autenticar por OAuth quando suportado pelo provedor ou associar chave SSH/token do vault.
3. Listar repositórios acessíveis e pedir seleção explícita dos repositórios que o MultAgent poderá usar.
4. Atribuir permissões de `read` / `patch` / `commit` / `push` / `PR` / `merge` por repo e, quando aplicável, branch.
5. Clonar em workspace controlado ou criar **git worktree** dedicada para cada tarefa/branch; bloquear alterações em `main`/`master`/`production` por padrão.
6. Vincular workspace a funcionário(s) e equipe com teto de custo, regras de autonomia, testes e aprovação para ações de publicação.
7. Executar tarefa → inspecionar diff/testes → criar commit/PR ou pedir revisão antes de push.

## Operações que a ferramenta pode expor

```text
git.repositories.list(source_id)
git.workspace.open(repo_id, branch, path)
git.file.read(workspace_id, relative_path)
git.patch.propose(workspace_id, patch)
git.tests.run(workspace_id, predefined_task_id)
git.commit.create(workspace_id, message)
git.remote.push(workspace_id, branch)
git.pull_request.create(workspace_id, target_branch)
ssh.host.connect(host_id)
ssh.file.read(host_id, approved_path)
ssh.command.run(host_id, allowed_command_id, arguments)
```

Schemas e autorização próprios em cada chamada; parâmetros livres não são instruções shell. O orquestrador bloqueia traversal, symlink escape, sobrescrita concorrente, branch inesperada e acesso fora dos grants. Scripts do repositório (`package.json`, `Makefile`, hooks etc.) são **código de terceiros**: executá-los exige ambiente isolado, limites de rede e segurança adicional.

## Preferências de autenticação

- **GitHub Apps** são preferíveis a um OAuth App amplo quando o fluxo exigir seleção de repositórios e permissões granulares; instalação OAuth/login via navegador externo ou método suportado, tokens armazenados no vault. Docs: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps
- **GitLab:** métodos dependem da instância e versão (OAuth, Project/Group/Personal Access Tokens, deploy keys, SSH). Respeitar a política da instância: https://docs.gitlab.com/integration/oauth_provider/
- **Bitbucket:** OAuth 2.0 ou Repository/Project/Workspace Access Tokens, com menor alcance disponível; a plataforma define permissões/rotas. Docs: https://developer.atlassian.com/cloud/bitbucket/rest/
- **SSH:** utilizar implementação/agent SSH do sistema ou biblioteca com suporte a known_hosts/host key verification, pin de host e contas de serviço específicas. Não aceitar host key nova de forma silenciosa, nem registrar chave privada.

## Exemplo de projeto

O usuário autoriza `D:\Projetos\MinhaAPI` para agente "Dev Backend" com `read + patch`; agente "Testador" tem acesso `read + run_tests`; gerente acompanha e revisa; apenas usuário ou agente com `PR approved` faz push. O mesmo fluxo pode usar `/home/user/projetos/api` ou clone remoto GitLab em worktree. O agente só vê o workspace autorizado.

## SSH para servidores

SSH não significa automaticamente root. Hosts devem ter credencial específica, conta de menor privilégio, comandos e pastas permitidos, execução com timeout, limite de upload/download e logs. Suporte a tunelamento/port forwarding ou `sudo` remoto **não** será habilitado por padrão; exige concessão explícita e broker/política independente.

## Aceite para MVP

Importar repositório local, visualizar arquivos autorizados, criar worktree, propor patch, rodar testes em ambiente isolado e mostrar diff. Em seguida GitHub App/OAuth e PR; depois GitLab/Bitbucket; SSH somente após suporte completo a host key verification e grants.

**Relacionado:** [Processos](../02-arquiteturas/10-hierarquia-processos-e-politicas.md) · [OAuth](03-oauth-tokens-seguranca.md) · [Roadmap](05-caminho-de-implementacao.md).

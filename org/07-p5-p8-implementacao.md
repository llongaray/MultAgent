# MultAgent — P5–P8, matriz de funcionalidades e limites de segurança

> [Mapa Mestre](README.md) · [Distribuição Desktop/Server](04-distribuicao/04-edicoes-desktop-server.md)

Esta página distingue **código implementado** de **integrações e operações que exigem infraestrutura/credenciais para homologação real**. Não publicar tokens, SSH private keys ou certificados TLS no GitHub.

| Etapa | Implementação técnica | Limitações que não podem ser ocultadas |
|---|---|---|
| P5-01 | CLI `multagent-server init/start/status/doctor/version`, FastAPI, login scrypt, sessões HttpOnly, CSRF, bind/porta e TLS obrigatório para bind externo | status é diagnóstico de configuração, não daemon manager; workers e ACL multiusuário não entregues; monitoramento externo depende do SO |
| P5-02 | React/TS + Vite, login, funcionários, modo, histórico/auditoria, build e arquivos servidos somente pelo Server | criar/revogar chaves e execução via Server dependem de backend/vault e políticas adicionais; frontend exige build Node para desenvolvimento |
| P6-01 | Git local: grants workspace/actor/resource, status/diff, worktrees após confirmação, path/symlink boundary e timeout | integração Git não substitui aprovação humana de patches e alteração remota |
| P6-02 | allowlist curta, execução Linux via bubblewrap sem rede/montagem host, saída limitada e sem fallback | Windows bloqueado até existir sandbox equivalente; kernels sem user namespaces podem recusar bwrap |
| P7-01 | GitHub: branches, issues, criação de PR, branch e commit-file com escopos e confirmação; tokens de acesso/instalação fornecidos via vault | processo de registro/login OAuth e emissão inicial de tokens GitHub App NÃO implementados; sem credenciais reais não há teste de E2E |
| P7-02 | GitLab/Bitbucket: lista de branches/issues e abertura de merge/pull requests via tokens e grants | OAuth login delegado e criação de commits específica de cada provedor pendentes |
| P7-03 | SSH com host key obrigatória, key no vault, root proibido, comandos fixos e limite de timeout | sem permissões root, shell remota arbitrária ou execução de scripts |
| P8-01 | cliente MCP HTTP remoto via SDK, descoberta de ferramentas e execução opt-in com grant; registry lê apenas metadados | cliente stdio local, OAuth automático e validação JSON Schema detalhada pendentes; nunca instalar entradas do Registry automaticamente |
| P8-02 | catálogo local pinned SHA256 + licença/origem, instalar/atualizar como nova versão/remover sob aprovação e SDK tipado | **execução de plugin está DESATIVADA** até sandbox de plugins validada para cada SO |
| P8-03 | importar Markdown com revision SHA fixa + checksum, GitHub/GitLab autorizados, quarentena por workspace | execução de scripts ou instruções importadas não é autorizada |

**Critério de publicação:** módulos P5–P8 podem ser integrados ao repositório para evolução incremental com testes de comportamento restritivo, sem anunciar que tarefas inseguras/sem infraestrutura estão concluídas. O cadastro de credenciais reais e autorização de operações pagas/remotas exige iniciativa do administrador.

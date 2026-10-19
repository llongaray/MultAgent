# 04 · Critérios de validação da estrutura e do software futuro

> [← Mapa Mestre](../README.md) · [↑ Desenvolvimento](README.md) · [Estrutura](01-mapa-de-pastas.md)

## Checklist desta etapa (somente documentação)

- [x] Criar diretórios do núcleo Python e módulos especializados com `README.md`.
- [x] Criar pastas distintas Desktop Qt e Server FastAPI/React.
- [x] Criar documentação de CLI, instaladores, testes e release.
- [x] Criar documentação para GitHub, GitLab, Bitbucket, SSH, MCP, OAuth, plugins e skills.
- [x] Reservar pastas para GitHub Actions, exemplos, configurações e assets.
- [ ] Implementar código Python/React e scripts — **fora do escopo desta etapa**.
- [ ] Compilar, executar testes ou publicar GitHub Releases — **fora do escopo desta etapa**.

## Matriz de critérios para marcos futuros

| Componente | Condição de aceite futura |
|---|---|
| Core | contratos tipados e testes que não importem GUI/HTTP |
| Desktop | executável nativo Qt, abre janela sem HTTP |
| Server | inicia headless com porta/bind configuráveis e autenticação |
| Multiagentes | duas ou mais IAs configuráveis por equipe, hierarquia validada |
| Git | diffs/branches/worktrees somente em repositórios autorizados |
| SSH | host key verificada, conta limitada e ações auditadas |
| MCP/plugin/skill | origem, hash, permissões e instalação segura |
| Privilege Broker | operação específica, autorização humana e execução isolada |
| Distribuição | artefatos por Windows/Linux e por edição, verificáveis |

## Validação documental

A validação de README e links locais verifica apenas **organização da documentação**, não funcionalidade do software. A fase atual não valida APIs reais, binários Qt, sistema operacional, autenticação OAuth ou isolamento do broker: tudo isso depende de implementação e testes posteriores.

**Próxima etapa:** [Roteiro para construção](../05-integracoes/05-caminho-de-implementacao.md) · [Mapa físico](01-mapa-de-pastas.md).

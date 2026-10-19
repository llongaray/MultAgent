# src/multagent/ — Pacote Python da aplicação

> [← Mapa Mestre](../../org/README.md) · [↑ src](../README.md) · [Guia de desenvolvimento](../../org/06-desenvolvimento/README.md)

**P0-01 — bootstrap implementado neste PR:** `src/multagent/__init__.py` fornece importação e versão `0.0.1.dev0` sem efeitos colaterais; `py.typed` sinaliza tipagem. Os módulos de domínio, ferramentas, provedores e interfaces permanecem somente documentados.

## Responsabilidade

Reunir os componentes compartilhados de DeepSeek/Grok, políticas, agentes e workflows, além dos entrypoints separados **Desktop PySide6/Qt** e **Server FastAPI/React**.

## Instalação local do pacote-base

Na raiz do repositório: `python -m pip install -e .`. Validar `python -c "import multagent; print(multagent.__version__)"`. Isso **não** disponibiliza comandos `multagent`/`multagent-server`; esses entrypoints dependem das respectivas implementações futuras.

## Submódulos previstos

- [core](core/README.md): domínio, orquestração, router e workflows.
- [providers](providers/README.md): interfaces de provedores e DeepSeek/Grok.
- [agents](agents/README.md): funcionários, equipes e perfis.
- [tools](tools/README.md): gateway, MCP, plugins e skills.
- [integrations](integrations/README.md): Git, GitHub, GitLab, Bitbucket, SSH, apps, catálogo e OAuth.
- [security](security/README.md): vault, grants, isolamento e broker administrativo.
- [storage](storage/README.md): SQLite e opção PostgreSQL.
- [observability](observability/README.md): logs, traces e custo.
- [desktop](desktop/README.md): GUI nativa Qt.
- [server](server/README.md): API e workers headless.
- [cli](cli/README.md): comandos e diagnóstico.

## Dependências permitidas

`desktop` e `server` importam serviços do core; **o core nunca importa interfaces**. Agentes não recebem root/Administrador diretamente; ações privilegiadas passam por um broker separado com autorização explícita.

**Referências:** [Arquitetura compartilhada](../../org/02-arquiteturas/09-desktop-server-core-compartilhado.md) · [Permissões](../../org/02-arquiteturas/11-acesso-maquina-e-isolamento.md).

# 06 · Guia de desenvolvimento e estrutura do repositório

> [← Mapa Mestre](../README.md) · [Missão](../00-fundamentos/05-proposito-e-casos-de-uso.md) · [Roadmap](../05-integracoes/05-caminho-de-implementacao.md)

**Estado: apenas planejamento/documentação.** Esta seção detalha a estrutura de diretórios reservados ao futuro código-fonte do MultAgent. Nenhum arquivo Python, TypeScript, instalador ou workflow de CI/CD funcional foi criado por esta organização.

## Estrutura prevista

- [Mapa das pastas e artefatos](01-mapa-de-pastas.md)
- [Contratos e limites dos módulos](02-contratos-e-dependencias.md)
- [Regras de documentação e contribuições futuras](03-padroes-de-documentacao.md)
- [Critérios de aceite e evolução por etapas](04-validacao-e-aceite.md)

## Produtos do mesmo repositório

- **Desktop**: interface nativa PySide6/Qt em Windows 10/11, Ubuntu e Debian, sem painel web ou porta HTTP.
- **Server**: binário headless Windows/Linux com FastAPI, porta configurável, autenticação e painel React.
- **Core Python**: workflows hierárquicos, provedores DeepSeek/Grok, agentes, Git/SSH, MCP e políticas compartilhados.

Cada diretório da futura implementação terá um `README.md` com propósito, módulos previstos, limites de responsabilidade e testes. Criar código executável somente nas próximas fases aprovadas.

**Consulte:** [Arquitetura](../02-arquiteturas/README.md) · [Integrações](../05-integracoes/README.md) · [Distribuição](../04-distribuicao/README.md).

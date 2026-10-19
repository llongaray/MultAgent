# src/ — Código-fonte futuro do MultAgent

> [← Mapa Mestre](../org/README.md) · [Estrutura planejada](../org/06-desenvolvimento/README.md)

**Somente estrutura documental.** Não existem módulos Python executáveis nesta pasta.

O código de produção será mantido em [`src/multagent/`](multagent/README.md), dividido entre núcleo de negócio, agentes, provedores, ferramentas, recursos, persistência, segurança, telemetria e as duas interfaces independentes.

**Regra principal:** `core/` não importa PySide6, FastAPI nem React; `desktop/` e `server/` são adaptadores. Desktop não abre porta HTTP. Server não depende de Qt.

**Próximo marco:** definir contratos de domínio e testes antes de criar arquivos `.py`. [Roadmap](../org/05-integracoes/05-caminho-de-implementacao.md).

# Testes unitários

> [← Mapa Mestre](../../org/README.md) · [↑ Pasta pai](../README.md) · [Guia técnico](../../org/06-desenvolvimento/README.md)

**Estado P0-01:** `test_package_bootstrap.py` implementa testes de versão, metadados, ausência de inicialização da GUI/HTTP na importação e sinalização de pacote tipado. Não são testes funcionais de agentes.

## Propósito

Core, modelos, regras e autorização com mocks.

## Componentes previstos

Pydantic, router, DAG, grants, gateway.

## Restrições

Nunca gastar tokens reais em testes unitários.

## Execução

Na raiz do repositório, em ambiente Python 3.11+: `python -m pip install -e ".[dev]"` e `python -m pytest`. A CI automatizada continua fora do escopo P0-01.

## Validação futura

Casos de sucesso/falha sem rede.

**Referências:** [Arquitetura Desktop e Server](../../org/04-distribuicao/04-edicoes-desktop-server.md) · [Roadmap](../../org/05-integracoes/05-caminho-de-implementacao.md).

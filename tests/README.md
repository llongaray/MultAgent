# Plano de testes

> [← Mapa Mestre](../org/README.md) · [↑ Pasta pai](../README.md) · [Guia técnico](../org/06-desenvolvimento/README.md)

**Estado P0-01:** testes de bootstrap do pacote Python adicionados em [unit/test_package_bootstrap.py](unit/test_package_bootstrap.py); a aplicação multiagente ainda não possui testes funcionais.

## Propósito

Organizar testes por módulo e plataforma.

## Componentes previstos

Unitários, integração, ponta a ponta, segurança e OS.

## Restrições

`python -m pytest` valida apenas o pacote-base. Testes de orquestração, políticas, integrações e GUI continuam pendentes. CI específica do projeto está planejada para P0-05.

## Validação futura

Critérios de aceite documentados.

**Referências:** [Arquitetura Desktop e Server](../org/04-distribuicao/04-edicoes-desktop-server.md) · [Roadmap](../org/05-integracoes/05-caminho-de-implementacao.md).

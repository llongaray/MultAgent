# Isolamento da execução

> [← Mapa Mestre](../../../../org/README.md) · [↑ Pasta pai](../README.md) · [Integrações e permissões](../../../../org/05-integracoes/README.md)

**Status: somente documentação.** Ainda não há código implementado neste diretório.

## Finalidade

Impedir que scripts e plugins extrapolem permissões.

## Interfaces e componentes previstos

Workers isolados, FS/egress policy, limites e cleanup.

## Segurança e limites

Allowlist de path isolada não substitui sandbox real de subprocesso.

## Validação futura

Exploração de paths, rede e processos.

**Referências:** [Caminho de implementação](../../../../org/05-integracoes/05-caminho-de-implementacao.md) · [Acesso à máquina](../../../../org/02-arquiteturas/11-acesso-maquina-e-isolamento.md).

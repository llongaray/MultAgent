# Broker de operações elevadas

> [← Mapa Mestre](../../../../org/README.md) · [↑ Pasta pai](../README.md) · [Integrações e permissões](../../../../org/05-integracoes/README.md)

**Status: somente documentação.** Ainda não há código implementado neste diretório.

## Finalidade

Permitir operações administrativas determinadas com consentimento explícito.

## Interfaces e componentes previstos

IPC autenticado, allowlist de operações, expiração, auditoria.

## Segurança e limites

Agente não recebe sudo/admin, prompt não vira comando privilegiado.

## Validação futura

Revisão adversarial e negativa de abuso.

**Referências:** [Caminho de implementação](../../../../org/05-integracoes/05-caminho-de-implementacao.md) · [Acesso à máquina](../../../../org/02-arquiteturas/11-acesso-maquina-e-isolamento.md).

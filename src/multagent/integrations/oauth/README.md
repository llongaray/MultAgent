# Conexão OAuth

> [← Mapa Mestre](../../../../org/README.md) · [↑ Pasta pai](../README.md) · [Integrações e permissões](../../../../org/05-integracoes/README.md)

**Status: somente documentação.** Ainda não há código implementado neste diretório.

## Finalidade

Autenticar em provedores externos quando suportado.

## Interfaces e componentes previstos

Authorization Code + PKCE, device grant quando cabível, refresh/revocation.

## Segurança e limites

Segredos no vault, scopes mostrados, callback seguro.

## Validação futura

CSRF state, revogação, expirado e escopos ausentes.

**Referências:** [Caminho de implementação](../../../../org/05-integracoes/05-caminho-de-implementacao.md) · [Acesso à máquina](../../../../org/02-arquiteturas/11-acesso-maquina-e-isolamento.md).

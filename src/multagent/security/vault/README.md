# Cofre de credenciais

> [← Mapa Mestre](../../../../org/README.md) · [↑ Pasta pai](../README.md) · [Integrações e permissões](../../../../org/05-integracoes/README.md)

**Status: somente documentação.** Ainda não há código implementado neste diretório.

## Finalidade

Guardar chaves DeepSeek/Grok, Git e SSH.

## Interfaces e componentes previstos

Windows Credential Manager; Linux Secret Service/KWallet ou vault protegido; Server secrets.

## Segurança e limites

Sem plaintext em SQLite/YAML/log; não enviar segredo a modelos.

## Validação futura

Persistência, rotação e revogação.

**Referências:** [Caminho de implementação](../../../../org/05-integracoes/05-caminho-de-implementacao.md) · [Acesso à máquina](../../../../org/02-arquiteturas/11-acesso-maquina-e-isolamento.md).

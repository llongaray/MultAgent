# P9-02 — Broker de privilégio restrito

**Implementado (código e testes):** solicitações assinadas HMAC-SHA256, validade <=60s, nonce consumido uma vez, confirmação humana explícita, grants por usuário/agente/workspace, auditoria de tentativa/resultado; API de IPC via AF_UNIX em diretório 0700 / AF_PIPE com authkey independente em Windows. Allowlist inicial somente `restart-service` do serviço `multagent-server`; subprocesso sem shell, timeout e verificação de OS-admin. A execução NUNCA concede shell/root ao modelo ou recebe comandos arbitrários.

**Importante:** implementar transporte e validação NÃO instala um serviço privilegiado, NÃO fornece consentimento seguro da tela do OS e NÃO concede elevação. O administrador deve registrar/iniciar um helper isolado com chaves geridas fora do LLM, políticas do sistema operacional e permissão explícita; `execute_admin_operation` recusa se não estiver elevado. A integração UAC/sudo/polkit e E2E em Windows/Linux ainda exigem implantação e revisão adversarial. Não usar este código como um serviço root em produção sem essas verificações.

Testes de negação, replay, assinatura falsa, TTL, paths de socket e auditabilidade são cobertos pela CI. Nenhuma operação administrativa real é chamada em testes.

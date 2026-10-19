# P9 — implementação e validação operacional

| Requisito | Entregue em código | Ainda exige teste/implantação |
|---|---|---|
| P9-01 UIA Windows | Adaptador opcional pywinauto, janela por PID/handle e InvokePattern em botões nomeados | Executar E2E em aplicativo controlado Windows 10/11 |
| P9-01 Linux AT-SPI | Adaptador pyatspi, inventário/seleção/ação sem injeção global de teclado | Testar X11/Wayland em Ubuntu/Debian reais, incluindo estado de acessibilidade |
| P9-01 Segurança | Consentimento para descoberta/seleção/invocação, grants por recurso, auditoria | Revisão de abuso de UI e proteção contra interface que troca janela |
| P9-02 broker | Assinatura HMAC, TTL, nonce de uso único persistido, grants revalidados, auditoria, transportes AF_UNIX/AF_PIPE | Instalar helper de administrador via systemd/UAC seguro, autenticar operadores, testar em host real |
| P9-02 operações | Allowlist fixa **somente** restart do MultAgent Server, comandos sem shell e privilégios OS validados | Aprovação do operador no prompt de elevação; testes adversariais do helper antes de executar ações reais |

**Não confundir testes unitários/IPC com certificação de elevação real.** A conexão entre o host Qt (que apresenta o consentimento) e o broker privilegiado e o mecanismo de instalação/registro do helper dependem de ambiente e de um modelo de ameaça revisado. Nenhum modelo de IA recebe credenciais administrativas ou autorização permanente.

Para Windows UIA instalar o extra opcional `multagent[automation-windows]`. Em Linux instalar `python3-pyatspi` usando o gerenciador da distribuição e executar na sessão gráfica local autorizada.

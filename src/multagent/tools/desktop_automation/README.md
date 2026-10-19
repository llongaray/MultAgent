# P9-01 — automação controlada por acessibilidade

Implementados: inventário de janelas, seleção de janela por identidade PID+handle/índice, grants por workspace e agente, expiração implícita ao mudar o alvo, aprovação humana a cada ação, auditoria no SQLite. API `DesktopAutomation` e adaptadores opcionais `WindowsUIABackend` (pywinauto/UI Automation) e `LinuxATSPIBackend` (pyatspi/AT-SPI).

**Limite de segurança:** somente invocação de botão acessível nomeado; sem teclado livre, atalhos globais, screenshots, campos de senha, injeção física de mouse/teclado ou controle elevado. Nenhuma automação roda sem interface gráfica e permissões de acessibilidade. No Linux, a disponibilidade depende do aplicativo expor AT-SPI em X11/Wayland; essa API não contorna limitações do compositor.

**Testes:** mocks de seleção, mudança de janela, grants, consentimento e auditoria. Testes manuais contra aplicativos gráficos reais ainda são necessários nas duas plataformas. Não declarar conformidade E2E apenas com CI headless.

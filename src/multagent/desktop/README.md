# MultAgent Desktop Qt

> [← Mapa Mestre](../../../org/README.md) · [↑ Pasta pai](../README.md) · [Guia técnico](../../../org/06-desenvolvimento/README.md)

## Estado técnico

O Desktop PySide6 possui interface nativa para funcionários, integrações, permissões, execuções e auditoria. Não inicia serviço HTTP nem exige navegador.

### V002-T02 — edição de funcionários

A janela **Funcionários → Editar funcionário** permite alterar nome, cargo, provedor, modelo, supervisor, ativo/inativo e instruções. ID e workspace permanecem imutáveis. A escolha de supervisor é restrita a outros funcionários do workspace; o `AgentRegistry` rejeita hierarquias cíclicas. Cancelar não altera o registro; campos obrigatórios inválidos são rejeitados antes de persistir em SQLite. Uma edição aceita atualiza a tabela e mantém o funcionário selecionado.

Testes automatizados: `tests/unit/test_v002_t02_agent_edit.py` e `tests/unit/test_p4_desktop.py`.

**Limites:** a interface não implementa ainda gerenciamento visual completo de equipes (V002-F07) ou seletores de grants (V002-T03). Testes unitários em Qt offscreen não substituem homologação manual no Windows 11.

## Homologação no Windows

1. Instalar dependências: `python -m pip install -e ".[desktop,dev]"`.
2. Executar `python -m pytest -q tests/unit/test_v002_t02_agent_edit.py tests/unit/test_p4_desktop.py`.
3. Abrir `multagent`; criar um funcionário, editar seus atributos, fechar e reabrir.
4. Conferir persistência, cancelamento, validação de campos vazios, supervisor e estado ativo.
5. Confirmar que nenhum servidor HTTP é aberto no Desktop.

Nenhuma API externa paga é necessária nesta homologação.

### Correções de revisão da V002-T02

- A coluna Estado distingue **Desativado** de **Suspenso pela política**. A lista de Execuções exibe o motivo e uma tentativa de iniciar um funcionário desativado é bloqueada com mensagem específica antes de qualquer chamada externa.
- A validação é executada ao clicar em Salvar, mantendo o diálogo aberto com os dados digitados quando o domínio ou a hierarquia rejeitam a alteração.
- Caso o supervisor persistido não esteja disponível no workspace, o diálogo apresenta a referência ausente. Salvar mantendo-a selecionada é recusado sem fechar o formulário; selecionar **Sem supervisor** ou outro funcionário válido permite reparar o vínculo.
- Os testes usam `objectName` estável nos widgets e cobrem persistência, cancelamento, validação, hierarquia cíclica e supervisor ausente.

### V002-T03 — permissões visuais (em revisão)

A aba Permissões usa um seletor de funcionários do workspace (nome e ID abreviado), no lugar da digitação manual do identificador. Quando o tipo de recurso é `directory`, o botão **Selecionar pasta…** abre o seletor nativo Qt e preenche o caminho. Para tipos Git, SSH, app e tool, mantém-se o campo de identificador, e o seletor de pastas fica desabilitado.

A criação de grant exige seleção explícita de funcionário e continua submetida ao ResourceManager e à validação de permissões do core. Não há concessão automática. Testes: `tests/unit/test_v002_t03_visual_permissions.py`. Homologação manual Windows e CI ainda necessárias.

#### Ajustes após revisão

- A tabela de grants mostra o nome do funcionário e o identificador abreviado. O UUID integral permanece preservado no SQLite para operações de revogação e auditoria. Se o funcionário foi excluído, o texto **Funcionário ausente** explicita a referência órfã.
- Mudar o tipo de recurso limpa o campo de caminho/identificador, impedindo reutilização acidental de uma pasta como identificador Git/SSH/app/tool. O botão de seleção de pasta permanece exclusivo de `directory`.
- Testes de regressão garantem apresentação legível e bloqueio de concessão com locator vazio após a troca de tipo.

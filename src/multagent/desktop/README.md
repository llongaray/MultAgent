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

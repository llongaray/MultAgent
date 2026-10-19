# 05 · Propósito, missão e casos de uso do MultAgent

> [← Mapa Mestre](../README.md) · [↑ Fundamentos](README.md) · [Arquitetura de hierarquia](../02-arquiteturas/10-hierarquia-processos-e-politicas.md) · [Integrações](../05-integracoes/README.md)

## Missão do produto

**O MultAgent é uma plataforma open-source que permite ao usuário transformar seu computador pessoal ou servidor em um ambiente de execução de múltiplos agentes de IA especializados, organizados em uma hierarquia de trabalhos e dotados de acesso configurável a arquivos, projetos, aplicativos, repositórios Git e serviços externos.**

O usuário cria **funcionários virtuais** (agentes) e define para cada um: nome, objetivo, cargo/papel, provedor e modelo DeepSeek ou Grok, equipe/supervisor, ferramentas, escopo de pastas/repositórios, limite de custo, autonomia, aprovações e agenda. A plataforma coordena subtarefas e devolve **entregas concretas**, não apenas mensagens de chat.

**O produto não executa tarefas de forma magicamente ilimitada:** permissões do SO, ambiente gráfico, capacidade dos programas, quotas das APIs e políticas das contas Git limitam o que é possível automatizar. Cada ação precisa ser instrumentada por adaptador/ferramenta, não apenas solicitada ao LLM.

## Experiência pretendida

1. Usuário instala **MultAgent Desktop** (janela PySide6/Qt) ou **MultAgent Server** (headless + FastAPI/React); escolhe o modo de operação.
2. Em **Integrações**, vincula DeepSeek e/ou Grok com sua chave, seleciona modelo e orçamento; configura Github/GitLab/Bitbucket, SSH, apps, MCPs, skills ou plugins.
3. Em **Recursos**, aprova pastas locais, workspaces Git, hosts SSH ou apps específicos (sempre com privilégios explícitos).
4. Em **Funcionários**, cria agentes, define papéis, subordinação, ferramentas, limites e provedores individuais.
5. Em **Processos**, desenha fluxo de aprovação, dependências, recorrência, condição de sucesso e entregáveis.
6. Agentes executam etapas em workers, com histórico, progresso, logs, arquivos e aprovação humana nas ações sensíveis.
7. Usuário revê alterações antes de aplicar/commitar/publicar conforme políticas, podendo parar/revogar qualquer agente.

## Casos de uso prioritários

| Situação real | Equipe de agentes | Resultado verificável |
|---|---|---|
| Corrigir código num repositório local | supervisor → coder → tester → reviewer | branch, diff e testes executados |
| Evoluir código hospedado no GitHub/GitLab/Bitbucket | planner → coder → reviewer | commits/PR sob política e autorização |
| Atualizar site em servidor remoto | analyst → coder → deployer | pacote testado e deploy **após aprovação** |
| Organizar arquivos do usuário | cataloger → classifier → executor | plano de movimentação, prévia e aplicação autorizada |
| Preencher relatórios num aplicativo desktop | operator → validator | resultado com relatório e captura de erros, quando GUI automável |
| Pesquisar via ferramentas externas | researcher → synthesizer | fontes e conclusões auditáveis |
| Trabalhos recorrentes | scheduler → supervisor → workers | histórico de execuções, alertas e custos |

## Três dimensões independentes de configuração

- **Provedor:** `deepseek_only`, `grok_only`, `hybrid`; escolha por funcionário e por tarefa.
- **Função e hierarquia:** supervisor/gerente, planejador, especialista, executor, revisor, auditor; fluxos DAG e delegação.
- **Permissões e recursos:** somente leitura, alteração em workspace, testes/shell restrito, GUI automation, acesso Git/SSH, instalação de extensões e eventual operação elevada autorizada.

**Importante:** o modelo **não** herda a autoridade do usuário automaticamente. Um agente recebe apenas as permissões aprovadas para sua função, local de trabalho e operação. Delegação não amplia autoridade.

## Critérios de sucesso do projeto

- Usuário cria dois ou mais agentes com modelos diferentes sem tocar em código.
- Supervisor delega tarefa, recebe artefatos, mostra progresso e valida resultados.
- Agente trabalha em **pasta/repo autorizados** sem ler outras pastas ou extrair segredos.
- Execução Git gera alterações revisáveis em branch/PR; não publica nem força push sem permissão.
- Ação em aplicativo usa ferramentas auditáveis, sem controle arbitrário fora do escopo aprovado.
- Loja de integrações permite pesquisar e instalar extensões de fontes verificadas, sem executar código malicioso automaticamente.
- Ação privilegiada, sensível, destrutiva ou que exfiltra dados exige política e confirmação.
- Executáveis Windows/Linux e edição Server compartilham a mesma lógica de domínio.

**Caminho de entrega:** [Roadmap funcional](../05-integracoes/05-caminho-de-implementacao.md) · [Arquitetura geral](../02-arquiteturas/README.md) · [Mapa Mestre](../README.md).

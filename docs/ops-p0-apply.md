# OPS-P0 — rulesets de verdade (somente admin pode ativar)

Status: **PREPARAÇÃO versionada**, não afirma que regras GitHub já estão ativas.

Este repositório inclui CI real para o gate `promotion-gate`, cuja validação exige feature PR → `dev`, `dev` → `hml` e `hml` → `main`. **Sem ruleset ativo, checks podem ser ignorados:** publicar YAML não protege o GitHub por si só.

O script `scripts/governance/rulesets.py` usa a API GitHub oficial para preparar e aplicar rulesets. Somente um administrador, com token escopado para **Administration: write** e **Issues: write** (labels), pode executar:

```bash
python scripts/governance/rulesets.py --plan
# Definir GH_ADMIN_TOKEN pelo gerenciador seguro de segredos do seu ambiente.
python scripts/governance/rulesets.py --apply
python scripts/governance/rulesets.py --verify
```

O `--apply` cria/atualiza rulesets `dev`, `hml`, `main` e cria as 14 etiquetas P0–P9, docs, security, bug e feature. **Não adicionar o token a commits ou arquivos .env versionados.**

*Antes de executar*, confirmar se os oito checks listados no script existem em PRs nas branches-alvo. Em `main`, a aprovação por outra identidade autorizada no GitHub será necessária para cumprir um required review (aprovação em chat não é review do GitHub).

**Verificação operacional obrigatória não automatizada nesta execução:** tentar push direto controlado e confirmar rejeição HTTP/Git; ler rulesets via API e confirmar `enforcement: active`; verificar comentários de checks em PR. Até essas verificações, manter OPS-P0 como pendente no Trello.

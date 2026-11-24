---
name: automatic-notes
description: Gerenciar anotações de todo o estudo, extraindo conhecimento verificado sem trabalho manual do aluno
---

# Memória e notas automáticas

**Quando usar:** depois de cada resposta significativa e ao final de cada sessão.

- Registro factual: respostas do aluno (ou descrição fiel), erros verificados, correções e contextos de uso.
- Cada nova expressão → `python -m tutor.cli note add --type expression --title ... --meaning ... --example ... --evidence ... --tags ...`.
- Conceito gramatical → `--type grammar`; observação fonética → `--type pronunciation` (não confundir com medição de áudio); lacuna persistente → `--type difficulty`.
- O CLI cria ou atualiza Markdown em `workspaces/data/notes/`, adiciona vínculo à música e mantém `index.json`.
- Toda questão do dia recebe `song checkpoint`; as notas são uma síntese reutilizável, não substituem registros de tentativa.
- Ao concluir uma sessão, inspecione anotações para coerência, atualize resumo e informe ao aluno **o que foi guardado** em duas frases, sem exigir cópia manual.
- Não grave a letra integral no repositório; preserve somente referências e material original do aluno.
- Se Graphify existir, execute `graph sync` com autorização/configuração adequada. Reindexação não deve apagar notas nem afirmar aprendizado não comprovado.

**Qualidade:** não armazene correções inventadas, nem atribua ao aluno uma frase que foi escrita pelo agente. Se um erro foi corrigido, preserve histórico e atualize estado com evidência.


No v2 note add retorna knowledge_id para expression/grammar. Vincule ao registrar tentativas. Classifique phrasal verb/idiom/collocation via knowledge introduce --note-id antes da primeira tentativa. Nota apenas introduz conhecimento.

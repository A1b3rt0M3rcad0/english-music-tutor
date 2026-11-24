# Learning Intelligence — v2

Quatro sistemas determinísticos e duas skills novas. O agente ensina e avalia; a CLI valida estrutura e deriva métricas. Não certifica CEFR nem verifica semanticamente respostas.

## Migração
Feche outros processos de escrita. Execute python -m tutor.cli migrate. Backup local em workspaces/.tutor/migration-v1-backup (config/data), ignorado pelo Git. Não infere horas ou domínio histórico; notas legadas entram como introduced. Revisões legadas encerradas são reabertas para verificar retenção. Para voltar ao v1, preserve dados v2 e restaure manualmente a cópia com código v1.

## CLI
Prefixo python -m tutor.cli. Use --help em cada subcomando. Exemplos sintéticos, nunca registre como progresso real.

| Comando | Operação |
| --- | --- |
| knowledge introduce --type phrasal_verb --content "figure out" --meaning "descobrir" --sense "solve" | Unidade |
| knowledge list / summary / gaps / show --id ID | Consultas |
| knowledge record --id ID --attempt-id A1 --mode transfer --outcome correct --assistance independent --context trabalho --question "..." --answer "..." --feedback "..." | Evidência |
| cefr begin / current / history / due | Avaliação e consultas |
| cefr record --id ID --item-id Q1 --skill reading --difficulty B1 --question "..." --answer "..." --score 0.8 --feedback "..." | Item |
| cefr finish --id ID --grammar not_assessed --vocabulary not_assessed --reading B1 --listening not_assessed --writing not_assessed --speaking not_assessed --summary "..." | Estimativa |
| study begin --planned-minutes 120 | Abrir/retomar |
| study record --id ID --activity-id A1 --type review --minutes 20 | Atividade |
| study finish --id ID --effective-minutes 105 | Duração confirmada |
| study finish --id ID --unknown | Duração desconhecida |
| study history / summary | Histórico |
| analytics summary / weekly / monthly / trends / difficulties | Métricas |
| song difficulty --level B1 --evidence "..." | Faixa textual provisória |
| roadmap create --reason "Lacuna demonstrada" | Versão adaptativa |
| review grade --note-id ID --attempt-id R1 --result correct --assistance independent --context trabalho --question "..." --answer "..." --evidence "..." | Revisão |

## Regras
- Domínio: dois contextos independentes de transferência/revisão; três revisões em dias distintos após aquisição, >=14 dias desde introdução para consolidação. Erro independente pode regredir. Limiar configurável, heurístico.
- CEFR: cinco músicas ou 30 horas confirmadas; mínimo dez itens, três por dimensão declarada e dois acertos no nível ou superior. Estimativas por dimensão e data; nível global não inferido. Grammar/vocabulary são dimensões auxiliares.
- Tempo: confirmação explícita, não relógio do chat. Aderência usa sessões confirmadas com planejamento, não calendário completo. Horas não registradas são desconhecidas.
- Analytics: taxas 0–1 com amostra; compreensão 0–100 é média de estimativas por música. Domínio e CEFR em relatório de período são snapshots atuais. Desempenho por dimensão/dificuldade depende de checkpoints categorizados.
- Revisões: janelas iniciais ancoradas ao fim da música; manutenção de 60/90/120/180 dias sucessivos, teto 180 repetido. Erros/pistas reduzem intervalo.
- Roadmap: snapshot de lacunas, tempo, transferência, retenção e níveis, com versões; agente adapta fases, não promove nível automaticamente. Capacidade nominal não é garantia.
- Um processo de escrita por vez. Arquivos individuais atômicos, sem transação ACID entre arquivos. IDs estáveis permitem retentativas.
- Teste com python -m pytest -q e python -m compileall -q tutor bootstrap.py; testes sintéticos não demonstram eficácia pedagógica.

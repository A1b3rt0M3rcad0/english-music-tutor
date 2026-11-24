---
name: learning-roadmap
description: Gerar e recalcular roadmap personalizado a partir de diagnóstico e disponibilidade
---

# Roadmap até o objetivo

**Quando usar:** diagnóstico concluído, objetivo/horário mudou, checkpoint revela nova lacuna.

## Processo
1. Leia `workspaces/config.yaml`, `workspaces/data/assessments/placement/report.yaml`, resultados posteriores e métricas históricas.
2. Calcule horas e capacidade nominal de músicas: `floor((dias do horizonte × dias/semana ÷ 7) ÷ dias efetivos por música)`. Se programa contínuo, use uma **janela rolante** de planejamento, não meta final. A CLI faz essa conta em `roadmap create`.
3. Execute `python -m tutor.cli roadmap create` na raiz do projeto. A CLI grava `workspaces/data/roadmap.yaml`; personalize as fases com lacunas **identificadas**, não inventadas. Mantenha metas mensuráveis.
4. Planeje progressão factual/conceitual → compreensão → produção → transferência e autonomia. Para objetivos profissionais, favoreça músicas com contexto útil e conversação fora das letras.
5. Em cada etapa estabeleça: foco, repertório-alvo, evidências de conclusão, indicadores de listening/speaking/reading/writing e checkpoints independentes de letras.
6. Apresente número nominal de músicas e ressalte que não é garantia de chegar a B2/C1. Se prazo parecer insuficiente, proponha um objetivo intermediário plausível.
7. Replaneje após avaliações periódicas ou alterações da rotina. Preserve história do roadmap antes de substituir etapas.

## Restrições
- Três dias de estudo por música é o padrão, não três dias corridos. Não avance só porque o calendário passou.
- O objetivo pode ser livre (não apenas CEFR), e o programa pode durar a vida toda.
- Jamais force uma meta B1→B2 ou 90 dias para todos.


No v2 roadmap create --reason ... inclui snapshot de níveis, lacunas e ritmo. Consulte analytics summary, cefr current e knowledge gaps; não extrapole CEFR linearmente.

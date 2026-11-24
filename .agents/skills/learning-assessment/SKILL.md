---
name: learning-assessment
description: Avaliar cada exercício e fechar cada ciclo com rubrica e relatórios fundamentados
---

# Avaliação formativa e fechamento

**Quando usar:** depois de cada resposta, no final de cada sessão ou música, e em checkpoints de progresso.

## Rubrica
- Evidência: cite *o que o aluno efetivamente respondeu ou executou*.
- Compreensão: testar a interpretação sem tradução, estimar percentual usando itens avaliados.
- Vocabulário ativo: contar expressões utilizadas corretamente em **contextos inéditos**.
- Produção: separar correção, variedade, coerência, independência e capacidade de responder a follow-ups.
- Pronúncia: `verified`, `needs_work`, `not_assessed`; só usar os dois primeiros com evidência acústica avaliada.
- Memória: testar recall sem consultar notas e monitorar erros recorrentes.

Ao fechar Dia 3, certifique-se de que `song end-day --day 3` já ocorreu e gere `song finish --comprehension 0..100 --expressions 0..8 --pronunciation ... --speaking ... --summary ...` com evidência. Exemplo de speaking quando não houver áudio: `not_assessed`.

Critérios indicativos: ≥80% compreensão; ≥5 expressões ativas; pronúncia compreensível verificada; exposição oral 2–3min quando há áudio. Esses critérios são **independentes** da finalização administrativa dos 3 dias.

Não declare nível CEFR por uma única letra. Checkpoints independentes devem usar conteúdo desconhecido.

Se falhar, registre lacunas e programa reforço sem bloquear indefinidamente a próxima música.


No v2 use --skill/--difficulty e --error-tag quando fundamentados; song finish deriva expressões de evidência individual. Reavaliação via $cefr-progression.

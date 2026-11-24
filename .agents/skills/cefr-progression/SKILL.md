---
name: cefr-progression
description: Reavaliar proficiência por dimensão com evidências inéditas e histórico.
---
# Reavaliação
Consulte cefr due; padrão cinco músicas ou 1800 minutos confirmados, ou evidência de mudança. Não sobrescreva placement.
1. cefr begin retorna ID; retome após interrupção.
2. Perguntas inéditas uma a uma, dificuldade A1–C2, interpretação e produção, não memorização.
3. cefr record --id ... --item-id ... --skill ... --difficulty ... --question ... --answer ... --score ... --feedback ... --evidence-mode text .
4. Mínimo dez itens, três por dimensão declarada e dois acertos >= 0.75 no nível ou superior. Salvaguardas heurísticas, não calibração psicométrica.
5. cefr finish --id ... --grammar ... --vocabulary ... --reading ... --listening not_assessed --writing ... --speaking not_assessed --summary ... . Todas as dimensões; sem evidência adequada not_assessed. Não solicite áudio ou transcrição.
6. Níveis por dimensão e data; grammar/vocabulary auxiliares, não média global ou certificação.
7. Consulte analytics summary, replaneje com justificativa e registre tempo confirmado.

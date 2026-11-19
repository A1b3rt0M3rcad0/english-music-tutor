---
name: placement-assessment
description: Aplicar nivelamento inicial adaptativo de inglês com evidências por competência
---

# Diagnóstico inicial por evidências

**Quando usar:** onboarding pronto, diagnóstico pendente; ou aluno pede reavaliação formal.

## Procedimento
1. Explique duração estimada (ideal 60–90 minutos; divida em sessões se necessário) e áreas: grammar, vocabulary, reading, listening, writing, speaking.
2. Comece com dificuldade A2/B1 se não houver histórico; ajuste uma faixa CEFR por vez, usando acertos e segurança das respostas. Evite efeito teto/piso.
3. Não revele respostas antes da tentativa. Utilize múltipla escolha, completar lacuna, tradução bidirecional, leitura curta, resumo, perguntas abertas e diálogos. **O nível não se mede só por questões de marcar.**
4. Para listening, forneça material realmente ouvido, com fonte/trecho e perguntas de compreensão sem texto. Se não há áudio, marque `not_assessed`.
5. Para speaking, solicite áudio e avalie se ferramenta permite acesso real. Caso só haja texto, registre evidências de produção interativa, mas informe que pronúncia, prosódia e fluência acústica estão **não verificadas**.
6. Registre **cada questão** e resposta efetiva com `python -m tutor.cli diagnostic record --skill ... --difficulty ... --question ... --answer ... --score ... --feedback ... --evidence-mode ...`.
7. Exija ao menos 10 itens registrados, distribua por competências e aplique questões de confirmação para pontos ambíguos. Não preencha dados fictícios para atingir esse mínimo.
8. Em `diagnostic finish`, atribua `A1..C2` ou `not_assessed` para todas as seis áreas, com resumo fundamentado e limitações. O CLI valida presença de evidência por área avaliada.
9. Explique que o resultado é uma estimativa pedagógica, não exame CEFR oficial. Passe para `$learning-roadmap`.

## Interpretação
- Acerto simples não prova nível. Observe complexidade, independência, consistência, autocorreção e transferência.
- Se há evidências insuficientes, nunca invente precisão; proponha teste complementar.
- Materiais inéditos são essenciais para evitar diagnosticar memória de músicas conhecidas.

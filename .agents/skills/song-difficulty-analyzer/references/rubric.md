# Rubrica heurística de dificuldade (0 a 15)

**Não é um teste CEFR validado.** Serve para ajustar tarefas de uma música **em relação ao aluno específico**. Use apenas se houver letra/trechos suficientes. Escuta e pronúncia não entram na soma.

| Dimensão | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Vocabulário | Itens cotidianos, maior parte familiar | Alguns itens novos com contexto claro | Muitos termos novos/menos frequentes | Alto volume de itens raros/especializados ou usos não convencionais |
| Gramática | Frases simples, construções familiares | Algumas subordinadas/tempos menos frequentes | Estruturas variadas, elipses frequentes | Elipses complexas, inversões, estruturas que exigem inferência avançada |
| Idiomas/metáforas | Predominantemente literal | Poucas expressões idiomáticas claras | Várias expressões figuradas | Altíssima dependência de metáforas/ambiguidade |
| Densidade textual | Poucas informações por verso; muitas repetições | Ritmo textual moderado, repetições úteis | Informação densa por linha | Sequências densas com muitas ideias, referências e mudança de assunto |
| Lacunas pessoais | Conteúdos comprovadamente dominados | 1–2 lacunas pequenas | Diversas lacunas no histórico | Muitos conceitos ainda não estudados ou reiteradamente difíceis |

**Quando não há diagnóstico/notas suficientes**, a quinta dimensão é `unknown` e o total permanece parcial, sem extrapolar o que falta.

Somatório **somente se todas as cinco dimensões forem mensuráveis**:
- `0–4`: aparentemente confortável;
- `5–9`: desafio linguístico moderado;
- `10–15`: desafio linguístico alto.

Essas faixas são orientadoras, não limiares empiricamente calibrados. Não convertê-las para A1–C2.

**Ajuste ao aluno pela compreensão independente** (amostra real de perguntas sobre a música):
- Aproximadamente 50%–80% dos itens relevantes compreendidos sem tradução: desafio produtivo sugerido.
- Abaixo de 50%: oferecer maior apoio ou indicar alternativa; se aluno insistir, respeitar escolha.
- Acima de 80%: utilizar a música para prática de velocidade, variação contextual, pragmática e transferência.

Denominadores pequenos, perguntas fáceis demais e leitura prévia podem distorcer o resultado. Mencione a limitação e não atribua precisão artificial a percentuais.

## Modelo mínimo de relatório

```markdown
# Análise da música

- song_id: ...
- data: ...
- fonte da letra: fornecida pelo aluno (sem cópia integral)
- extensão da amostra: ...
- estado: provisional | calibrated | insufficient_data
- confiança: baixa | moderada | alta
- dimensões: vocabulary=..., grammar=..., idioms=..., density=..., learner_gap=...
- total heurístico: .../15 | não calculado
- adequação pessoal: comfortable | productive_challenge | overwhelming | undecided
- evidência: respostas verificadas, registradas fielmente
- áudio/velocidade/pronúncia: not_assessed
- ajustes para os 3 dias: ...
```

Não preencher respostas, notas ou percentual antes de obter evidência. Não armazenar letras completas no Git.

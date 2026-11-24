---
name: song-difficulty-analyzer
description: Analisar a dificuldade linguística de uma música informada pelo aluno e decidir como adaptar as atividades ao seu perfil e roadmap, sem usar áudio ou serviços externos.
---

# Análise de dificuldade da música — apenas texto

## Quando acionar

- **Antes de iniciar a música**, quando o aluno fornece título/artista e letra ou trechos suficientes.
- **No início do Dia 1**, depois da primeira tentativa de interpretação do aluno, para atualizar uma estimativa preliminar.
- **Depois dos testes dos Dias 1–3**, caso as dificuldades reais contrariem a classificação inicial.
- Quando o aluno pedir ajuda para escolher uma música compatível com o momento atual.

Esta skill apoia `$music-study-coach`, `$learning-roadmap`, `$placement-assessment`, `$lyrics-comprehension`, `$adaptive-learning` e `$automatic-notes`. Ela **não** determina sozinha o nível CEFR do aluno e **não** substitui o diagnóstico inicial.

## Entradas e limites

Ler `workspaces/config.yaml`, `workspaces/data/roadmap.yaml` quando disponível, diagnóstico (se houver) e notas sobre conteúdos conhecidos/pendentes. Utilize **somente letra ou trechos realmente fornecidos pelo aluno ou acessados por uma ferramenta disponível e autorizada**. Se houver só o nome da música, classifique como **dados insuficientes**: solicite a letra ou um trecho, ou continue com uma hipótese explicitamente provisória, sem inventar características.

**Não exigir** gravação, microfone, transcrição, análise acústica, serviços de streaming, scraping ou integração externa. O aluno escuta a música por conta própria. Sem evidência acústica, velocidade, articulação, sotaque e inteligibilidade da gravação permanecem **não avaliados**.

## Processo obrigatório

1. **Ler o perfil** e identificar objetivo atual (não presumir B1 nem duração de 90 dias), conceitos dominados, erros e prioridades.
2. **Inspecionar material disponível**: letra ou trechos fornecidos. Não alucinar texto de música; não salvar letra integral nem reproduzi-la no relatório.
3. **Avaliar cinco dimensões de 0–3**, usando os critérios em [references/rubric.md](references/rubric.md): vocabulário, construções gramaticais, expressões idiomáticas/ambiguidade, densidade textual e distância entre conteúdos da letra e conhecimento comprovado do aluno.
4. **Registrar fonte e incerteza**: se a amostra for curta ou o diagnóstico for incompleto, classificar como `provisional`; se não houver letra, `insufficient_data` e **não atribuir soma**.
5. **Estimar adequação ao aluno**, não uma dificuldade universal. Recomende `comfortable`, `productive_challenge` ou `overwhelming` conforme o desempenho observado e a compreensão inicial da letra. Uma pontuação de texto não equivale a certificação CEFR.
6. **Aplicar calibração**: peça ao aluno ouvir por conta própria e descrever em inglês o tema ou interpretar alguns trechos sem tradução. Se houver evidência suficiente, atualize dificuldade e confiança. Não conte autoavaliação como medida acústica objetiva.
7. **Adaptar o ciclo sem quebrar os três dias**: selecionar 5–8 chunks úteis, ajustar tipo/nível de pergunta, oferecer suporte contextual antes dos trechos difíceis e preservar prática de transferência no Dia 3.
8. **Respeitar a escolha**: nunca recusar automaticamente música difícil; explique a adequação, ofereça alternativa ou plano de simplificação e deixe o aluno decidir.
9. **Salvar evidências** depois de criar a música: relatório enxuto em `workspaces/data/songs/<id>/song-difficulty.md`. Se houver atividade de diagnóstico no Dia 1, registre `song checkpoint` após `begin-day` com evidência real do aluno; lacunas recorrentes podem virar `note add --type difficulty`.
10. **Revisar conclusão** no fim do Dia 3: compare previsão com erros efetivos e use `$learning-roadmap` somente quando o histórico justificar replanejamento.

## Saída padrão ao aluno

Exemplo de **formato**, não pontuação real:

> Dificuldade linguística: desafio produtivo (estimativa provisória). Os verbos são familiares, mas há metáforas e 3 expressões idiomáticas novas para você. Vamos concentrar o Dia 1 nessas expressões. O listening não foi avaliado porque você ainda não realizou a escuta.

Na resposta, incluir no máximo: nível de adequação, dois fatores relevantes, confiança e ajuste de estudo. Não apresentar cinco tabelas nem um relatório completo antes de começar o exercício.

## Persistência e compatibilidade

- O motor do repositório não possui `song analyze`. **Não inventar esse comando**.
- Antes de `song start`, mantenha análise provisória em contexto de conversa, sem criar uma nova música persistida prematuramente.
- Depois de `song start`, grave `song-difficulty.md` no diretório `workspaces/data/songs/<id>/` em Markdown **curto, sem letra completa**. Sugestão de campos:
  - `song_id`, `analysis_date`, `sample_scope`, `source`, `status`, `confidence`, `dimensions`, `personal_fit`, `evidence`, `teaching_adjustments`, `unassessed_audio`.
- Se a atividade foi aplicada e o Dia 1 começou, um checkpoint compatível com a CLI é:

  ```bash
  python -m tutor.cli song checkpoint --day 1 --activity "song-difficulty" --evidence "Aluno interpretou 3/5 perguntas sem tradução; dificuldade em dois phrasal verbs" --feedback "Ajustar seleção de expressões; confiança moderada" --score 0.6
  ```

  Substitua o exemplo pela **resposta real**. A nota do checkpoint é sobre a resposta do aluno, **não** a dificuldade da música. Não execute exemplo com dados fictícios.
- Graphify é índice derivado das anotações em `workspaces/data/notes/`, não da classificação provisória por si só. Salve nota em `workspaces/data/notes/` somente quando surgir uma lacuna de conhecimento comprovada, via `$automatic-notes`.

## Regras de qualidade

- Não usar o número de palavras sozinho como medida de dificuldade.
- Não confundir repetição fácil de decorar com compreensão transferível.
- Não estimar pronúncia/velocidade sem áudio analisável; não depender de áudio para executar a skill.
- Se o texto não for suficiente, informe isso claramente e não fabrique uma faixa CEFR.
- Música conhecida ou muito repetida pode parecer fácil sem ser linguisticamente transferível: testar em contexto diferente via `$knowledge-transfer`.


No v2 consulte cefr current e knowledge gaps. Após song start, song difficulty --level ... --evidence ... só se houver faixa textual fundamentada; caso contrário preserve ausência de nível.

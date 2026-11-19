---
name: knowledge-transfer
description: Testar se o aluno consegue reutilizar inglês aprendido em situações inéditas, por chat textual, sem depender da letra ou de repetir exemplos memorizados.
---

# Transferência de conhecimento entre contextos

## Quando acionar

- **Dia 1**: após o aluno compreender uma expressão e criar seu primeiro exemplo, aplicar uma pequena transferência guiada.
- **Dia 2**: testar as mesmas construções em uma tarefa diferente da música, com menos pistas.
- **Dia 3**: aplicar testes **sem revelar antecipadamente as expressões-alvo** e enviar evidências a `$learning-assessment`.
- **Revisões D+1/D+3/D+7/D+14/D+30**: preferir recuperar em contexto novo, junto com `$spaced-repetition`.
- **Fora da música**: quando o aluno disser que sabe uma expressão, mas ainda não consegue utilizá-la espontaneamente.

Esta skill complementa `$lyrics-comprehension`, `$speaking-coach`, `$adaptive-learning`, `$learning-assessment` e `$automatic-notes`. Não substitui o plano de três dias nem cria um segundo chat para uma nova música.

## Princípio central

**Reconhecer a expressão na letra não é demonstrar transferência.** A evidência relevante é o aluno **produzir uma frase apropriada para uma situação diferente**, preferencialmente sem pistas lexicais. Faça uma pergunta por vez, aguarde a resposta, corrija e reteste de outro modo. Não forneça solução antes da tentativa.

## Procedimento obrigatório

1. Leia `workspaces/config.yaml`, `workspaces/data/roadmap.yaml` (se existir), `workspaces/data/notes/index.json` e registros da música em `workspaces/data/songs/<id>/cycle.json`. Localize 1–3 construções já ensinadas; **não invente que o aluno dominou algo**.
2. Selecione um cenário distante do tema original: trabalho, deslocamento, planejamento, atendimento, conflito, experiência pessoal ou hipótese. Ajuste ao objetivo e nível efetivamente demonstrados, sem fixar B1/B2.
3. Defina uma intenção comunicativa observável, como explicar uma decisão ou narrar uma experiência.
4. **Etapa guiada**: peça ao aluno para usar a construção-alvo em contexto novo. Conte como prática, **não como domínio espontâneo**.
5. **Etapa sem pistas (holdout)**: apresente outro cenário, omita o nome da expressão e peça resposta livre. Se o aluno usar a construção correta adequadamente sem ajuda, marque como evidência de uso independente.
6. Dê feedback separando `meaning`, `grammar`, `collocation` e `appropriateness` quando pertinente; não corrija escolhas válidas só porque diferem do exemplo esperado.
7. Em erro, explique brevemente, apresente um contraste e aplique **outra pergunta com novo contexto**, não a mesma frase com dicas sucessivas.
8. Registre imediatamente a **resposta real**, as pistas dadas e o feedback via `song checkpoint` se o dia já estiver em andamento. Use `$automatic-notes` para guardar frase do aluno e lacuna, não uma resposta atribuída indevidamente ao aluno.
9. Ao concluir, informe brevemente quais expressões demonstraram uso independente e quais permanecem em revisão. Programe reforço com as habilidades existentes; não altere automaticamente o nível CEFR.

## Rubrica curta (aplicar por tentativa)

- **1.0 — Independente**: produz expressão ou construção correta, semanticamente pertinente, **sem** indicação explícita da resposta-alvo e sem consultar notas.
- **0.5 — Com ajuda**: uso correto depois de nomear a expressão, fornecer modelo, traduzir partes ou corrigir a primeira tentativa.
- **0.0 — Não demonstrado**: resposta incorreta, omissão da construção exigida ou resposta sem evidência suficiente.
- **`not_assessed`**: tarefa não executada; **não** passe `score` numérico nem conte como acerto.

Se a resposta livre atingir o objetivo por outra construção correta, **não penalize a comunicação**: registre êxito comunicativo e indique que a transferência da expressão específica não foi observada. Distinguir avaliação de comunicação vs domínio de um chunk.

Consulte [references/test-design.md](references/test-design.md) para formatos e critérios de independência.

## Persistência: compatível com o motor existente

A integração é por instruções e pelos comandos que **já existem**; não requer modificações em `tutor/`.

1. Somente após `song begin-day --day N`, use uma linha equivalente a:

   ```bash
   python -m tutor.cli song checkpoint --day 3 --activity "knowledge-transfer" --evidence "Resposta literal do aluno: ...; sem dica lexical; cenário de trabalho" --feedback "Utilizou ... adequadamente em situação inédita" --score 1
   ```

   Substitua o exemplo pelos dados **verdadeiros** e o dia atual. Não execute o exemplo literalmente.

2. Para uma lacuna realmente observada, use `note add --type difficulty` com título representativo e `--example` contendo a resposta produzida pelo aluno. Para expressão demonstrada, use `note add --type expression` se for informação útil e ainda não registrada.
3. A pontuação de transferência entra na avaliação final somente se houver tentativas **sem pistas**; aproveite `learning-assessment` para contar expressões demonstradas independentemente.
4. Opcional: gere um resumo curto em `workspaces/data/songs/<id>/transfer-assessment.md` se o workspace exigir relatório legível. Nunca salve letra integral da música.
5. Graphify indexa notas canônicas de `workspaces/data/notes/`; somente chame `graph sync` se já estiver configurado e o usuário tiver consentido com o backend.

## Limites de escopo

- **Somente chat textual**: não solicite gravações, microfone, transcrição, upload de áudio, serviços externos ou aplicativos adicionais.
- O aluno pode ouvir/cantar a música no serviço que já utiliza; essas ações não comprovam qualidade acústica da pronúncia.
- Preserve o orçamento da sessão e a regra **uma atividade por turno**.
- Não use conteúdo de outra música como ciclo novo dentro do chat atual. Uma expressão antiga pode aparecer em revisão.
- Não reproduza a letra completa nem grave trechos extensos protegidos por direitos autorais.

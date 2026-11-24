---
name: spaced-repetition
description: Gerir revisões D+1, D+3, D+7, D+14, D+30 a partir do fechamento de cada música
---

# Revisão espaçada de expressões

**Quando usar:** início de cada sessão e após conclusão de música.

1. Execute `python -m tutor.cli review due`; dedique orçamento inicial de revisão (20 min quando sessão diária totaliza 120 min).
2. Solicite recuperação sem consultar notas: significado, frase inédita, complemento ou mini diálogo com a expressão.
3. Avalie **cada expressão** como correta/incorreta, grave a resposta real e o resultado com `review grade --note-id ... --result ... --evidence ...`.
4. Correta: próxima janela D+3, D+7, D+14, D+30 a partir do encerramento da música; erro: repetir no dia seguinte, sem perder histórico.
5. Se várias revisões estão vencidas, priorize as mais atrasadas e as que apresentam falhas; não faça o aluno cantar todas as músicas de novo.
6. Em dias sem sessão, as revisões ficam pendentes e são atendidas no próximo dia de estudo.
7. Se não houve novas expressões registradas, não fabrique cartões/revisões.

**Atenção:** o motor cria a fila apenas depois do `song finish` da música. O início dos dias 2 e 3 inclui recuperação das expressões da própria música no bloco de revisão, conduzida pelo agente, mesmo quando a fila futura ainda não foi criada.


No v2 use review grade --note-id ... --attempt-id ... --result correct|incorrect --assistance independent|assisted --context ... --question ... --answer ... --evidence ... . Só acerto independente avança; erro/ajuda reduz intervalo. Manutenção configurável 60/90/120/180 dias entre sucessos; sem consolidação após janelas iniciais, reforço em sete dias. Unidade fora de música é agendada imediatamente.

# Comandos operacionais para Codex e usuários avançados

Execute na **raiz do repositório**, com a venv ativada. A CLI usa `workspaces/` automaticamente.

```bash
python -m tutor.cli doctor
python -m tutor.cli status
python -m tutor.cli onboard  # fallback de terminal; o Codex prefere conduzir perguntas no chat
```

## Diagnóstico

O agente deve aplicar o teste e registrar cada tentativa REAL; não grave exemplos fictícios como desempenho real.

```bash
python -m tutor.cli diagnostic record --skill vocabulary --difficulty A2 \
  --question "Write a sentence with 'used to'" --answer "I used to play tennis" \
  --score 1 --feedback "Uso correto em contexto" --evidence-mode text
```

`diagnostic finish` exige no mínimo dez itens com evidência. Informe todos os níveis, usando `not_assessed` onde não houve teste.

```bash
python -m tutor.cli diagnostic finish \
  --grammar B1 --vocabulary B1 --reading B1 --listening not_assessed \
  --writing B1 --speaking not_assessed \
  --summary "Evidências disponíveis sustentam B1 em escrita e leitura; áudio não avaliado"
python -m tutor.cli roadmap create
python -m tutor.cli roadmap show
```

No PowerShell, escreva os comandos em linha única ou use o escape de linha `` ` `` (não a barra invertida `\`).

## Música e três dias

```bash
python -m tutor.cli song start --title "Example Song" --artist "Example Artist" --source "link ou referência fornecida"
python -m tutor.cli song begin-day --day 1
python -m tutor.cli song checkpoint --day 1 --activity "listening" \
  --evidence "aluno descreveu o tema e confundiu passado/presente" \
  --feedback "rever verbos no passado" --score 0.6
python -m tutor.cli note add --type expression --title "figure out" \
  --meaning "entender/descobrir" --example "I need to figure it out." \
  --evidence "Aluno produziu frase correta após correção" --tags "phrasal-verb,compreensao"
python -m tutor.cli song end-day --day 1 --summary "Aluno adquiriu quatro expressões; precisa revisar passado"
```

Dia 2 e 3 seguem o mesmo formato com `begin-day`/`checkpoint`/`end-day`.

```bash
python -m tutor.cli song finish --comprehension 85 --expressions 5 \
  --pronunciation not_assessed --speaking not_assessed \
  --summary "Domínio textual satisfatório; pronúncia não testada acusticamente"
python -m tutor.cli review due
python -m tutor.cli review grade --note-id expressions/figure-out --result correct \
  --evidence "Respondeu corretamente sem olhar a frase"
```

**Nunca** use os exemplos para registrar performance de alguém que não executou os exercícios. A CLI não observa a voz nem valida semanticamente as respostas; o agente deve reportar sua avaliação com as evidências.

## Graphify

```bash
graphify --help
# Instale o Graphify como skill no projeto; leia INSTALL.md.
python -m tutor.cli graph sync
# Consulte as opções de query da versão instalada:
graphify query --help
```

A sincronização executa Graphify sobre `workspaces/data/notes/` com o backend já configurado. Ela é opcional, pode fazer chamadas remotas e não será invocada silenciosamente por hooks.

## Arquivos gerados

- `workspaces/config.yaml`: preferências, fonte de verdade.
- `workspaces/data/state.json`: progresso do fluxo (não editar manualmente, salvo recuperação consciente).
- `workspaces/data/assessments/placement/items.json`: tentativas e respostas reais.
- `workspaces/data/assessments/placement/report.yaml`: estimativa por competência com limitações.
- `workspaces/data/roadmap.yaml`: plano nominal (editável pelo Codex, sem remover histórico).
- `workspaces/data/songs/<id>/cycle.json`: dias, evidências, status e vínculo com chat.
- `workspaces/data/notes/**/*.md`: conhecimento permanente; `workspaces/data/notes/index.json`: índice.
- `workspaces/data/reviews.json`: revisões vencidas e histórico de tentativas.
- `workspaces/data/events.jsonl`: registro cronológico técnico.
- `workspaces/data/threads.json`: vínculo entre músicas e chats.
- `workspaces/.tutor/session.json`: identificador efêmero do chat corrente (ignorado pelo Git).

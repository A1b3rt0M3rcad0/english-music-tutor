# Arquitetura

## Um projeto, um progresso local

O código, a CLI, as skills, as instruções do Codex e os hooks ficam na raiz deste repositório. `python bootstrap.py workspace` inicializa `workspaces/` no mesmo projeto. Essa pasta guarda apenas a configuração, os dados do aluno e arquivos locais. O código não é copiado nem duplicado.

`workspaces/` é ignorada pelo Git na raiz para que dados pessoais não sejam enviados ao repositório público. Um `.gitignore` dentro dela também exclui credenciais, áudio, letras integrais e saídas temporárias. Consulte o README para optar por um repositório particular.

## Persistência

A CLI é executada na raiz do repositório. `tutor.store.root()` usa `TUTOR_WORKSPACE` quando definido, aceita uma configuração no diretório atual para compatibilidade e, no uso normal, encontra `workspaces/config.yaml` automaticamente.

- Configuração: `workspaces/config.yaml`, schema v1 com PyYAML.
- Controle de jornada: `workspaces/data/state.json` com onboarding, diagnóstico, roadmap, música ativa e contagem.
- Evidências de nivelamento: `workspaces/data/assessments/placement/items.json` e `report.yaml`.
- Roadmap: `workspaces/data/roadmap.yaml`, estimativas e fases.
- Música ativa: `workspaces/data/songs/<n>-<slug>/cycle.json`; `day-N.md` resume cada dia; `assessment.yaml` registra o resultado.
- Conhecimento: arquivos Markdown em `workspaces/data/notes/` e índice `index.json`.
- Revisões: `workspaces/data/reviews.json`, nos intervalos D+1, D+3, D+7, D+14 e D+30 após concluir uma música.
- Auditoria: `workspaces/data/events.jsonl`, com eventos explícitos da CLI.
- Sessão Codex: `workspaces/.tutor/session.json`, vinculada ao chat quando o hook está habilitado; `workspaces/data/threads.json` impede usar o mesmo chat para músicas diferentes.
- Grafo: `workspaces/graphify-out/`, índice derivado e opcional.

## Orquestração e limites

`AGENTS.md` define as regras do tutor, e cada skill descreve um procedimento. `tutor/cli.py` e `tutor/engine.py` validam e persistem entradas, mas não avaliam inglês por conta própria. O Codex precisa se basear nas respostas reais do aluno. Os hooks carregam contexto e registram o encerramento consultivo.

Listening exige áudio realmente ouvido. Speaking e pronúncia acústica exigem evidência de áudio. Sem player ou transcritor integrado, o aluno usa os recursos de áudio que já possui. A agenda é um orçamento de estudo, não um cronômetro. O roadmap calcula capacidade estimada, não resultados garantidos.

O Graphify é opcional e indexa as notas locais. As notas Markdown e o índice JSON continuam sendo a fonte de verdade. A sincronização pode usar um serviço remoto e não é iniciada automaticamente.

## Evolução

1. Mantenha o schema 1 ou forneça migrações explícitas para mudanças de formato.
2. Prefira operações idempotentes e checkpoints frequentes.
3. Atualize skills e testes juntos quando mudar o comportamento do tutor.
4. Confirme afirmações do grafo nos arquivos Markdown ou JSON de origem.
5. Não dependa de transcrições internas do Codex nos hooks.
6. O motor é local e single-user, sem servidor ou controle de acesso multiusuário.

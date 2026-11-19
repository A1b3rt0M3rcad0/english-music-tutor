# Arquitetura, contratos e decisões

## Separação de ambientes

**Template (público):** documentação, AGENTS, skills, engine, bootstrap, CI, testes e config.example.yaml. Não há `config.yaml`, `data/state.json` ou dados de aluno.

**Workspace (pessoal):** cópia independente das capacidades necessárias ao estudo, sem caminho absoluto do template. Ao criar, `data/` contém somente subpastas e `.gitkeep`. `config.yaml` contém valores iniciais `null` até o onboarding. Históricos pertencem a este workspace e nunca são sincronizados automaticamente com o template.

**Restrição de portabilidade:** cópia inicial do motor/skills não recebe patches automaticamente do template. Atualizações devem ser explicitamente migradas e testadas.

## Fluxo de persistência

- Configuração: `config.yaml`, schema v1 com PyYAML.
- Controle de jornada: `data/state.json` com onboarding/diagnóstico/roadmap, música ativa e contagem.
- Evidências de nivelamento: `data/assessments/placement/items.json` e `report.yaml`.
- Roadmap: `data/roadmap.yaml`, estimativas e fases.
- Música ativa: `data/songs/<n>-<slug>/cycle.json`; `day-N.md` apresenta resumo do dia; avaliação final `assessment.yaml`.
- Conhecimento: `data/notes/{expressions,grammar,pronunciation,difficulties}/*.md`; índice `data/notes/index.json`.
- Revisões: `data/reviews.json`, intervalos D+1, D+3, D+7, D+14, D+30 contados da conclusão da música.
- Auditoria: `data/events.jsonl` (apenas eventos explícitos da CLI).
- Sessão Codex: `.tutor/session.json` (não versionado), vinculado ao chat ao iniciar música quando hook é confiável; `data/threads.json` mantém o mapeamento para impedir duas músicas na mesma conversa.
- Grafo: `graphify-out/`, derivado; não é armazenamento canônico.

## Orquestração

`AGENTS.md` contém regras permanentes e roteamento de skills. Cada skill é procedimento, não um serviço em execução. `tutor/cli.py` e `tutor/engine.py` persistem e validam entradas; **não geram avaliação linguística sozinhos**. O Codex deve executar as instruções e fornecer evidências. Os hooks apenas injetam estado/resumo no início e fazem registro consultivo no encerramento. A escolha de metodologia (ex.: nova tradução ou interpretação) depende do agente, das respostas reais e do tempo disponível.

## Avaliação realista

- O motor valida existência de respostas/evidências, não certifica o grau CEFR.
- Listening precisa de áudio efetivamente ouvido. Speaking/pronúncia precisa de evidência acústica para conclusões fonéticas.
- Não foi integrado um conversor de voz, transcritor ou player de música; usa recursos que o aluno já possui.
- Sessões de calendário são orientadas por orçamento de estudo; sem temporizador externo não existe contagem automática de minutos reais.
- O roadmap calcula **capacidade nominal**, não resultados garantidos.

## Boas práticas de evolução do motor

1. Mantenha o schema 1 e migrações explícitas ao alterar formato persistente.
2. Priorize operações idempotentes e checkpoints frequentes.
3. Documente mudança de skill junto de caso de teste correspondente.
4. Não confunda índice Graphify com dado de domínio. Todas as relações importantes devem ser demonstráveis nos Markdown/JSON.
5. Nunca faça hook depender de leitura do transcript do Codex: formato não estável, e `SessionEnd` é tardio.
6. Proteja dados privados; a v1 é um CLI local single-user, não um servidor multiusuário nem um sistema de controle de acesso.

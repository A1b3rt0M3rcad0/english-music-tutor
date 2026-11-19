# Meu ambiente de estudo de inglês com músicas

Este repositório é o **workspace pessoal de aprendizagem**, gerado automaticamente a partir do projeto-template English Music Tutor. Ele contém ferramentas e, depois do uso, poderá conter seu histórico individual. Use um repositório **privado** se desejar armazenar desempenho e anotações.

## Primeiro uso

1. Abra esta pasta no terminal.
2. Instale Python 3.10+ e Codex CLI, conforme o `INSTALL.md`.
3. Execute `python -m pip install -e .` (preferencialmente em ambiente virtual).
4. Execute `python -m tutor.cli doctor`.
5. Abra `codex` **nesta pasta**, confie nos hooks revisados com `/hooks` e diga: `Quero começar minha jornada de inglês`.
6. Responda ao onboarding e ao nivelamento. O agente criará o roadmap automaticamente.

Cada música ocupa um **chat** distinto, com três dias de atividades no **mesmo chat**. Em um novo chat: `Quero iniciar a próxima música: [título, artista e letra ou referência]`.

Consulte `AGENTS.md` e `docs/COMMANDS.md` para as regras e comandos. O agente deve criar suas anotações automaticamente: você realiza os exercícios, não precisa organizar um caderno.

Se quiser gerar o grafo das notas, instale Graphify separadamente, seguindo `INSTALL.md`. O projeto funciona mesmo quando Graphify não está disponível.

**Importante:** recursos de voz dependem do cliente e de ferramentas disponíveis. Codex somente textual não mede pronúncia de forma acústica. Não comite letras completas de músicas protegidas.

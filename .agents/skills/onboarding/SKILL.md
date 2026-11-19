---
name: onboarding
description: Conduzir instalação pedagógica e mudanças de objetivo, prazo e rotina
---

# Onboarding adaptativo

**Quando usar:** aluno ainda não configurado ou deseja alterar objetivo/disponibilidade.

## Entrevista guiada (uma pergunta por vez)
1. Pergunte para que quer aprender inglês, como pretende usar a língua e qual meta de resultado pretende demonstrar (ex.: participar de reuniões, compreender podcasts, chegar a C1). Não reduza o objetivo automaticamente a CEFR.
2. Pergunte horizonte: número de dias ou jornada contínua para a vida. Para modo fixo, descubra dias exatos. Pergunte quantos dias por semana.
3. Pergunte **minutos por sessão**, **sessões por dia** e horários preferenciais (horário pode ser nota, não precisa configuração obrigatória). Calcule a carga total sem prometer fluência.
4. Pergunte se possui áudio, acesso a letras, microfone e conversação por voz. Diferencie `external` (faz fora do Codex), `audio_available` (há áudio realmente acessível) e `text_only`.
5. Pergunte qual foi a experiência anterior do aluno. Isso contextualiza, mas não substitui diagnóstico.
6. Resuma a configuração e peça validação **uma única vez** antes da persistência inicial.
7. Registre em `config.yaml` através de `engine.update_profile` (Python). Alternativa: `python -m tutor.cli onboard` no terminal, com usuário preenchendo.
8. Execute `python -m tutor.cli doctor` e prossiga para `$placement-assessment`.

**Campos YAML obrigatórios:** `student.learning_goal`, `schedule.mode`, `schedule.duration_days` (se fixo), `days_per_week`, `sessions_per_day`, `minutes_per_session`, `method.voice_mode`. O projeto começa sem valores pessoais.

**Alterações futuras:** preserve avaliações, notas e ciclos; altere somente preferências e rode novamente `roadmap create` com histórico preservado. Confirme com o aluno antes de mudanças com impacto no plano.

**Nunca:** declarar B2 como nível comprovado com base na autodeclaração, iniciar música antes do diagnóstico, ou fazer perguntas em formulário extenso.

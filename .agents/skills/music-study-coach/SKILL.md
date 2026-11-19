---
name: music-study-coach
description: Conduzir cada música em um chat exclusivo com três dias e sessões interativas
---

# Tutor principal de música

**Quando usar:** o aluno informa música ou deseja continuar Dia 2/Dia 3 do chat atual.

## Antes da primeira atividade
- Leia `workspaces/config.yaml`, estado e roadmap, rode `review due` e consulte sessões anteriores. Faça somente a revisão correspondente à sessão.
- Confirme nome/artista e se existe áudio e letra acessíveis. O aluno pode colar letra durante a conversa, mas não salve sua íntegra no repositório, especialmente letras protegidas.
- Novo chat + nova música: `song start --title ... --artist ... --source ...`; continuação: `song current`. A música é vinculada ao ID de chat por hook se disponível.
- Em cada dia: `song begin-day --day N` → atividades sequenciais → `song checkpoint` em cada resposta relevante → `song end-day --day N` com resumo fiel.

## Dia 1 — Entender
- 20min revisão (ou diagnóstico no primeiro dia de estudo); 10min escuta sem letra; 15min interpretação; 20min 5–8 chunks; 15min cantar lendo; 30min conversação; 10min notas automáticas.
## Dia 2 — Reproduzir
- 20min revisão; 15min ditado auditivo; 20min shadowing; 15min canto com/sem letra; 10min escuta; 30min conversação; 10min notas.
## Dia 3 — Dominar
- 20min revisão; 15min compreensão final; 15min canto de memória; 15min chunks inéditos; 15min fala externa natural; 30min diálogo/fala; 10min notas e avaliação. `song finish` só após os 3 dias encerrados.

## Pedagogia
- Uma instrução por turno. Faça o aluno tentar antes da solução. Dê correção objetiva e **retente com outra pergunta** se necessário.
- Adapte o número de sessões/dia e tempo por sessão configurado; conserve revisões, música, produção e consolidação. Controle o tempo como **orçamento** e pergunte se a atividade foi executada; não finja cronômetro.
- Para a primeira música, substitua revisão inicial por avaliação curta de base já realizada (ou familiarização inicial), não reinicie o nivelamento inteiro.
- Cada chat contém uma música principal. Músicas anteriores aparecem somente no bloco de revisão; não abra novo ciclo sem chat novo.
- O agente registra notas via `$automatic-notes` automaticamente.

**Critério de execução:** não conclua um dia sem checkpoints de evidência. Não marque estudo de áudio sem que aluno tenha realmente ouvido.

---
name: knowledge-mastery
description: Registrar evidência individual de conhecimento e acompanhar domínio.
---
# Domínio
Consulte knowledge list e reutilize IDs, distinguindo sentidos. Note add retorna knowledge_id; vincule com --note-id. Uma nota não comprova domínio. 
1. knowledge introduce --type ... --content ... --meaning ... --sense ...
2. Uma questão por turno: compreensão, aplicação assistida ou transferência independente em contexto distinto. Use knowledge-transfer.
3. knowledge record --id ... --attempt-id ... --mode comprehension|application|transfer --outcome correct|incorrect|not_observed|not_assessed --assistance independent|assisted|unknown --context ... --question ... --answer ... --feedback ... . IDs estáveis, resposta real, sem inventar evidência. Alternativa válida sem alvo é not_observed.
4. Revisões passam apenas por review grade. Consulte knowledge summary/gaps. Nunca edite estados diretamente.
5. Dois contextos independentes distintos para aquisição; três revisões em dias distintos após aquisição, com pelo menos 14 dias desde introdução, para consolidação. Erro independente pode regredir. Limiar heurístico configurável.
6. Não solicite áudio, gravação ou transcrição; não armazene letras integrais.

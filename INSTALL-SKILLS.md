# Skills adicionais

O projeto inclui duas skills pedagógicas novas em `.agents/skills/`. Elas são descobertas pelo Codex ao abrir uma sessão na raiz do repositório. Não exigem dependências, serviços ou hooks adicionais.

## Analisar a dificuldade da música

`$song-difficulty-analyzer` estima se a linguagem de uma música oferece um desafio adequado ao aluno. Use letra ou trechos fornecidos por ele. Sem amostra suficiente, informe que faltam dados e não invente características. A análise é textual, provisória e não define nível CEFR.

O relatório curto é salvo em `workspaces/data/songs/<id>/song-difficulty.md` depois que a música começa. A CLI atual não possui o comando `song analyze`.

## Praticar transferência

`$knowledge-transfer` verifica se o aluno consegue usar expressões aprendidas em situações diferentes da música. Comece com uma prática guiada e depois faça uma pergunta sem mencionar a expressão-alvo. Registre a resposta real com `song checkpoint`; não conte uma tentativa com dicas como uso independente.

As notas e evidências ficam na pasta local `workspaces/`. O código, as skills e as instruções continuam compartilhados na raiz do projeto.

## Verificar a instalação

Abra uma nova sessão do Codex na raiz do repositório para carregar as skills. Para testar seus arquivos e referências:

```bash
python -m unittest discover -s tests -p 'test_skill_extension.py' -v
```
